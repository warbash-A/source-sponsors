"""Service for discovering similar events."""

import os
import requests
from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import time

from ..models import Event
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class EventDiscoveryService:
    """Service to discover similar events from various sources."""

    def __init__(self, eventbrite_api_key: Optional[str] = None):
        """Initialize the event discovery service."""
        self.eventbrite_api_key = eventbrite_api_key or os.getenv('EVENTBRITE_API_KEY')
        self.eventbrite_base_url = 'https://www.eventbriteapi.com/v3'

    def discover_similar_events(
        self,
        event_type: str,
        industry: str,
        description: str,
        location: Optional[str] = None,
        max_results: int = 20
    ) -> List[Event]:
        """Discover similar events from multiple sources."""
        logger.info(f"Discovering similar events for {event_type} in {industry} industry")

        similar_events = []

        # Try Eventbrite API first
        if self.eventbrite_api_key:
            try:
                eventbrite_events = self._search_eventbrite(
                    event_type, industry, description, location, max_results
                )
                similar_events.extend(eventbrite_events)
                logger.info(f"Found {len(eventbrite_events)} events from Eventbrite")
            except Exception as e:
                logger.warning(f"Eventbrite search failed: {str(e)}")

        # Web scraping fallback (search multiple sources)
        try:
            scraped_events = self._scrape_events(
                event_type, industry, description, max_results - len(similar_events)
            )
            similar_events.extend(scraped_events)
            logger.info(f"Found {len(scraped_events)} events from web scraping")
        except Exception as e:
            logger.warning(f"Web scraping failed: {str(e)}")

        logger.info(f"Total similar events found: {len(similar_events)}")
        return similar_events[:max_results]

    def _search_eventbrite(
        self,
        event_type: str,
        industry: str,
        description: str,
        location: Optional[str],
        max_results: int
    ) -> List[Event]:
        """Search for events using Eventbrite API."""
        if not self.eventbrite_api_key:
            return []

        events = []
        headers = {
            'Authorization': f'Bearer {self.eventbrite_api_key}'
        }

        # Build search query
        keywords = f"{event_type} {industry}"
        params = {
            'q': keywords,
            'sort_by': 'best',
            'page_size': min(max_results, 50)
        }

        if location:
            params['location.address'] = location

        try:
            response = requests.get(
                f"{self.eventbrite_base_url}/events/search/",
                headers=headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            for event_data in data.get('events', []):
                try:
                    event = Event(
                        name=event_data.get('name', {}).get('text', 'Unknown Event'),
                        event_type=event_type,
                        industry=industry,
                        description=event_data.get('description', {}).get('text', '')[:500],
                        date=self._parse_date(event_data.get('start', {}).get('utc')),
                        location=event_data.get('venue', {}).get('address', {}).get('localized_area_display'),
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
