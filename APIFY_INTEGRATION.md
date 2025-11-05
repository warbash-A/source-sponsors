# Apify Eventbrite Scraper Integration

This document explains the Apify platform integration for enhanced Eventbrite event and sponsor discovery in the Source Sponsors project.

## Overview

The project now includes integration with the Apify platform, specifically using the `newpo/eventbrite-scraper` actor for advanced web scraping capabilities. This provides a powerful alternative and complement to the Eventbrite API, enabling comprehensive event discovery and sponsor extraction.

## What is Apify?

[Apify](https://apify.com/) is a web scraping and automation platform that provides ready-made "actors" (scrapers) for various websites. The EventBrite Scraper actor extracts structured data from Eventbrite including:

- Event details (name, description, dates)
- Organizer information
- Venue details
- Pricing information
- Potential sponsor mentions

## Integration Architecture

### Three-Tier Discovery System

The project now uses a sophisticated three-tier approach for event discovery:

```
1. Eventbrite API (Primary)
   - Official API with structured data
   - Advanced filtering (categories, dates, price)
   - Rate-limited but reliable
   ↓
2. Apify Scraper (Secondary)
   - Web scraping for additional events
   - Extracts data not available via API
   - Can scrape specific event pages
   ↓
3. Sample Data (Fallback)
   - Demonstrates functionality
   - Used when APIs unavailable
```

## Features

### 1. Enhanced Event Discovery

The `ApifyEventbriteScraperService` automatically scrapes Eventbrite when:
- Eventbrite API is not configured
- API results are insufficient
- Additional event details are needed

**Example:**
```python
from src.services import EventDiscoveryService

service = EventDiscoveryService(use_apify=True)

events = service.discover_similar_events(
    event_type="conference",
    industry="technology",
    description="AI conference",
    location="San Francisco, CA",
    max_results=20
)
```

### 2. Sponsor Extraction from Events

The Apify scraper can extract sponsor information from event pages:

```python
from src.services.apify_scraper import ApifyEventbriteScraperService

scraper = ApifyEventbriteScraperService()

# Extract sponsors from scraped events
sponsors = scraper.extract_sponsors_from_events(events)
```

### 3. Event Detail Scraping

Get comprehensive details about specific events:

```python
event_details = scraper.scrape_event_details(
    "https://www.eventbrite.com/e/tech-conference-2024-tickets-123456"
)
```

## Setup

### 1. Get Apify API Token

1. Sign up at [Apify Console](https://console.apify.com/)
2. Navigate to Settings > Integrations
3. Copy your API token

### 2. Configure in Project

Add to `.env` file:
```
APIFY_API_TOKEN=apify_api_xxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 3. Install Dependencies

```bash
pip install apify-client
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### 4. Verify Configuration

```bash
python main.py config
```

Should show:
```
Apify API Token: ✓ Configured
```

## Usage

### Automatic Integration

The Apify scraper is automatically used when configured:

```bash
python main.py discover \
  --name "Tech Summit 2024" \
  --type "conference" \
  --industry "technology" \
  --description "Technology conference" \
  --location "San Francisco, CA"
```

**What happens:**
1. Tries Eventbrite API first (if configured)
2. Falls back to Apify scraper for additional events
3. Extracts sponsors using Apify if standard scraping fails
4. Uses sample data only if both fail

### Disable Apify Programmatically

If you want to disable Apify in code:

```python
from src.services import EventDiscoveryService

# Disable Apify, use only Eventbrite API and fallback
service = EventDiscoveryService(use_apify=False)
```

## How It Works

### Event Scraping Workflow

1. **Build Search URL**
   - Formats location and search query
   - Example: `https://www.eventbrite.com/d/california--san-francisco/tech-events/`

2. **Run Apify Actor**
   - Calls `newpo/eventbrite-scraper` actor
   - Waits for completion
   - Retrieves dataset ID

3. **Parse Results**
   - Iterates through dataset items
   - Parses event fields (name, date, location, etc.)
   - Creates Event objects

4. **Extract Sponsors**
   - Looks for organizer information
   - Scans descriptions for sponsor mentions
   - Extracts explicit sponsor fields if present

### Data Extraction

The scraper extracts and maps the following fields:

| Apify Field | Our Model | Notes |
|-------------|-----------|-------|
| name / title | Event.name | Event name |
| description / summary | Event.description | Truncated to 500 chars |
| start_date / date | Event.date | Multiple format support |
| venue / location | Event.location | City, region, country |
| url / link | Event.url | Event page URL |
| organizer | Potential Sponsor | May be sponsor |

## API Reference

### ApifyEventbriteScraperService

Located in: `src/services/apify_scraper.py`

#### Methods

**`__init__(api_token: Optional[str] = None)`**
- Initialize with API token (or from environment)

**`scrape_events(search_query, location, max_results, category) -> List[Event]`**
- Scrape Eventbrite events based on search criteria
- Returns list of Event objects

**`scrape_event_details(event_url) -> Dict`**
- Get detailed information about a specific event
- Returns raw scraped data dictionary

**`extract_sponsors_from_events(events) -> Dict[str, Sponsor]`**
- Extract sponsors from list of events
- Returns dictionary of sponsor name to Sponsor object

**`is_available() -> bool`**
- Check if Apify client is initialized and ready

## Cost Considerations

### Apify Pricing

Apify charges based on compute units and dataset operations. The `newpo/eventbrite-scraper` actor:

- **Free Tier**: $5 of platform credit per month
- **Compute Units**: Varies based on scraping complexity
- **Storage**: Dataset storage included

**Typical Usage:**
- Scraping 20 events: ~0.01-0.05 compute units
- Estimated cost: $0.01-$0.05 per run
- Free tier covers: ~100-500 runs/month

### Optimization Tips

1. **Cache Results**: Store scraped events to avoid re-scraping
2. **Batch Requests**: Scrape multiple events in one actor run
3. **Set Limits**: Use `max_results` to limit scraping
4. **Monitor Usage**: Check Apify Console for usage stats

## Error Handling

The integration includes comprehensive error handling:

### Common Scenarios

1. **No API Token**
   - Logs warning: "Apify client not initialized"
   - Falls back to sample data
   - No errors thrown

2. **Actor Run Fails**
   - Logs error with details
   - Returns empty list
   - Continues with other methods

3. **Network Issues**
   - Retries handled by Apify client
   - Timeout after reasonable duration
   - Graceful degradation

4. **Parsing Errors**
   - Individual events logged as debug
   - Other events still processed
   - Partial results returned

### Debugging

Enable debug logging:

```python
import logging
logging.getLogger('src.services.apify_scraper').setLevel(logging.DEBUG)
```

Check actor runs in Apify Console:
- https://console.apify.com/actors/runs

## Comparison: API vs Apify

| Feature | Eventbrite API | Apify Scraper |
|---------|----------------|---------------|
| **Authorization** | API key required | API token required |
| **Data Access** | Official, structured | Web scraping |
| **Rate Limits** | Yes (varies by plan) | Based on compute units |
| **Reliability** | Very high | High |
| **Cost** | Free tier available | Pay per use |
| **Event Details** | Structured JSON | Scraped HTML |
| **Sponsor Data** | Limited | More comprehensive |
| **Historical Events** | Limited | Can access archived |
| **Setup Complexity** | Simple | Simple |

## Best Practices

### When to Use Each Method

**Use Eventbrite API for:**
- Real-time event searches
- Category-based filtering
- Official event data
- High-volume queries

**Use Apify Scraper for:**
- Events not in API results
- Detailed sponsor information
- Historical event data
- When API quota exceeded

**Use Both for:**
- Maximum event coverage
- Comprehensive sponsor lists
- Redundancy and reliability

### Configuration Strategy

**Development/Testing:**
```env
# Use Eventbrite API only to save Apify credits
EVENTBRITE_API_KEY=your_key
APIFY_API_TOKEN=  # Leave empty
```

**Production:**
```env
# Use both for best results
EVENTBRITE_API_KEY=your_key
APIFY_API_TOKEN=your_token
```

## Troubleshooting

### Issue: "Apify client not initialized"

**Solution:**
1. Check API token in `.env`
2. Verify `apify-client` is installed
3. Run `python main.py config`

### Issue: Actor run times out

**Solution:**
1. Reduce `max_results` parameter
2. Check Apify platform status
3. Verify actor is not deprecated

### Issue: No sponsors extracted

**Solution:**
1. Event pages may not list sponsors
2. Apify scraper has limitations on sponsor detection
3. Standard web scraping will be attempted
4. Sample sponsors used as fallback

### Issue: High Apify costs

**Solution:**
1. Reduce max_results in queries
2. Cache results locally
3. Use Eventbrite API primarily
4. Monitor usage in Apify Console

## Future Enhancements

Potential improvements:

1. **Custom Actors**: Create optimized sponsor-specific scraper
2. **Caching Layer**: Store scraped data to reduce API calls
3. **Batch Processing**: Process multiple events in parallel
4. **Enhanced Parsing**: Better sponsor detection algorithms
5. **Scheduled Scraping**: Periodic updates of event database

## Resources

- **Apify Platform**: https://apify.com/
- **EventBrite Scraper Actor**: https://apify.com/newpo/eventbrite-scraper
- **Apify Python Client**: https://docs.apify.com/api/client/python/
- **Apify Console**: https://console.apify.com/
- **Support**: https://docs.apify.com/support

## Support

For Apify integration issues:

1. Check Apify Console for actor run logs
2. Verify API token permissions
3. Review actor documentation
4. Check Apify platform status

For Source Sponsors issues:
- See main README.md
- Check integration logs with debug mode
- Review EVENTBRITE_MCP_INTEGRATION.md for API comparison

---

**Version**: 1.0.0
**Last Updated**: 2025
**Actor**: newpo/eventbrite-scraper v1.0+
