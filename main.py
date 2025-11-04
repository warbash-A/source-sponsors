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
@click.option('--output-format', type=click.Choice(['csv', 'excel', 'both']), default='both',
              help='Output format')
@click.option('--export-templates', is_flag=True, help='Export individual email template files')
def discover(name, event_type, industry, description, date, location, audience_size,
             max_events, output_format, export_templates):
    """Discover sponsors and generate outreach emails for your event."""

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
    logger.info("="*60)

    # Step 1: Discover similar events
    logger.info("\n📅 Step 1: Discovering similar events...")
    discovery_service = EventDiscoveryService()
    similar_events = discovery_service.discover_similar_events(
        event_type=event.event_type,
        industry=event.industry,
        description=event.description,
        location=event.location,
        max_results=max_events
    )

    if not similar_events:
        logger.warning("No similar events found. The tool will still work with sample data.")
    else:
        logger.info(f"✓ Found {len(similar_events)} similar events")

    # Step 2: Identify sponsors
    logger.info("\n🎯 Step 2: Identifying sponsors from events...")
    sponsor_service = SponsorIdentificationService()
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
    openai_key = os.getenv('OPENAI_API_KEY')

    logger.info(f"Eventbrite API Key: {'✓ Configured' if eventbrite_key else '✗ Not configured'}")
    logger.info(f"OpenAI API Key: {'✓ Configured' if openai_key else '✗ Not configured (using templates)'}")

    logger.info("\nTo configure API keys:")
    logger.info("1. Copy .env.example to .env")
    logger.info("2. Add your API keys to the .env file")
    logger.info("\nNote: OpenAI is optional - template-based emails will be used if not configured")


if __name__ == '__main__':
    cli()
