# Source Sponsors - Automated Sponsor Outreach Workflow

An intelligent tool that automates the process of finding potential event sponsors and generating personalized outreach emails.

**✨ Enhanced with Dual Integration:**
- **Eventbrite MCP** - Full Model Context Protocol capabilities for advanced event discovery
- **Apify Platform** - Powerful web scraping for comprehensive event and sponsor extraction

## Features

- **🔍 Three-Tier Event Discovery System**:
  1. **Eventbrite API** (Primary) - Official API with MCP capabilities
     - Category-based filtering
     - Location search (latitude/longitude or address)
     - Date range filtering
     - Free/paid event filtering
     - Event details retrieval by ID
     - Venue information lookup
  2. **Apify Scraper** (Secondary) - Advanced web scraping
     - Extracts events not in API results
     - Comprehensive event details
     - Enhanced sponsor detection
  3. **Sample Data** (Fallback) - Demonstration mode
- **🎯 Sponsor Identification**: Multi-source sponsor extraction from event pages
- **📧 Contact Discovery**: Finds email addresses and contact information for sponsors
- **✍️ Email Generation**: Creates personalized outreach emails (template-based or AI-powered)
- **📊 Export Options**: Exports to CSV, Excel, or individual email template files
- **📈 Analytics**: Provides statistics on sponsor tiers, industries, and coverage

## Workflow Overview

```
1. Event Description Input
   ↓
2. Three-Tier Event Discovery
   - Eventbrite API (MCP-enhanced)
   - Apify Web Scraping
   - Sample Data Fallback
   ↓
3. Multi-Source Sponsor Identification
   - Standard web scraping
   - Apify-powered extraction
   - Pattern matching
   ↓
4. Contact Information Gathering (Email patterns + Website scraping)
   ↓
5. Personalized Email Generation (Templates or AI)
   ↓
6. Export to CSV/Excel + Email Templates
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone or download this repository**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv

   # On Linux/Mac:
   source venv/bin/activate

   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API keys** (optional but recommended):
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API keys:
   - `EVENTBRITE_API_KEY`: For official API access (get it from https://www.eventbrite.com/platform/)
   - `APIFY_API_TOKEN`: For enhanced web scraping (get it from https://console.apify.com/account/integrations)
   - `OPENAI_API_KEY`: For AI-powered email generation (optional, will use templates if not provided)

   **Note**: All APIs are optional. The tool works with any combination:
   - No APIs = Sample data only (demonstration mode)
   - Eventbrite only = Official events
   - Apify only = Scraped events
   - Both = Maximum coverage and best results

5. **Install Playwright browsers** (optional - for future enhancements):
   ```bash
   playwright install
   ```

## Usage

### Basic Command

```bash
python main.py discover \
  --name "Tech Innovation Summit 2024" \
  --type "conference" \
  --industry "technology" \
  --description "A premier technology conference for industry leaders" \
  --location "San Francisco, CA" \
  --audience 500
```

### Interactive Mode

Simply run without all options to use interactive prompts:

```bash
python main.py discover
```

You'll be prompted to enter:
- Event name
- Event type (conference, workshop, meetup, etc.)
- Industry/category
- Brief description

### Full Options

```bash
python main.py discover \
  --name "Your Event Name" \
  --type "conference" \
  --industry "technology" \
  --description "Event description" \
  --date "2024-06-15" \
  --location "San Francisco, CA" \
  --audience 500 \
  --max-events 20 \
  --output-format both \
  --export-templates
```

**Options:**
- `--name`: Name of your event (required)
- `--type`: Event type - conference, workshop, meetup, etc. (required)
- `--industry`: Industry or category - tech, healthcare, finance, etc. (required)
- `--description`: Brief event description (required)
- `--date`: Event date in YYYY-MM-DD format (optional)
- `--location`: Event location (optional)
- `--audience`: Expected audience size (optional)
- `--max-events`: Maximum similar events to search (default: 20)
- `--categories`: Eventbrite category IDs, comma-separated (optional)
- `--start-date`: Search events from this date, YYYY-MM-DD (optional)
- `--end-date`: Search events until this date, YYYY-MM-DD (optional)
- `--price`: Filter by 'free' or 'paid' events (optional)
- `--output-format`: Output format - csv, excel, or both (default: both)
- `--export-templates`: Export individual email template text files

### Enhanced MCP Features

**List Eventbrite Categories:**
```bash
python main.py categories
```
Shows all available Eventbrite category IDs and names. Use these with `--categories` option.

**Get Event Details:**
```bash
python main.py event-details EVENT_ID
```
Retrieves detailed information about a specific Eventbrite event by ID.

**Advanced Search Example:**
```bash
python main.py discover \
  --name "AI Conference 2024" \
  --type "conference" \
  --industry "technology" \
  --description "Artificial Intelligence conference" \
  --categories "102,113" \
  --start-date "2024-06-01" \
  --end-date "2024-12-31" \
  --price "paid" \
  --location "San Francisco, CA"
```

### Check Configuration

```bash
python main.py config
```

This shows your current API key configuration status.

## Output

The tool generates several output files in the `output/` directory:

### CSV Format (`sponsors_TIMESTAMP.csv`)
A single CSV file with all sponsor data and email drafts:
- Company information
- Contact emails
- Previous sponsorships
- Personalized email subject and body
- Alternative subject lines

### Excel Format (`sponsors_TIMESTAMP.xlsx`)
A multi-sheet Excel workbook with:
1. **Event Details**: Your event information
2. **Sponsors**: Complete sponsor database
3. **Email Drafts**: Ready-to-send email templates
4. **Statistics**: Analytics on sponsor coverage, tiers, industries

### Email Templates (optional)
Individual text files for each sponsor with:
- Primary subject line
- Email body
- Alternative subject line variations

## Example Output

```
📊 Summary:
   - Similar events analyzed: 15
   - Sponsors identified: 47
   - Emails generated: 47
   - Output files: 2

📁 Output files:
   - output/sponsors_20240315_143022.csv
   - output/sponsors_20240315_143022.xlsx
```

## How It Works

### 1. Event Discovery
- Uses Eventbrite API to find similar events based on keywords
- Falls back to web scraping for additional sources
- Filters by event type, industry, and location

### 2. Sponsor Identification
- Scrapes event pages for sponsor sections
- Identifies sponsor logos and company names
- Categorizes by sponsorship tier (platinum, gold, silver, etc.)
- Extracts company websites

### 3. Contact Finding
- Scrapes company websites for email addresses
- Generates common email variants (sponsorships@, partnerships@, events@)
- Validates email format
- Creates LinkedIn company page URLs

### 4. Email Generation
- **Template Mode** (default): Uses professionally crafted templates with personalization
- **AI Mode** (with OpenAI API): Generates unique, contextually relevant emails
- Creates multiple subject line variations
- References sponsor's previous event sponsorships
- Highlights fit between event and sponsor

### 5. Data Export
- Structured CSV for easy import into CRM or mail merge tools
- Excel workbook with multiple sheets for analysis
- Individual email templates for manual sending
- Statistics dashboard for tracking coverage

## Tips for Best Results

1. **Be Specific**: Provide detailed event descriptions to find better matches
2. **Use Eventbrite API**: Set up an API key for more accurate event discovery
3. **Review Before Sending**: Always review and customize the generated emails
4. **Check Email Validity**: Verify contact emails before bulk sending
5. **Respect Privacy**: Use contact information responsibly and comply with anti-spam laws
6. **Follow Up**: Track responses and follow up appropriately

## API Keys

### Eventbrite API (Recommended)
1. Go to https://www.eventbrite.com/platform/
2. Sign up for a developer account
3. Create an app and get your API key
4. Add to `.env` file: `EVENTBRITE_API_KEY=your_key_here`

**Benefits:**
- More accurate event discovery
- Access to structured event data
- Better filtering options

### OpenAI API (Optional)
1. Go to https://platform.openai.com/
2. Create an account and get an API key
3. Add to `.env` file: `OPENAI_API_KEY=your_key_here`

**Benefits:**
- More personalized, contextual emails
- Better variation in messaging
- Adapts tone to different industries

**Note:** The tool works without these APIs using templates and sample data.

## Advanced Usage

### Custom Event List

If you already have a list of events to analyze:

1. Create a Python script:
```python
from src.models import Event
from src.services import SponsorIdentificationService

events = [
    Event(
        name="Tech Summit 2024",
        event_type="conference",
        industry="technology",
        description="...",
        url="https://example.com/event"
    )
]

sponsor_service = SponsorIdentificationService()
sponsors = sponsor_service.identify_sponsors(events)
```

### Integrate with CRM

Export CSV can be imported into most CRM systems:
- Salesforce
- HubSpot
- Pipedrive
- Zoho CRM

Use the "Primary Email" column for contact information.

## Troubleshooting

### No events found
- Check your Eventbrite API key configuration
- Try broader search terms
- The tool will work with sample data for demonstration

### No sponsors extracted
- Event pages may have anti-scraping measures
- Try adding a delay or using Playwright
- Manually verify the event URLs are accessible

### Email generation failed
- Check OpenAI API key if using AI mode
- Falls back to template mode automatically
- Templates work without any API keys

### Import errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Activate your virtual environment
- Check Python version (3.8+ required)

## Project Structure

```
source-sponsors/
├── main.py                 # CLI entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment variables
├── README.md              # This file
├── src/
│   ├── models/            # Data models (Event, Sponsor)
│   ├── services/          # Core services
│   │   ├── event_discovery.py
│   │   ├── sponsor_identification.py
│   │   ├── contact_finder.py
│   │   ├── email_generator.py
│   │   └── export_service.py
│   └── utils/             # Utility functions
│       ├── email_utils.py
│       └── logger.py
├── output/                # Generated output files
└── examples/              # Example files
```

## Contributing

Contributions are welcome! Areas for improvement:
- Additional event discovery sources
- Better sponsor extraction algorithms
- More email template variations
- Integration with email sending services
- CRM integrations

## License

This project is provided as-is for educational and commercial use.

## Disclaimer

This tool is designed for legitimate business outreach. Users are responsible for:
- Complying with anti-spam laws (CAN-SPAM, GDPR, etc.)
- Respecting website terms of service
- Obtaining proper consent for email communication
- Using contact information ethically

Always personalize and review automated emails before sending.

## Support

For issues, questions, or feature requests, please open an issue in the repository.

## Version

Current version: 1.0.0

---

**Happy Sponsoring! 🎉**
