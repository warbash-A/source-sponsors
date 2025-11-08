"""Enhanced service for discovering events using Eventbrite API.

This service provides full Eventbrite API integration with capabilities matching
the Eventbrite MCP server, including:
- Advanced search with location, categories, dates, and price filters
- Event details retrieval
- Venue information
- Category listings
"""

import os
import requests
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from bs4 import BeautifulSoup
import time

from ..models import Event
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class EventbriteApiClient:
    """Enhanced Eventbrite API client with full MCP capabilities."""

    def __init__(self, api_key: str):
        """Initialize the Eventbrite API client."""
        self.api_key = api_key
        self.base_url = "https://www.eventbriteapi.com/v3"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def search_events(
        self,
        query: Optional[str] = None,
        location_latitude: Optional[float] = None,
        location_longitude: Optional[float] = None,
        location_within: Optional[str] = None,
        location_address: Optional[str] = None,
        categories: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        price: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Dict[str, Any]:
        """
        Search for events with advanced filters.

        Args:
            query: Search query string
            location_latitude: Latitude for location search
            location_longitude: Longitude for location search
            location_within: Distance radius (e.g., '10km', '10mi')
            location_address: Address string for location search
            categories: List of category IDs
            start_date: ISO format date string (e.g., '2024-01-01T00:00:00Z')
            end_date: ISO format date string
            price: Filter by 'free' or 'paid' events
            page: Page number for pagination
            page_size: Results per page (max 100)

        Returns:
            Dictionary with 'events' and 'pagination' keys
        """
        params = {}

        if query:
            params['q'] = query

        # Location handling - multiple options
        if location_latitude and location_longitude:
            params['location.latitude'] = location_latitude
            params['location.longitude'] = location_longitude
            if location_within:
                params['location.within'] = location_within
        elif location_address:
            params['location.address'] = location_address

        if categories:
            params['categories'] = ','.join(categories)

        if start_date:
            params['start_date.range_start'] = start_date

        if end_date:
            params['start_date.range_end'] = end_date

        if price:
            params['price'] = price

        params['page'] = page
        params['page_size'] = min(page_size, 100)

        try:
            response = requests.get(
                f"{self.base_url}/events/search",
                headers=self.headers,
                params=params,
                timeout=10
            )

            # Log the actual URL being called for debugging
            logger.debug(f"Eventbrite API request: {response.url}")

            response.raise_for_status()
            data = response.json()

            return {
                'events': data.get('events', []),
                'pagination': data.get('pagination', {})
            }

        except requests.exceptions.HTTPError as e:
            # Enhanced error handling with specific guidance
            status_code = e.response.status_code if e.response else 'unknown'
            url = e.response.url if e.response else 'unknown'

            if status_code == 403:
                error_msg = (
                    f"403 Forbidden: API credentials rejected. "
                    f"You may be using an OAuth Client Secret instead of a Personal OAuth Token. "
                    f"Get a Personal OAuth Token from https://www.eventbrite.com/account-settings/apps"
                )
            elif status_code == 401:
                error_msg = f"401 Unauthorized: API key is invalid or expired"
            elif status_code == 404:
                error_msg = f"404 Not Found: Endpoint {url} doesn't exist"
            else:
                try:
                    error_data = e.response.json() if e.response else {}
                    error_msg = error_data.get('error_description', str(e))
                except:
                    error_msg = str(e)

            raise Exception(f"Eventbrite API error ({status_code}): {error_msg}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    def get_event(self, event_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific event.

        Args:
            event_id: Eventbrite event ID

        Returns:
            Event details dictionary
        """
        try:
            response = requests.get(
                f"{self.base_url}/events/{event_id}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            error_msg = e.response.json().get('error_description', str(e)) if e.response else str(e)
            raise Exception(f"Eventbrite API error: {error_msg}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    def get_venue(self, venue_id: str) -> Dict[str, Any]:
        """
        Get information about a specific venue.

        Args:
            venue_id: Eventbrite venue ID

        Returns:
            Venue details dictionary
        """
        try:
            response = requests.get(
                f"{self.base_url}/venues/{venue_id}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            error_msg = e.response.json().get('error_description', str(e)) if e.response else str(e)
            raise Exception(f"Eventbrite API error: {error_msg}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    def get_categories(self) -> List[Dict[str, Any]]:
        """
        Get a list of all Eventbrite event categories.

        Returns:
            List of category dictionaries
        """
        try:
            response = requests.get(
                f"{self.base_url}/categories",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json().get('categories', [])

        except requests.exceptions.HTTPError as e:
            error_msg = e.response.json().get('error_description', str(e)) if e.response else str(e)
            raise Exception(f"Eventbrite API error: {error_msg}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")


class EventDiscoveryService:
    """Service to discover similar events from various sources."""

    def __init__(
        self,
        eventbrite_api_key: Optional[str] = None,
        meetup_api_key: Optional[str] = None,
        apify_api_token: Optional[str] = None,
        use_apify: bool = True,
        use_meetup: bool = True
    ):
        """Initialize the event discovery service.

        Args:
            eventbrite_api_key: Eventbrite API key
            meetup_api_key: Meetup API key
            apify_api_token: Apify API token for enhanced scraping
            use_apify: Whether to use Apify for web scraping (default: True)
            use_meetup: Whether to use Meetup API (default: True)
        """
        self.eventbrite_api_key = eventbrite_api_key or os.getenv('EVENTBRITE_API_KEY')
        self.eventbrite_client = None
        self.meetup_service = None
        self.apify_scraper = None
        self.use_apify = use_apify
        self.use_meetup = use_meetup

        if self.eventbrite_api_key:
            self.eventbrite_client = EventbriteApiClient(self.eventbrite_api_key)
            logger.info("✓ Eventbrite API client initialized")

        # Initialize Meetup service if enabled
        if use_meetup:
            try:
                from .meetup_discovery import MeetupDiscoveryService
                meetup_key = meetup_api_key or os.getenv('MEETUP_API_KEY')
                if meetup_key:
                    self.meetup_service = MeetupDiscoveryService(meetup_key)
                    logger.info("✓ Meetup API client initialized")
            except Exception as e:
                logger.debug(f"Meetup client not available: {str(e)}")

        # Initialize Apify scraper if enabled
        if use_apify:
            try:
                from .apify_scraper import ApifyEventbriteScraperService
                self.apify_scraper = ApifyEventbriteScraperService(apify_api_token)
                if self.apify_scraper.is_available():
                    logger.info("✓ Apify scraper initialized")
            except Exception as e:
                logger.debug(f"Apify scraper not available: {str(e)}")

    def discover_similar_events(
        self,
        event_type: str,
        industry: str,
        description: str,
        location: Optional[str] = None,
        categories: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        price: Optional[str] = None,
        max_results: int = 20
    ) -> List[Event]:
        """
        Discover similar events from multiple sources.

        Args:
            event_type: Type of event (conference, workshop, etc.)
            industry: Industry category
            description: Event description
            location: Location string or address
            categories: List of Eventbrite category IDs
            start_date: Start date filter
            end_date: End date filter
            price: Price filter ('free' or 'paid')
            max_results: Maximum number of results

        Returns:
            List of Event objects
        """
        logger.info(f"Discovering similar events for {event_type} in {industry} industry")

        similar_events = []

        # Try Eventbrite API first with enhanced search
        if self.eventbrite_client:
            try:
                eventbrite_events = self._search_eventbrite_enhanced(
                    event_type=event_type,
                    industry=industry,
                    description=description,
                    location=location,
                    categories=categories,
                    start_date=start_date,
                    end_date=end_date,
                    price=price,
                    max_results=max_results
                )
                similar_events.extend(eventbrite_events)
                logger.info(f"Found {len(eventbrite_events)} events from Eventbrite")
            except Exception as e:
                logger.warning(f"Eventbrite search failed: {str(e)}")

        # Try Meetup API (if available and enabled)
        if len(similar_events) < max_results and self.meetup_service:
            try:
                meetup_events = self.meetup_service.discover_events(
                    event_type=event_type,
                    industry=industry,
                    description=description,
                    location=location,
                    start_date=start_date,
                    end_date=end_date,
                    max_results=max_results - len(similar_events)
                )
                similar_events.extend(meetup_events)
                logger.info(f"Found {len(meetup_events)} events from Meetup")
            except Exception as e:
                logger.warning(f"Meetup search failed: {str(e)}")

        # Apify scraping (if available and enabled)
        if len(similar_events) < max_results and self.apify_scraper and self.apify_scraper.is_available():
            try:
                search_query = f"{event_type} {industry}"
                apify_events = self.apify_scraper.scrape_events(
                    search_query=search_query,
                    location=location,
                    max_results=max_results - len(similar_events)
                )
                similar_events.extend(apify_events)
                logger.info(f"Found {len(apify_events)} events from Apify scraper")
            except Exception as e:
                logger.warning(f"Apify scraping failed: {str(e)}")

        # Sample data fallback (for demonstration)
        if len(similar_events) < max_results:
            try:
                scraped_events = self._scrape_events(
                    event_type, industry, description, max_results - len(similar_events)
                )
                similar_events.extend(scraped_events)
                logger.info(f"Found {len(scraped_events)} events from fallback")
            except Exception as e:
                logger.warning(f"Fallback generation failed: {str(e)}")

        logger.info(f"Total similar events found: {len(similar_events)}")
        return similar_events[:max_results]

    def _search_eventbrite_enhanced(
        self,
        event_type: str,
        industry: str,
        description: str,
        location: Optional[str] = None,
        categories: Optional[List[str]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        price: Optional[str] = None,
        max_results: int = 20
    ) -> List[Event]:
        """Search for events using enhanced Eventbrite API with MCP capabilities."""
        if not self.eventbrite_client:
            return []

        events = []

        # Build search query
        keywords = f"{event_type} {industry}"

        # Convert datetime to ISO format strings
        start_date_iso = start_date.isoformat() if start_date else None
        end_date_iso = end_date.isoformat() if end_date else None

        try:
            # Search with enhanced parameters
            result = self.eventbrite_client.search_events(
                query=keywords,
                location_address=location,
                categories=categories,
                start_date=start_date_iso,
                end_date=end_date_iso,
                price=price,
                page=1,
                page_size=min(max_results, 50)
            )

            for event_data in result.get('events', []):
                try:
                    # Extract event details
                    event = Event(
                        name=event_data.get('name', {}).get('text', 'Unknown Event'),
                        event_type=event_type,
                        industry=industry,
                        description=event_data.get('description', {}).get('text', '')[:500],
                        date=self._parse_date(event_data.get('start', {}).get('utc')),
                        location=self._format_location(event_data),
                        url=event_data.get('url')
                    )
                    events.append(event)
                except Exception as e:
                    logger.debug(f"Error parsing event: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Eventbrite API error: {str(e)}")
            raise

        return events

    def get_event_details(self, event_id: str) -> Optional[Event]:
        """
        Get detailed information about a specific Eventbrite event.

        Args:
            event_id: Eventbrite event ID

        Returns:
            Event object with detailed information
        """
        if not self.eventbrite_client:
            logger.warning("Eventbrite API client not initialized")
            return None

        try:
            event_data = self.eventbrite_client.get_event(event_id)

            event = Event(
                name=event_data.get('name', {}).get('text', 'Unknown Event'),
                event_type='conference',  # Default
                industry='general',  # Default
                description=event_data.get('description', {}).get('text', ''),
                date=self._parse_date(event_data.get('start', {}).get('utc')),
                location=self._format_location(event_data),
                url=event_data.get('url')
            )

            logger.info(f"Retrieved details for event: {event.name}")
            return event

        except Exception as e:
            logger.error(f"Failed to get event details: {str(e)}")
            return None

    def get_categories(self) -> List[Dict[str, Any]]:
        """
        Get list of all Eventbrite categories.

        Returns:
            List of category dictionaries with id, name, etc.
        """
        if not self.eventbrite_client:
            logger.warning("Eventbrite API client not initialized")
            return []

        try:
            categories = self.eventbrite_client.get_categories()
            logger.info(f"Retrieved {len(categories)} Eventbrite categories")
            return categories
        except Exception as e:
            logger.error(f"Failed to get categories: {str(e)}")
            return []

    def _scrape_events(
        self,
        event_type: str,
        industry: str,
        description: str,
        max_results: int
    ) -> List[Event]:
        """Scrape events from web sources."""
        events = []

        # Build search query
        search_query = f"{event_type} {industry} conference sponsors"

        # Use a simple web search simulation (in production, you'd use real search APIs)
        # For now, we'll create some sample events to demonstrate the workflow
        logger.info("Web scraping is a fallback - in production, integrate with search APIs")

        # This would be replaced with actual scraping logic
        sample_events = self._generate_sample_events(event_type, industry)
        events.extend(sample_events[:max_results])

        return events

    def _generate_sample_events(self, event_type: str, industry: str) -> List[Event]:
        """Generate sample events for demonstration purposes."""
        # This is a placeholder that would be replaced with actual web scraping
        sample_event_names = [
            f"{industry.title()} Innovation Summit 2024",
            f"Global {event_type.title()} Conference",
            f"{industry.title()} Leaders Forum",
            f"International {industry.title()} Expo",
            f"{event_type.title()} & Technology Summit"
        ]

        events = []
        for name in sample_event_names:
            event = Event(
                name=name,
                event_type=event_type,
                industry=industry,
                description=f"A premier {event_type} focused on {industry} industry trends and innovation.",
                date=datetime(2024, 6, 15),
                location="Virtual/Hybrid",
                url=f"https://example.com/{name.lower().replace(' ', '-')}"
            )
            events.append(event)

        return events

    @staticmethod
    def _parse_date(date_string: Optional[str]) -> Optional[datetime]:
        """Parse date string to datetime object."""
        if not date_string:
            return None

        try:
            return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        except:
            return None

    @staticmethod
    def _format_location(event_data: Dict[str, Any]) -> str:
        """Format location from event data."""
        venue = event_data.get('venue')
        if venue:
            address = venue.get('address', {})
            city = address.get('city', '')
            region = address.get('region', '')
            country = address.get('country', '')

            parts = [p for p in [city, region, country] if p]
            return ', '.join(parts)

        return event_data.get('online_event', False) and 'Online' or 'TBD'
