"""Apify Eventbrite scraper service for enhanced event and sponsor discovery.

This service uses the Apify platform to scrape Eventbrite events and extract
detailed information including sponsors, organizers, venues, and pricing.
"""

import os
from typing import List, Optional, Dict, Any
from datetime import datetime
import time

from ..models import Event, Sponsor
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class ApifyEventbriteScraperService:
    """Service to scrape Eventbrite using Apify actors."""

    def __init__(self, api_token: Optional[str] = None):
        """Initialize the Apify scraper service."""
        self.api_token = api_token or os.getenv('APIFY_API_TOKEN')
        self.client = None

        if self.api_token:
            try:
                from apify_client import ApifyClient
                self.client = ApifyClient(self.api_token)
                logger.info("✓ Apify client initialized")
            except ImportError:
                logger.warning("apify-client not installed. Run: pip install apify-client")
            except Exception as e:
                logger.warning(f"Failed to initialize Apify client: {str(e)}")

    def scrape_events(
        self,
        search_query: str,
        location: Optional[str] = None,
        max_results: int = 20,
        category: Optional[str] = None
    ) -> List[Event]:
        """
        Scrape Eventbrite events using Apify.

        Args:
            search_query: Search keywords
            location: Location to search (city, state, country)
            max_results: Maximum number of events to scrape
            category: Category filter

        Returns:
            List of Event objects with scraped data
        """
        if not self.client:
            logger.warning("Apify client not initialized")
            return []

        logger.info(f"Scraping Eventbrite via Apify: '{search_query}'")

        # Build Eventbrite search URL
        base_url = "https://www.eventbrite.com"

        if location:
            # Format: /d/{location}/all-events/
            location_slug = location.lower().replace(' ', '-').replace(',', '--')
            search_url = f"{base_url}/d/{location_slug}/all-events/?page=1"
            if search_query:
                # Add search query parameter
                search_url += f"&q={search_query.replace(' ', '+')}"
        else:
            # Use search endpoint
            search_url = f"{base_url}/d/online/all-events/?page=1&q={search_query.replace(' ', '+')}"

        # Prepare actor input
        run_input = {
            "start_urls": [{"url": search_url}],
            "max_results": max_results
        }

        try:
            logger.info(f"Starting Apify actor: newpo/eventbrite-scraper")
            logger.info(f"Scraping URL: {search_url}")

            # Run the actor and wait for it to finish
            run = self.client.actor("newpo/eventbrite-scraper").call(run_input=run_input)

            # Get dataset ID
            dataset_id = run.get("defaultDatasetId")
            if not dataset_id:
                logger.error("No dataset ID returned from Apify")
                return []

            logger.info(f"✓ Scraping complete. Dataset: {dataset_id}")

            # Fetch results from dataset
            events = []
            dataset = self.client.dataset(dataset_id)

            for item in dataset.iterate_items():
                try:
                    event = self._parse_event_from_apify(item)
                    if event:
                        events.append(event)
                except Exception as e:
                    logger.debug(f"Error parsing event: {str(e)}")
                    continue

            logger.info(f"✓ Parsed {len(events)} events from Apify results")
            return events[:max_results]

        except Exception as e:
            logger.error(f"Apify scraping failed: {str(e)}")
            return []

    def scrape_event_details(self, event_url: str) -> Optional[Dict[str, Any]]:
        """
        Scrape detailed information about a specific event.

        Args:
            event_url: URL of the Eventbrite event

        Returns:
            Dictionary with event details including sponsors
        """
        if not self.client:
            logger.warning("Apify client not initialized")
            return None

        logger.info(f"Scraping event details: {event_url}")

        run_input = {
            "start_urls": [{"url": event_url}],
            "max_results": 1
        }

        try:
            run = self.client.actor("newpo/eventbrite-scraper").call(run_input=run_input)
            dataset_id = run.get("defaultDatasetId")

            if not dataset_id:
                return None

            # Get first item from dataset
            dataset = self.client.dataset(dataset_id)
            items = list(dataset.iterate_items())

            if items:
                return items[0]

            return None

        except Exception as e:
            logger.error(f"Failed to scrape event details: {str(e)}")
            return None

    def extract_sponsors_from_events(self, events: List[Event]) -> Dict[str, Sponsor]:
        """
        Extract sponsors from scraped event data.

        Args:
            events: List of Event objects with scraped data

        Returns:
            Dictionary of sponsor name to Sponsor object
        """
        sponsors = {}

        for event in events:
            # Try to scrape event page for sponsor information
            if event.url:
                event_details = self.scrape_event_details(event.url)

                if event_details:
                    # Extract sponsor information from event details
                    event_sponsors = self._extract_sponsors_from_event_data(
                        event_details, event.name
                    )

                    for sponsor in event_sponsors:
                        if sponsor.company_name in sponsors:
                            sponsors[sponsor.company_name].add_event(event.name)
                        else:
                            sponsor.add_event(event.name)
                            sponsors[sponsor.company_name] = sponsor

                # Be polite - don't hammer the server
                time.sleep(1)

        logger.info(f"Extracted {len(sponsors)} sponsors from Apify results")
        return sponsors

    def _parse_event_from_apify(self, item: Dict[str, Any]) -> Optional[Event]:
        """Parse an event from Apify scraper output."""
        try:
            # Common field mappings from Apify EventBrite scraper
            name = item.get('name') or item.get('title') or item.get('event_name')
            description = item.get('description') or item.get('summary') or ''
            url = item.get('url') or item.get('link') or item.get('event_url')

            # Parse date
            date_str = item.get('start_date') or item.get('date') or item.get('startDate')
            event_date = None
            if date_str:
                try:
                    # Try different date formats
                    for fmt in ['%Y-%m-%dT%H:%M:%S', '%Y-%m-%d', '%B %d, %Y']:
                        try:
                            event_date = datetime.strptime(date_str, fmt)
                            break
                        except:
                            continue
                except:
                    pass

            # Location
            location = None
            if 'venue' in item:
                venue = item['venue']
                if isinstance(venue, dict):
                    city = venue.get('city', '')
                    region = venue.get('region', '')
                    country = venue.get('country', '')
                    location = ', '.join([p for p in [city, region, country] if p])
                elif isinstance(venue, str):
                    location = venue
            else:
                location = item.get('location') or item.get('city') or 'Online'

            # Organizer info (potential sponsor)
            organizer = item.get('organizer') or item.get('organizer_name')

            if not name:
                return None

            event = Event(
                name=name,
                event_type='conference',  # Default, could be enhanced
                industry='general',  # Default, could be enhanced
                description=description[:500] if description else '',
                date=event_date,
                location=location,
                url=url
            )

            # Store organizer for potential sponsor extraction
            if organizer:
                event._organizer = organizer  # Temporary storage

            return event

        except Exception as e:
            logger.debug(f"Error parsing event: {str(e)}")
            return None

    def _extract_sponsors_from_event_data(
        self,
        event_data: Dict[str, Any],
        event_name: str
    ) -> List[Sponsor]:
        """Extract sponsors from event data."""
        sponsors = []

        # Look for organizer as potential sponsor
        organizer = event_data.get('organizer') or event_data.get('organizer_name')
        if organizer and isinstance(organizer, str):
            sponsor = Sponsor(
                company_name=organizer,
                website=event_data.get('organizer_url')
            )
            sponsors.append(sponsor)

        # Look for sponsors in description or other fields
        description = event_data.get('description', '')
        if description:
            # Common patterns for sponsor mentions
            sponsor_keywords = [
                'sponsored by', 'presented by', 'in partnership with',
                'supported by', 'brought to you by'
            ]

            for keyword in sponsor_keywords:
                if keyword in description.lower():
                    # Try to extract company names after the keyword
                    # This is a simplified extraction - could be enhanced
                    pass

        # Check if event data has explicit sponsor fields
        if 'sponsors' in event_data:
            sponsor_list = event_data['sponsors']
            if isinstance(sponsor_list, list):
                for sponsor_data in sponsor_list:
                    if isinstance(sponsor_data, dict):
                        sponsor = Sponsor(
                            company_name=sponsor_data.get('name', 'Unknown'),
                            website=sponsor_data.get('website') or sponsor_data.get('url'),
                            tier=sponsor_data.get('tier') or sponsor_data.get('level')
                        )
                        sponsors.append(sponsor)
                    elif isinstance(sponsor_data, str):
                        sponsor = Sponsor(company_name=sponsor_data)
                        sponsors.append(sponsor)

        return sponsors

    def is_available(self) -> bool:
        """Check if Apify service is available and configured."""
        return self.client is not None
