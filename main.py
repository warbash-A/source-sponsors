#!/usr/bin/env python3
"""
Source Sponsors - Automated Sponsor Outreach Workflow
Main CLI interface
"""

import os
import sys
import click
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.models import Event
from src.services import (
    EventDiscoveryService,
    SponsorIdentificationService,
    ContactFinderService,
    EmailGeneratorService
)
from src.services.export_service import ExportService
from src.utils.logger import setup_logger

logger = setup_logger()


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Source Sponsors - Automated Sponsor Outreach Workflow

    Discover potential sponsors and generate personalized outreach emails.
    """
    pass


@cli.command()
@click.option('--name', prompt='Event name', help='Name of your event')
@click.option('--type', 'event_type', prompt='Event type (e.g., conference, workshop, meetup)',
              help='Type of event')
@click.option('--industry', prompt='Industry/category', help='Industry or category')
@click.option('--description', prompt='Brief description', help='Brief event description')
@click.option('--date', help='Event date (YYYY-MM-DD)', default=None)
@click.option('--location', help='Event location', default=None)
@click.option('--audience', 'audience_size', type=int, help='Expected audience size', default=None)
@click.option('--max-events', type=int, default=20, help='Max similar events to search')
@click.option('--categories', help='Eventbrite category IDs (comma-separated)', default=None)
@click.option('--start-date', help='Search events from this date (YYYY-MM-DD)', default=None)
@click.option('--end-date', help='Search events until this date (YYYY-MM-DD)', default=None)
@click.option('--price', type=click.Choice(['free', 'paid']), help='Filter by free or paid events', default=None)
@click.option('--output-format', type=click.Choice(['csv', 'excel', 'both']), default='both',
              help='Output format')
@click.option('--export-templates', is_flag=True, help='Export individual email template files')
def discover(name, event_type, industry, description, date, location, audience_size,
             max_events, categories, start_date, end_date, price, output_format, export_templates):
    """Discover sponsors and generate outreach emails for your event.

    Enhanced with Eventbrite MCP capabilities including:
    - Advanced category filtering
    - Date range searches
    - Free/paid event filtering
    - Location-based discovery
    """

    logger.info("🚀 Starting Source Sponsors workflow")
    logger.info("="*60)

    # Parse date if provided
    event_date = None
    if date:
        try:
            event_date = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            logger.error("Invalid date format. Use YYYY-MM-DD")
            sys.exit(1)

    # Parse search date filters
    search_start_date = None
    if start_date:
        try:
            search_start_date = datetime.strptime(start_date, '%Y-%m-%d')
        except ValueError:
            logger.error("Invalid start-date format. Use YYYY-MM-DD")
            sys.exit(1)

    search_end_date = None
    if end_date:
        try:
            search_end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            logger.error("Invalid end-date format. Use YYYY-MM-DD")
            sys.exit(1)

    # Parse categories if provided
    category_list = None
    if categories:
        category_list = [c.strip() for c in categories.split(',')]

    # Create event object
    event = Event(
        name=name,
        event_type=event_type,
        industry=industry,
        description=description,
        date=event_date,
        location=location,
        audience_size=audience_size
    )

    logger.info(f"Event: {event.name}")
    logger.info(f"Type: {event.event_type} | Industry: {event.industry}")
    if category_list:
        logger.info(f"Categories: {', '.join(category_list)}")
    if price:
        logger.info(f"Price filter: {price}")
    logger.info("="*60)

    # Step 1: Discover similar events
    logger.info("\n📅 Step 1: Discovering similar events...")
    discovery_service = EventDiscoveryService()
    similar_events = discovery_service.discover_similar_events(
        event_type=event.event_type,
        industry=event.industry,
        description=event.description,
        location=event.location,
        categories=category_list,
        start_date=search_start_date,
        end_date=search_end_date,
        price=price,
        max_results=max_events
    )

    if not similar_events:
        logger.warning("No similar events found. The tool will still work with sample data.")
    else:
        logger.info(f"✓ Found {len(similar_events)} similar events")

    # Step 2: Identify sponsors
    logger.info("\n🎯 Step 2: Identifying sponsors from events...")
    # Pass Apify scraper to sponsor service if available
    sponsor_service = SponsorIdentificationService(
        apify_scraper=discovery_service.apify_scraper
    )
    sponsors = sponsor_service.identify_sponsors(similar_events)

    if not sponsors:
        logger.error("No sponsors found. Please check the event URLs or try different search parameters.")
        sys.exit(1)

    logger.info(f"✓ Identified {len(sponsors)} unique sponsors")

    # Step 3: Find contact information
    logger.info("\n📧 Step 3: Finding contact information...")
    contact_service = ContactFinderService()
    sponsors = contact_service.enrich_sponsors_with_contacts(sponsors)

    sponsors_with_emails = sum(1 for s in sponsors.values() if s.contact_emails)
    logger.info(f"✓ Found contact info for {sponsors_with_emails}/{len(sponsors)} sponsors")

    # Step 4: Generate personalized emails
    logger.info("\n✍️  Step 4: Generating personalized emails...")
    email_service = EmailGeneratorService()
    emails = email_service.generate_emails(event, sponsors)
    logger.info(f"✓ Generated {len(emails)} personalized emails")

    # Step 5: Export results
    logger.info("\n💾 Step 5: Exporting results...")
    export_service = ExportService()

    output_files = []

    if output_format in ['csv', 'both']:
        csv_file = export_service.export_to_csv(event, sponsors, emails)
        output_files.append(csv_file)
        logger.info(f"✓ CSV exported: {csv_file}")

    if output_format in ['excel', 'both']:
        excel_file = export_service.export_to_excel(event, sponsors, emails)
        output_files.append(excel_file)
        logger.info(f"✓ Excel exported: {excel_file}")

    if export_templates:
        template_folder = export_service.export_email_templates(emails)
        logger.info(f"✓ Email templates exported: {template_folder}")

    # Summary
    logger.info("\n" + "="*60)
    logger.info("✅ Workflow completed successfully!")
    logger.info("="*60)
    logger.info(f"📊 Summary:")
    logger.info(f"   - Similar events analyzed: {len(similar_events)}")
    logger.info(f"   - Sponsors identified: {len(sponsors)}")
    logger.info(f"   - Emails generated: {len(emails)}")
    logger.info(f"   - Output files: {len(output_files)}")
    logger.info("\n📁 Output files:")
    for file in output_files:
        logger.info(f"   - {file}")
    logger.info("")


@cli.command()
@click.option('--file', 'input_file', required=True, help='Input CSV/Excel file with sponsor data')
@click.option('--name', prompt='Event name', help='Name of your event')
@click.option('--type', 'event_type', prompt='Event type', help='Type of event')
@click.option('--industry', prompt='Industry', help='Industry or category')
@click.option('--description', prompt='Brief description', help='Brief event description')
def generate_emails(input_file, name, event_type, industry, description):
    """Generate emails from existing sponsor list (CSV/Excel)."""

    logger.info("📧 Generating emails from sponsor list")

    if not os.path.exists(input_file):
        logger.error(f"File not found: {input_file}")
        sys.exit(1)

    # Create event object
    event = Event(
        name=name,
        event_type=event_type,
        industry=industry,
        description=description
    )

    # Load sponsors from file
    # (Implementation would read CSV/Excel and create Sponsor objects)
    logger.info("This feature is not yet implemented in this version.")
    logger.info("Use the 'discover' command for the full workflow.")


@cli.command()
def config():
    """Show current configuration and API key status."""

    logger.info("Configuration Status:")
    logger.info("="*60)

    eventbrite_key = os.getenv('EVENTBRITE_API_KEY')
    apify_token = os.getenv('APIFY_API_TOKEN')
    openai_key = os.getenv('OPENAI_API_KEY')

    logger.info(f"Eventbrite API Key: {'✓ Configured' if eventbrite_key else '✗ Not configured'}")
    logger.info(f"Apify API Token: {'✓ Configured' if apify_token else '✗ Not configured (will use sample data)'}")
    logger.info(f"OpenAI API Key: {'✓ Configured' if openai_key else '✗ Not configured (using templates)'}")

    logger.info("\nTo configure API keys:")
    logger.info("1. Copy .env.example to .env")
    logger.info("2. Add your API keys to the .env file")
    logger.info("\nGet API keys from:")
    logger.info("  - Eventbrite: https://www.eventbrite.com/platform/api")
    logger.info("  - Apify: https://console.apify.com/account/integrations")
    logger.info("  - OpenAI (optional): https://platform.openai.com/api-keys")
    logger.info("\nNote: OpenAI is optional - template-based emails will be used if not configured")


@cli.command()
def categories():
    """List all available Eventbrite event categories."""

    logger.info("📋 Fetching Eventbrite Categories...")
    logger.info("="*60)

    discovery_service = EventDiscoveryService()

    if not discovery_service.eventbrite_client:
        logger.error("Eventbrite API key not configured!")
        logger.info("\nTo configure:")
        logger.info("1. Get API key from https://www.eventbrite.com/platform/api")
        logger.info("2. Add to .env file: EVENTBRITE_API_KEY=your_key_here")
        sys.exit(1)

    categories = discovery_service.get_categories()

    if not categories:
        logger.warning("No categories found")
        return

    logger.info(f"\nFound {len(categories)} categories:\n")

    for cat in categories:
        cat_id = cat.get('id', 'N/A')
        name = cat.get('name', 'Unknown')
        logger.info(f"  [{cat_id}] {name}")

    logger.info(f"\n💡 Use category IDs with --categories option in discover command")
    logger.info("="*60)


@cli.command()
@click.argument('event_id')
def event_details(event_id):
    """Get detailed information about a specific Eventbrite event."""

    logger.info(f"📅 Fetching Event Details for ID: {event_id}")
    logger.info("="*60)

    discovery_service = EventDiscoveryService()

    if not discovery_service.eventbrite_client:
        logger.error("Eventbrite API key not configured!")
        logger.info("\nTo configure:")
        logger.info("1. Get API key from https://www.eventbrite.com/platform/api")
        logger.info("2. Add to .env file: EVENTBRITE_API_KEY=your_key_here")
        sys.exit(1)

    event = discovery_service.get_event_details(event_id)

    if not event:
        logger.error(f"Event {event_id} not found")
        sys.exit(1)

    logger.info(f"\n✓ Event Found:\n")
    logger.info(f"  Name: {event.name}")
    logger.info(f"  Type: {event.event_type}")
    logger.info(f"  Date: {event.date.strftime('%Y-%m-%d %H:%M') if event.date else 'TBD'}")
    logger.info(f"  Location: {event.location}")
    logger.info(f"  URL: {event.url}")
    logger.info(f"\n  Description:")
    logger.info(f"  {event.description[:200]}...")
    logger.info("="*60)


if __name__ == '__main__':
    cli()
