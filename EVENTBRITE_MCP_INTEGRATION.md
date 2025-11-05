# Eventbrite MCP Integration

This document explains the Eventbrite Model Context Protocol (MCP) integration in the Source Sponsors project.

## Overview

The project now includes full Eventbrite MCP capabilities, providing advanced event discovery features matching the functionality of the `@ibraheem4/eventbrite-mcp` NPM package.

## What is Eventbrite MCP?

The Eventbrite MCP (Model Context Protocol) is a server that provides standardized tools for interacting with the Eventbrite API. It was originally created as a Node.js package to enable AI assistants to search for events, get event details, retrieve venue information, and more.

## Integration Approach

Rather than depending on the deprecated Node.js MCP package, we implemented the same capabilities directly in Python with our own `EventbriteApiClient` class. This provides:

1. **Zero external dependencies** - No Node.js runtime required
2. **Native Python integration** - Works seamlessly with the rest of the codebase
3. **Enhanced control** - Direct access to all Eventbrite API features
4. **Better maintainability** - Single language stack

## Features Implemented

### 1. Enhanced Event Search

The `EventbriteApiClient` now supports all MCP search capabilities:

```python
from src.services import EventDiscoveryService

service = EventDiscoveryService(eventbrite_api_key="your_key")

# Search with advanced filters
events = service.discover_similar_events(
    event_type="conference",
    industry="technology",
    description="AI and ML conference",
    location="San Francisco, CA",
    categories=["102", "113"],  # Science & Tech, Business
    start_date=datetime(2024, 6, 1),
    end_date=datetime(2024, 12, 31),
    price="paid",  # or "free"
    max_results=20
)
```

**Supported Parameters:**
- `query` - Search query string
- `location_latitude` / `location_longitude` - GPS coordinates
- `location_within` - Distance radius (e.g., "10km", "10mi")
- `location_address` - Address string
- `categories` - List of Eventbrite category IDs
- `start_date` / `end_date` - ISO format date strings
- `price` - Filter by "free" or "paid" events
- `page` / `page_size` - Pagination support

### 2. Event Details Retrieval

Get detailed information about a specific event:

```python
event = service.get_event_details("event_id_here")
```

### 3. Category Listing

Retrieve all available Eventbrite categories:

```python
categories = service.get_categories()
for cat in categories:
    print(f"{cat['id']}: {cat['name']}")
```

### 4. Venue Information

The API client includes venue lookup capabilities:

```python
from src.services.event_discovery import EventbriteApiClient

client = EventbriteApiClient(api_key="your_key")
venue = client.get_venue("venue_id_here")
```

## CLI Commands

The integration adds new CLI commands:

### List Categories

```bash
python main.py categories
```

Shows all available Eventbrite category IDs and names.

### Get Event Details

```bash
python main.py event-details EVENT_ID
```

Retrieves detailed information about a specific event.

### Enhanced Discover

```bash
python main.py discover \
  --name "Your Event" \
  --type "conference" \
  --industry "technology" \
  --description "Event description" \
  --categories "102,113" \
  --start-date "2024-06-01" \
  --end-date "2024-12-31" \
  --price "paid" \
  --location "San Francisco, CA"
```

## API Structure

### EventbriteApiClient

Located in: `src/services/event_discovery.py`

**Methods:**
- `search_events(...)` - Advanced event search with all filters
- `get_event(event_id)` - Get event details
- `get_venue(venue_id)` - Get venue details
- `get_categories()` - List all categories

### EventDiscoveryService

High-level service that uses `EventbriteApiClient`:

**Methods:**
- `discover_similar_events(...)` - Main discovery method
- `get_event_details(event_id)` - Wrapper for event retrieval
- `get_categories()` - Wrapper for category listing

## Common Eventbrite Category IDs

Here are some commonly used category IDs:

- `102` - Science & Technology
- `103` - Music
- `105` - Performing & Visual Arts
- `108` - Sports & Fitness
- `110` - Travel & Outdoor
- `113` - Business & Professional
- `115` - Food & Drink
- `116` - Health & Wellness

Use the `python main.py categories` command to see the complete list.

## Configuration

Set your Eventbrite API key in the `.env` file:

```
EVENTBRITE_API_KEY=your_eventbrite_api_key_here
```

Get your API key from: https://www.eventbrite.com/platform/api

## Comparison with Original MCP

| Feature | Original Node.js MCP | Our Python Integration |
|---------|---------------------|----------------------|
| Language | Node.js | Python |
| Installation | npm package | Built-in |
| Dependencies | @modelcontextprotocol/sdk, axios | requests (already required) |
| Status | Deprecated | Active, maintained |
| Event Search | ✓ | ✓ |
| Event Details | ✓ | ✓ |
| Venue Lookup | ✓ | ✓ |
| Categories | ✓ | ✓ |
| CLI Integration | Requires separate setup | Built-in commands |
| Python API | ✗ | ✓ |

## Example Use Cases

### 1. Find Tech Conferences in Specific Location

```bash
python main.py discover \
  --name "My Tech Event" \
  --type "conference" \
  --industry "technology" \
  --description "Technology conference" \
  --categories "102" \
  --location "San Francisco, CA" \
  --price "paid"
```

### 2. Find Free Networking Events

```bash
python main.py discover \
  --name "Networking Meetup" \
  --type "meetup" \
  --industry "business" \
  --description "Professional networking" \
  --price "free" \
  --start-date "2024-06-01"
```

### 3. Research Event Details

```bash
# First, find events to get their IDs
python main.py discover --name "Event" --type "conference" --industry "tech" --description "Tech"

# Then get details about a specific event
python main.py event-details 123456789
```

## Error Handling

The integration includes robust error handling:

- **Missing API Key**: Clear error message with setup instructions
- **Invalid Category IDs**: API returns error, falls back to sample data
- **Network Issues**: Graceful fallback to web scraping/sample data
- **Invalid Event IDs**: Returns None with logged error

## Future Enhancements

Potential improvements to the integration:

1. **Caching**: Cache category lists to reduce API calls
2. **Pagination**: Implement automatic pagination for large result sets
3. **Rate Limiting**: Add built-in rate limiting to respect API limits
4. **Batch Operations**: Support batch event detail retrieval
5. **Geographic Search**: Enhanced location-based search with radius

## References

- Original Eventbrite MCP: https://github.com/ibraheem4/eventbrite-mcp
- Eventbrite API Docs: https://www.eventbrite.com/platform/api
- Model Context Protocol: https://modelcontextprotocol.io/

## Support

For issues related to the Eventbrite integration:

1. Check your API key configuration
2. Verify API key has proper permissions
3. Check Eventbrite API status
4. Review error logs for specific error messages

For general Source Sponsors issues, see the main README.md file.
