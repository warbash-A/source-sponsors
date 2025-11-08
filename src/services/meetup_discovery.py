"""Service for discovering events using Meetup API.

This service provides Meetup API integration for finding events and groups,
serving as an additional data source alongside Eventbrite.
"""

import os
import requests
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models import Event
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class MeetupApiClient:
    """Meetup API client for event discovery."""

    def __init__(self, api_key: str):
        """Initialize the Meetup API client.

        Args:
            api_key: Meetup API key or OAuth token
        """
        self.api_key = api_key
        self.base_url = "https://api.meetup.com"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def search_events(
        self,
        query: Optional[str] = None,
        location: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius: Optional[int] = 25,  # miles
        category_ids: Optional[List[int]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """
        Search for events on Meetup.

        Args:
            query: Search query string
            location: Location string (e.g., "San Francisco, CA")
            latitude: Latitude for location search
            longitude: Longitude for location search
            radius: Search radius in miles (default: 25)
            category_ids: List of Meetup category IDs
            start_date: ISO format date string
            end_date: ISO format date string
            page: Page number for pagination
            page_size: Results per page

        Returns:
            Dictionary with 'events' list
        """
        # Meetup API v3 endpoint
        endpoint = f"{self.base_url}/find/upcoming_events"

        params = {}

        if query:
            params['text'] = query

        # Location handling
        if latitude and longitude:
            params['lat'] = latitude
            params['lon'] = longitude
        elif location:
            params['location'] = location

        if radius:
            params['radius'] = radius

        if category_ids:
            params['category'] = ','.join(str(c) for c in category_ids)

        # Meetup uses different date format
        if start_date:
            params['start_date_range'] = start_date

        if end_date:
            params['end_date_range'] = end_date

        params['page'] = page_size
        params['offset'] = (page - 1) * page_size

        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            return {
                'events': data.get('events', []),
                'total_count': data.get('total_count', 0)
            }

        except requests.exceptions.HTTPError as e:
            error_msg = str(e)
            if e.response:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('errors', [{}])[0].get('message', str(e))
                except:
                    error_msg = e.response.text or str(e)
            raise Exception(f"Meetup API error: {error_msg}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    def get_event(self, event_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific event.

        Args:
            event_id: Meetup event ID

        Returns:
            Event details dictionary
        """
        try:
            response = requests.get(
                f"{self.base_url}/2/event/{event_id}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            error_msg = str(e)
            if e.response:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('errors', [{}])[0].get('message', str(e))
                except:
                    error_msg = e.response.text or str(e)
            raise Exception(f"Meetup API error: {error_msg}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    def get_group(self, group_urlname: str) -> Dict[str, Any]:
        """
        Get information about a specific Meetup group.

        Args:
            group_urlname: Meetup group URL name

        Returns:
            Group details dictionary
        """
        try:
            response = requests.get(
                f"{self.base_url}/{group_urlname}",
                headers=self.headers,
                timeout=10
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as e:
            error_msg = str(e)
            if e.response:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('errors', [{}])[0].get('message', str(e))
                except:
                    error_msg = e.response.text or str(e)
            raise Exception(f"Meetup API error: {error_msg}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")


class MeetupDiscoveryService:
    """Service to discover events from Meetup."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the Meetup discovery service.

        Args:
            api_key: Meetup API key
        """
        self.api_key = api_key or os.getenv('MEETUP_API_KEY')
        self.client = None

        if self.api_key:
            self.client = MeetupApiClient(self.api_key)
            logger.info("✓ Meetup API client initialized")

    def discover_events(
        self,
        event_type: str,
        industry: str,
        description: str,
        location: Optional[str] = None,
        category_ids: Optional[List[int]] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        max_results: int = 20
    ) -> List[Event]:
        """
        Discover events from Meetup.

        Args:
            event_type: Type of event (conference, workshop, meetup, etc.)
            industry: Industry category
            description: Event description
            location: Location string
            category_ids: List of Meetup category IDs
            start_date: Start date filter
            end_date: End date filter
            max_results: Maximum number of results

        Returns:
            List of Event objects
        """
        if not self.client:
            logger.warning("Meetup API client not initialized")
            return []

        logger.info(f"Searching Meetup for {event_type} in {industry} industry")

        events = []

        # Build search query
        query = f"{event_type} {industry}"

        # Convert datetime to ISO format strings
        start_date_iso = start_date.isoformat() if start_date else None
        end_date_iso = end_date.isoformat() if end_date else None

        try:
            # Search with parameters
            result = self.client.search_events(
                query=query,
                location=location,
                category_ids=category_ids,
                start_date=start_date_iso,
                end_date=end_date_iso,
                page=1,
                page_size=min(max_results, 50)
            )

            for event_data in result.get('events', []):
                try:
                    # Extract event details
                    event = Event(
                        name=event_data.get('name', 'Unknown Event'),
                        event_type=event_type,
                        industry=industry,
                        description=event_data.get('description', '')[:500],
                        date=self._parse_date(event_data.get('local_date'), event_data.get('local_time')),
                        location=self._format_location(event_data),
                        url=event_data.get('link')
                    )
                    events.append(event)
                except Exception as e:
                    logger.debug(f"Error parsing Meetup event: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Meetup API error: {str(e)}")
            raise

        logger.info(f"Found {len(events)} events from Meetup")
        return events

    @staticmethod
    def _parse_date(date_str: Optional[str], time_str: Optional[str]) -> Optional[datetime]:
        """Parse Meetup date and time strings to datetime object."""
        if not date_str:
            return None

        try:
            # Meetup provides separate date and time
            if time_str:
                datetime_str = f"{date_str} {time_str}"
                return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M')
            else:
                return datetime.strptime(date_str, '%Y-%m-%d')
        except:
            return None

    @staticmethod
    def _format_location(event_data: Dict[str, Any]) -> str:
        """Format location from Meetup event data."""
        venue = event_data.get('venue', {})
        if venue:
            city = venue.get('city', '')
            state = venue.get('state', '')
            country = venue.get('country', '')

            parts = [p for p in [city, state, country] if p]
            return ', '.join(parts)

        # Check for group location
        group = event_data.get('group', {})
        if group:
            city = group.get('localized_location', '')
            if city:
                return city

        return 'Online' if event_data.get('online_event', False) else 'TBD'
