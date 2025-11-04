"""
Sample usage of the Source Sponsors library as a Python module.

This demonstrates how to use the tool programmatically instead of via CLI.
"""

from datetime import datetime
from src.models import Event
from src.services import (
    EventDiscoveryService,
    SponsorIdentificationService,
    ContactFinderService,
    EmailGeneratorService
)
from src.services.export_service import ExportService


def main():
    """Run the sponsor discovery workflow programmatically."""

    # Step 1: Define your event
    my_event = Event(
        name="Tech Innovation Summit 2024",
        event_type="conference",
        industry="technology",
        description="A premier technology conference bringing together industry leaders and innovators.",
        date=datetime(2024, 9, 15),
        location="San Francisco, CA",
        audience_size=500
    )

    print(f"Finding sponsors for: {my_event.name}")

    # Step 2: Discover similar events
    discovery_service = EventDiscoveryService()
    similar_events = discovery_service.discover_similar_events(
        event_type=my_event.event_type,
        industry=my_event.industry,
        description=my_event.description,
        location=my_event.location,
        max_results=10
    )
    print(f"Found {len(similar_events)} similar events")

    # Step 3: Identify sponsors from those events
    sponsor_service = SponsorIdentificationService()
    sponsors = sponsor_service.identify_sponsors(similar_events)
    print(f"Identified {len(sponsors)} unique sponsors")

    # Step 4: Enrich with contact information
    contact_service = ContactFinderService()
    sponsors = contact_service.enrich_sponsors_with_contacts(sponsors)
    print(f"Enriched sponsors with contact information")

    # Step 5: Generate personalized emails
    email_service = EmailGeneratorService()
    emails = email_service.generate_emails(my_event, sponsors)
    print(f"Generated {len(emails)} personalized emails")

    # Step 6: Export results
    export_service = ExportService()

    # Export to CSV
    csv_file = export_service.export_to_csv(my_event, sponsors, emails)
    print(f"Exported to: {csv_file}")

    # Export to Excel
    excel_file = export_service.export_to_excel(my_event, sponsors, emails)
    print(f"Exported to: {excel_file}")

    # Export email templates
    templates_folder = export_service.export_email_templates(emails)
    print(f"Email templates: {templates_folder}")

    print("\n✅ Workflow completed successfully!")


if __name__ == "__main__":
    main()
