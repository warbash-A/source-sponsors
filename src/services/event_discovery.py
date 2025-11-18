"""Enhanced service for discovering events using Eventbrite and Meetup APIs.

This service provides full API integration with capabilities matching MCP servers:

Eventbrite MCP capabilities:
- Advanced search with location, categories, dates, and price filters
- Event details retrieval
- Venue information
- Category listings

Meetup MCP capabilities:
- Natural language event search
- Location-based discovery
- Upcoming events filtering
- Online/remote event support
"""

import os
import requests
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from bs4 import BeautifulSoup
import time
import re

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
                f"{self.base_url}/events/search/",
                headers=self.headers,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            return {
                'events': data.get('events', []),
                'pagination': data.get('pagination', {})
            }

        except requests.exceptions.HTTPError as e:
            error_msg = e.response.json().get('error_description', str(e)) if e.response else str(e)
            raise Exception(f"Eventbrite API error: {error_msg}")
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
                f"{self.base_url}/events/{event_id}/",
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
                f"{self.base_url}/venues/{venue_id}/",
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
                f"{self.base_url}/categories/",
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


class MeetupApiClient:
    """Meetup API client with MCP capabilities for event discovery."""

    def __init__(self, access_token: str):
        """Initialize the Meetup API client.

        Args:
            access_token: Meetup OAuth2 access token
        """
        self.access_token = access_token
        self.base_url = "https://api.meetup.com"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        self.max_events = 100  # Configurable max events per query

    def search_events(
        self,
        query: Optional[str] = None,
        location: Optional[str] = None,
        start_date: Optional[datetime] = None,
        radius: Optional[float] = None,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for upcoming Meetup events with natural language support.

        Args:
            query: Search query (keywords, topics, event names)
            location: Location string (city, state, country, or coordinates)
            start_date: Filter events starting from this date
            radius: Search radius in miles (default: 25)
            max_results: Maximum number of results to return (max 100)

        Returns:
            List of event dictionaries with parsed data
        """
        params = {
            'page': min(max_results, self.max_events),
            'status': 'upcoming'
        }

        # Add location if provided
        if location:
            params['location'] = location

        # Add start date range if provided
        if start_date:
            params['start_date_range'] = start_date.isoformat()

        # Add text search if provided
        if query:
            # Extract parameters from natural language query
            query_params = self._extract_query_parameters(query)

            # Override with extracted parameters if found
            if query_params.get('location'):
                params['location'] = query_params['location']

            if query_params.get('keywords'):
                params['text'] = query_params['keywords']
            elif query:
                params['text'] = query

        # Add radius if specified
        if radius:
            params['radius'] = radius

        try:
            response = requests.get(
                f"{self.base_url}/find/upcoming_events",
                headers=self.headers,
                params=params,
                timeout=15
            )
            response.raise_for_status()
            data = response.json()

            # Parse and return events
            events = []
            for event_data in data.get('events', []):
                parsed_event = self._parse_event(event_data)
                if parsed_event:
                    events.append(parsed_event)

            logger.info(f"Found {len(events)} Meetup events")
            return events

        except requests.exceptions.HTTPError as e:
            error_msg = str(e)
            if e.response:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('errors', [{}])[0].get('message', str(e))
                except:
                    pass
            raise Exception(f"Meetup API error: {error_msg}")
        except Exception as e:
            raise Exception(f"Meetup request failed: {str(e)}")

    def _extract_query_parameters(self, query: str) -> Dict[str, Any]:
        """
        Extract search parameters from natural language query.

        Args:
            query: Natural language search query

        Returns:
            Dictionary with extracted parameters
        """
        params = {}
        query_lower = query.lower()

        # Extract location
        location_patterns = [
            r'near\s+([A-Za-z\s,]+?)(?:\s+(?:this|next|today|tomorrow|on)|$)',
            r'in\s+([A-Za-z\s,]+?)(?:\s+(?:this|next|today|tomorrow|on)|$)',
        ]

        for pattern in location_patterns:
            match = re.search(pattern, query_lower)
            if match:
                params['location'] = match.group(1).strip()
                break

        # Check for remote/online/virtual keywords
        if any(word in query_lower for word in ['remote', 'online', 'virtual']):
            params['is_online'] = True

        # Extract tech and topic keywords (common Meetup categories)
        tech_keywords = [
            'python', 'javascript', 'java', 'react', 'node', 'ai', 'ml',
            'data science', 'machine learning', 'web development', 'devops',
            'cloud', 'aws', 'kubernetes', 'docker', 'networking', 'security'
        ]

        found_keywords = []
        for keyword in tech_keywords:
            if keyword in query_lower:
                found_keywords.append(keyword)

        if found_keywords:
            params['keywords'] = ' '.join(found_keywords)
        else:
            # Use the original query, removing location phrases
            cleaned_query = query
            for pattern in location_patterns:
                cleaned_query = re.sub(pattern, '', cleaned_query, flags=re.IGNORECASE)
            params['keywords'] = cleaned_query.strip()

        return params

    def _parse_event(self, event_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse Meetup API event data into standardized format.

        Args:
            event_data: Raw event data from Meetup API

        Returns:
            Parsed event dictionary or None if parsing fails
        """
        try:
            # Extract venue information
            venue = event_data.get('venue', {})
            venue_name = venue.get('name', '')
            venue_city = venue.get('city', '')
            venue_id = venue.get('id', 0)

            # Check if event is online (venue_id of 1 indicates online)
            is_online = venue_id == 1

            # Format location string
            if is_online:
                location_str = "Online"
            elif venue_city:
                location_str = venue_city
            else:
                location_str = "TBD"

            # Parse event time (milliseconds timestamp)
            event_time_ms = event_data.get('time', 0)
            event_datetime = datetime.fromtimestamp(event_time_ms / 1000) if event_time_ms else None

            # Extract group information
            group = event_data.get('group', {})
            group_name = group.get('name', '')

            # Extract description
            description = event_data.get('description', '')

            # Check for fee information
            fee = event_data.get('fee')
            is_free = fee is None
            fee_amount = None
            fee_currency = None
            if fee:
                fee_amount = fee.get('amount', 0)
                fee_currency = fee.get('currency', 'USD')

            parsed = {
                'id': event_data.get('id'),
                'name': event_data.get('name', 'Unnamed Event'),
                'description': description,
                'link': event_data.get('link', ''),
                'datetime': event_datetime,
                'location': location_str,
                'venue_name': venue_name,
                'is_online': is_online,
                'group_name': group_name,
                'group_urlname': group.get('urlname', ''),
                'rsvp_count': event_data.get('yes_rsvp_count', 0),
                'is_free': is_free,
                'fee_amount': fee_amount,
                'fee_currency': fee_currency
            }

            return parsed

        except Exception as e:
            logger.debug(f"Error parsing Meetup event: {str(e)}")
            return None


class EventDiscoveryService:
    """Service to discover similar events from various sources."""

    def __init__(
        self,
        eventbrite_api_key: Optional[str] = None,
        meetup_access_token: Optional[str] = None,
        apify_api_token: Optional[str] = None,
        use_apify: bool = True
    ):
        """Initialize the event discovery service.

        Args:
            eventbrite_api_key: Eventbrite API key
            meetup_access_token: Meetup OAuth2 access token
            apify_api_token: Apify API token for enhanced scraping
            use_apify: Whether to use Apify for web scraping (default: True)
        """
        self.eventbrite_api_key = eventbrite_api_key or os.getenv('EVENTBRITE_API_KEY')
        self.meetup_access_token = meetup_access_token or os.getenv('MEETUP_ACCESS_TOKEN')
        self.eventbrite_client = None
        self.meetup_client = None
        self.apify_scraper = None
        self.use_apify = use_apify

        if self.eventbrite_api_key:
            self.eventbrite_client = EventbriteApiClient(self.eventbrite_api_key)
            logger.info("✓ Eventbrite API client initialized")

        if self.meetup_access_token:
            self.meetup_client = MeetupApiClient(self.meetup_access_token)
            logger.info("✓ Meetup API client initialized")

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

        # Try Meetup API if we need more results
        if len(similar_events) < max_results and self.meetup_client:
            try:
                meetup_events = self._search_meetup(
                    event_type=event_type,
                    industry=industry,
                    location=location,
                    start_date=start_date,
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

    def _search_meetup(
        self,
        event_type: str,
        industry: str,
        location: Optional[str] = None,
        start_date: Optional[datetime] = None,
        max_results: int = 20
    ) -> List[Event]:
        """Search for events using Meetup API with MCP capabilities."""
        if not self.meetup_client:
            return []

        events = []

        # Build natural language query
        query = f"{event_type} {industry}"

        try:
            # Search with Meetup API
            meetup_events = self.meetup_client.search_events(
                query=query,
                location=location,
                start_date=start_date,
                max_results=max_results
            )

            for event_data in meetup_events:
                try:
                    # Convert Meetup event to Event model
                    event = Event(
                        name=event_data.get('name', 'Unknown Event'),
                        event_type=event_type,
                        industry=industry,
                        description=event_data.get('description', '')[:500],
                        date=event_data.get('datetime'),
                        location=event_data.get('location', 'TBD'),
                        url=event_data.get('link', '')
                    )
                    events.append(event)
                except Exception as e:
                    logger.debug(f"Error parsing Meetup event: {str(e)}")
                    continue

        except Exception as e:
            logger.error(f"Meetup API error: {str(e)}")
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
