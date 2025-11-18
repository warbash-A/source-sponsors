# Meetup MCP Integration

This document explains the Meetup Model Context Protocol (MCP) integration in the Source Sponsors project.

## Overview

The project now includes full Meetup MCP capabilities, providing natural language event discovery features inspired by the `d4nshields/mcp-meetup` repository. This integration enables intelligent searching of Meetup.com events with location-based discovery, date filtering, and natural language query support.

## What is Meetup MCP?

The Meetup MCP (Model Context Protocol) is a system that provides standardized tools for interacting with the Meetup API. The original implementation was created as a Python-based MCP server to enable AI assistants to search for events, filter by location and time, and discover meetups using natural language queries.

## Integration Approach

Following the pattern established with Eventbrite, we implemented the Meetup MCP capabilities directly in Python with our own `MeetupApiClient` class. This provides:

1. **Consistent architecture** - Matches the Eventbrite integration pattern
2. **Native Python integration** - Works seamlessly with the existing event discovery system
3. **Natural language support** - Intelligent query parameter extraction
4. **Multi-source discovery** - Combines Meetup with Eventbrite and Apify for comprehensive results

## Features Implemented

### 1. Natural Language Event Search

The `MeetupApiClient` supports intelligent natural language queries:

```python
from src.services import EventDiscoveryService

service = EventDiscoveryService(
    eventbrite_api_key="your_eventbrite_key",
    meetup_access_token="your_meetup_token"
)

# Search with natural language and filters
events = service.discover_similar_events(
    event_type="meetup",
    industry="python programming",
    description="Python developers meetup",
    location="San Francisco, CA",
    start_date=datetime(2024, 6, 1),
    max_results=20
)
```

**Key Capabilities:**
- **Natural language processing** - Extracts keywords, locations, and topics from queries
- **Location-based search** - Find events near specific cities or addresses
- **Date filtering** - Filter events by start date
- **Online event support** - Automatically identifies virtual/remote meetups
- **Tech keyword extraction** - Recognizes common tech topics (Python, JavaScript, AI, etc.)

### 2. Direct API Search

For more control, you can use the `MeetupApiClient` directly:

```python
from src.services.event_discovery import MeetupApiClient

client = MeetupApiClient(access_token="your_token")

# Search for events
events = client.search_events(
    query="Python developers meetup",
    location="San Francisco, CA",
    start_date=datetime(2024, 6, 1),
    radius=25,  # miles
    max_results=20
)

for event in events:
    print(f"{event['name']} - {event['location']}")
    print(f"  Date: {event['datetime']}")
    print(f"  Link: {event['link']}")
    print(f"  RSVPs: {event['rsvp_count']}")
    print(f"  Free: {event['is_free']}")
```

**Search Parameters:**
- `query` - Search keywords or natural language query
- `location` - City, state, country, or coordinates
- `start_date` - Filter events starting from this date
- `radius` - Search radius in miles (default: 25)
- `max_results` - Maximum number of results (max: 100)

### 3. Event Data Structure

Meetup events are returned with the following structure:

```python
{
    'id': 'event_id',
    'name': 'Event Name',
    'description': 'Event description...',
    'link': 'https://www.meetup.com/...',
    'datetime': datetime(2024, 6, 15, 18, 0),
    'location': 'San Francisco, CA',
    'venue_name': 'Tech Hub SF',
    'is_online': False,
    'group_name': 'Python Developers Group',
    'group_urlname': 'python-devs-sf',
    'rsvp_count': 45,
    'is_free': True,
    'fee_amount': None,
    'fee_currency': None
}
```

### 4. Natural Language Query Extraction

The client intelligently extracts parameters from natural language:

**Location extraction:**
```python
"events near San Francisco"  → location="San Francisco"
"meetups in New York"        → location="New York"
```

**Online event detection:**
```python
"remote Python meetups"      → is_online=True
"virtual JavaScript events"  → is_online=True
"online data science"        → is_online=True
```

**Tech keyword recognition:**
```python
"Python programming"         → keywords="python"
"React and Node.js"          → keywords="react node"
"AI machine learning"        → keywords="ai machine learning"
```

Supported tech keywords include: Python, JavaScript, Java, React, Node, AI, ML, Data Science, Web Development, DevOps, Cloud, AWS, Kubernetes, Docker, Networking, Security

## Multi-Tier Event Discovery

The system now uses a **four-tier architecture** for comprehensive event discovery:

```
User Query
    │
    ├─► Tier 1: Eventbrite API (Official events)
    │
    ├─► Tier 2: Meetup API (Community meetups) ◄── NEW!
    │
    ├─► Tier 3: Apify Scraper (Web scraping fallback)
    │
    └─► Tier 4: Sample Data (Demo fallback)
```

The system automatically:
1. Searches Eventbrite first for professional conferences and events
2. Supplements with Meetup for community-driven meetups
3. Falls back to Apify scraping if more results needed
4. Uses sample data for demonstration purposes

## Setup and Configuration

### 1. Get Meetup OAuth2 Access Token

To use the Meetup API, you need an OAuth2 access token:

1. Go to [Meetup OAuth Consumers](https://www.meetup.com/api/oauth/list/)
2. Create a new OAuth consumer
3. Note your Client ID and Client Secret
4. Use the OAuth2 flow to obtain an access token

For detailed OAuth setup, see the [Meetup API documentation](https://www.meetup.com/api/authentication/).

### 2. Configure Environment Variables

Add your Meetup access token to `.env`:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your token
MEETUP_ACCESS_TOKEN=your_meetup_access_token_here
```

### 3. Verify Configuration

Check your API configuration status:

```bash
python main.py config
```

Should show:
```
Configuration Status:
============================================================
Eventbrite API Key: ✓ Configured
Meetup Access Token: ✓ Configured
Apify API Token: ✓ Configured
OpenAI API Key: ✓ Configured
```

## CLI Usage

### Basic Event Discovery

The existing `discover` command now automatically searches Meetup:

```bash
python main.py discover \
    --name "My Tech Conference" \
    --type "conference" \
    --industry "technology" \
    --description "A tech conference" \
    --location "San Francisco, CA"
```

The system will automatically:
1. Search Eventbrite for tech events
2. Search Meetup for tech meetups in San Francisco
3. Combine and deduplicate results
4. Identify sponsors from all sources

### Advanced Filtering

Use date filters to find recent events:

```bash
python main.py discover \
    --name "Python Meetup" \
    --type "meetup" \
    --industry "python programming" \
    --description "Python developers" \
    --location "New York, NY" \
    --start-date "2024-06-01" \
    --end-date "2024-12-31"
```

### Location-Based Discovery

Search for events in specific locations:

```bash
# City and state
python main.py discover --location "Austin, TX" ...

# Just city
python main.py discover --location "Seattle" ...

# Country
python main.py discover --location "London, UK" ...
```

## Python API Usage

### Basic Search

```python
from src.services import EventDiscoveryService
from datetime import datetime

# Initialize with both Eventbrite and Meetup
service = EventDiscoveryService(
    eventbrite_api_key="your_eventbrite_key",
    meetup_access_token="your_meetup_token"
)

# Search for events
events = service.discover_similar_events(
    event_type="conference",
    industry="python",
    description="Python conference",
    location="Seattle, WA",
    start_date=datetime(2024, 6, 1),
    max_results=30
)

print(f"Found {len(events)} events from Eventbrite, Meetup, and other sources")
```

### Meetup-Only Search

```python
from src.services.event_discovery import MeetupApiClient
from datetime import datetime

# Direct Meetup API usage
client = MeetupApiClient(access_token="your_token")

# Natural language search
events = client.search_events(
    query="Python meetups near San Francisco this month",
    max_results=20
)

# Structured search
events = client.search_events(
    query="data science",
    location="Boston, MA",
    start_date=datetime.now(),
    radius=10,  # 10 miles
    max_results=50
)
```

### Processing Results

```python
for event in events:
    print(f"\n{event['name']}")
    print(f"  When: {event['datetime'].strftime('%Y-%m-%d %H:%M')}")
    print(f"  Where: {event['location']}")
    print(f"  Online: {'Yes' if event['is_online'] else 'No'}")
    print(f"  RSVPs: {event['rsvp_count']}")

    if event['is_free']:
        print(f"  Cost: Free")
    else:
        print(f"  Cost: {event['fee_amount']} {event['fee_currency']}")

    print(f"  Group: {event['group_name']}")
    print(f"  Link: {event['link']}")
```

## Architecture Details

### MeetupApiClient Class

Location: `src/services/event_discovery.py`

**Key Methods:**
- `search_events()` - Main search function with natural language support
- `_extract_query_parameters()` - Extracts structured params from natural language
- `_parse_event()` - Converts Meetup API response to standardized format

**Authentication:**
- Uses OAuth2 Bearer token authentication
- Token passed via `Authorization: Bearer {token}` header

**API Endpoint:**
- Base URL: `https://api.meetup.com`
- Primary endpoint: `GET /find/upcoming_events`

### Integration with EventDiscoveryService

The `EventDiscoveryService` coordinates all event sources:

```python
def discover_similar_events(self, ...):
    events = []

    # Tier 1: Eventbrite
    if self.eventbrite_client:
        events.extend(self._search_eventbrite_enhanced(...))

    # Tier 2: Meetup (NEW!)
    if len(events) < max_results and self.meetup_client:
        events.extend(self._search_meetup(...))

    # Tier 3: Apify
    if len(events) < max_results and self.apify_scraper:
        events.extend(self.apify_scraper.scrape_events(...))

    # Tier 4: Sample data
    if len(events) < max_results:
        events.extend(self._generate_sample_events(...))

    return events
```

## Benefits of Integration

### 1. Comprehensive Event Coverage

- **Eventbrite**: Professional conferences, large events, paid events
- **Meetup**: Community meetups, local groups, free events
- **Combined**: Maximum sponsor discovery opportunities

### 2. Improved Sponsor Discovery

By including Meetup events, you can discover:
- Local community sponsors
- Grassroots tech companies
- Early-stage startups
- Community-focused organizations

### 3. Natural Language Search

The Meetup integration brings intelligent query parsing:
- "Python meetups in SF" → Automatically extracts location and topic
- "remote data science events" → Filters for online events
- "JavaScript workshops near me" → Location-based search

### 4. Flexible Configuration

All APIs are optional:
- No APIs → Sample data only
- Eventbrite only → Professional events
- Meetup only → Community events
- Both → Maximum coverage
- All three (+ Apify) → Ultimate discovery power

## Troubleshooting

### "Meetup API error: Unauthorized"

**Problem**: Invalid or expired access token

**Solution**:
1. Check that `MEETUP_ACCESS_TOKEN` is set in `.env`
2. Verify the token is valid (not expired)
3. Regenerate OAuth token if needed
4. Ensure token has required scopes

### "No Meetup events found"

**Problem**: Query too specific or location not recognized

**Solution**:
1. Broaden your search query
2. Use more common location names (e.g., "San Francisco" not "SF")
3. Remove date filters to see if events exist
4. Check Meetup.com directly to verify events in that location

### "MeetupApiClient not initialized"

**Problem**: Access token not provided

**Solution**:
1. Set `MEETUP_ACCESS_TOKEN` in your `.env` file
2. Restart the application to reload environment variables
3. Verify the token is correct with `python main.py config`

## Comparison: Eventbrite vs Meetup

| Feature | Eventbrite | Meetup |
|---------|-----------|--------|
| Event Type | Professional conferences, large events | Community meetups, local groups |
| Price | Often paid events | Often free |
| Size | Small to very large | Small to medium |
| Category Filtering | ✓ Advanced categories | ✗ Basic keywords |
| Natural Language | ✗ Structured only | ✓ Intelligent parsing |
| Location Search | ✓ GPS + address | ✓ City/state/country |
| Date Filtering | ✓ Start and end dates | ✓ Start date |
| Online Events | ✓ Supported | ✓ Auto-detected |
| Free/Paid Filter | ✓ Explicit filter | ✗ Mixed results |

**Recommendation**: Use both APIs together for comprehensive event and sponsor discovery!

## Future Enhancements

Potential improvements to the Meetup integration:

1. **OAuth Flow UI** - Add web-based OAuth flow for easier token generation
2. **Group Search** - Search for Meetup groups by topic
3. **Event Recommendations** - AI-powered event suggestions using Claude
4. **RSVP Data** - Track RSVP trends to identify popular topics
5. **Organizer Profiles** - Extract organizer info for direct outreach
6. **Recurring Events** - Handle event series and recurring meetups
7. **Category Mapping** - Map Eventbrite categories to Meetup topics

## Additional Resources

- [Meetup API Documentation](https://www.meetup.com/api/)
- [OAuth Authentication Guide](https://www.meetup.com/api/authentication/)
- [Original MCP Meetup Server](https://github.com/d4nshields/mcp-meetup)
- [Eventbrite MCP Integration](./EVENTBRITE_MCP_INTEGRATION.md)
- [Apify Integration](./APIFY_INTEGRATION.md)

## Support

For issues or questions about the Meetup integration:

1. Check this documentation first
2. Verify your configuration with `python main.py config`
3. Review the [Meetup API documentation](https://www.meetup.com/api/)
4. Check the application logs for detailed error messages
5. Ensure your access token has the required OAuth scopes

---

**Note**: The Meetup API requires OAuth2 authentication. Make sure you have a valid access token before using this integration. See the Setup section for details.
