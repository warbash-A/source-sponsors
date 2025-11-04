"""Service for exporting sponsor data and emails."""

import os
import csv
from datetime import datetime
from typing import Dict
import pandas as pd

from ..models import Event, Sponsor
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class ExportService:
    """Service to export sponsor data and emails to various formats."""

    def __init__(self, output_dir: str = "output"):
        """Initialize the export service."""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def export_to_csv(
        self,
        event: Event,
        sponsors: Dict[str, Sponsor],
        emails: Dict[str, Dict[str, str]],
        filename: str = None
    ) -> str:
        """Export sponsor data and emails to CSV."""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"sponsors_{timestamp}.csv"

        filepath = os.path.join(self.output_dir, filename)

        # Prepare data for CSV
        rows = []
        for company_name, sponsor in sponsors.items():
            email_data = emails.get(company_name, {})

            row = {
                'Company Name': sponsor.company_name,
                'Website': sponsor.website or '',
                'Industry': sponsor.industry or '',
                'Tier': sponsor.tier or '',
                'Primary Email': sponsor.get_primary_email() or '',
                'All Contact Emails': '; '.join(sponsor.contact_emails),
                'LinkedIn URL': sponsor.linkedin_url or '',
                'Events Sponsored': '; '.join(sponsor.events_sponsored),
                'Number of Events': len(sponsor.events_sponsored),
                'Logo URL': sponsor.logo_url or '',
                'Email Subject': email_data.get('subject', ''),
                'Email Body': email_data.get('body', ''),
                'Subject Variations': ' | '.join(email_data.get('subject_variations', []))
            }
            rows.append(row)

        # Write to CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Company Name', 'Website', 'Industry', 'Tier',
                'Primary Email', 'All Contact Emails', 'LinkedIn URL',
                'Events Sponsored', 'Number of Events', 'Logo URL',
                'Email Subject', 'Email Body', 'Subject Variations'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

        logger.info(f"Exported {len(rows)} sponsors to {filepath}")
        return filepath

    def export_to_excel(
        self,
        event: Event,
        sponsors: Dict[str, Sponsor],
        emails: Dict[str, Dict[str, str]],
        filename: str = None
    ) -> str:
        """Export sponsor data and emails to Excel with multiple sheets."""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"sponsors_{timestamp}.xlsx"

        filepath = os.path.join(self.output_dir, filename)

        # Prepare data for Excel
        sponsor_data = []
        email_data = []

        for company_name, sponsor in sponsors.items():
            email_info = emails.get(company_name, {})

            # Sponsor information sheet
            sponsor_row = {
                'Company Name': sponsor.company_name,
                'Website': sponsor.website or '',
                'Industry': sponsor.industry or '',
                'Tier': sponsor.tier or '',
                'Primary Email': sponsor.get_primary_email() or '',
                'All Contact Emails': '; '.join(sponsor.contact_emails),
                'LinkedIn URL': sponsor.linkedin_url or '',
                'Events Sponsored': '; '.join(sponsor.events_sponsored),
                'Number of Events': len(sponsor.events_sponsored),
                'Logo URL': sponsor.logo_url or ''
            }
            sponsor_data.append(sponsor_row)

            # Email drafts sheet
            email_row = {
                'Company Name': sponsor.company_name,
                'Primary Email': sponsor.get_primary_email() or '',
                'Subject Line': email_info.get('subject', ''),
                'Email Body': email_info.get('body', ''),
                'Alternative Subjects': '\n'.join(email_info.get('subject_variations', []))
            }
            email_data.append(email_row)

        # Create Excel file with multiple sheets
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            # Event details sheet
            event_df = pd.DataFrame([{
                'Event Name': event.name,
                'Event Type': event.event_type,
                'Industry': event.industry,
                'Date': event.date.isoformat() if event.date else '',
                'Location': event.location or '',
                'Expected Audience': event.audience_size or '',
                'Description': event.description,
                'Total Sponsors Found': len(sponsors)
            }])
            event_df.to_excel(writer, sheet_name='Event Details', index=False)

            # Sponsors sheet
            sponsors_df = pd.DataFrame(sponsor_data)
            sponsors_df.to_excel(writer, sheet_name='Sponsors', index=False)

            # Email drafts sheet
            emails_df = pd.DataFrame(email_data)
            emails_df.to_excel(writer, sheet_name='Email Drafts', index=False)

            # Statistics sheet
            stats_df = self._generate_statistics(sponsors)
            stats_df.to_excel(writer, sheet_name='Statistics', index=False)

        logger.info(f"Exported {len(sponsor_data)} sponsors to {filepath}")
        return filepath

    def _generate_statistics(self, sponsors: Dict[str, Sponsor]) -> pd.DataFrame:
        """Generate statistics about the sponsors."""
        total_sponsors = len(sponsors)
        with_emails = sum(1 for s in sponsors.values() if s.contact_emails)
        with_websites = sum(1 for s in sponsors.values() if s.website)

        # Tier distribution
        tier_counts = {}
        for sponsor in sponsors.values():
            tier = sponsor.tier or 'unknown'
            tier_counts[tier] = tier_counts.get(tier, 0) + 1

        # Industry distribution
        industry_counts = {}
        for sponsor in sponsors.values():
            industry = sponsor.industry or 'unknown'
            industry_counts[industry] = industry_counts.get(industry, 0) + 1

        # Create statistics dataframe
        stats = [
            {'Metric': 'Total Sponsors', 'Value': total_sponsors},
            {'Metric': 'Sponsors with Emails', 'Value': with_emails},
            {'Metric': 'Sponsors with Websites', 'Value': with_websites},
            {'Metric': 'Email Coverage %', 'Value': f"{(with_emails/total_sponsors*100):.1f}%" if total_sponsors > 0 else '0%'},
            {'Metric': '', 'Value': ''},
            {'Metric': 'Tier Distribution', 'Value': ''},
        ]

        for tier, count in sorted(tier_counts.items()):
            stats.append({'Metric': f"  {tier.title()}", 'Value': count})

        stats.append({'Metric': '', 'Value': ''})
        stats.append({'Metric': 'Industry Distribution', 'Value': ''})

        for industry, count in sorted(industry_counts.items()):
            stats.append({'Metric': f"  {industry.title()}", 'Value': count})

        return pd.DataFrame(stats)

    def export_email_templates(
        self,
        emails: Dict[str, Dict[str, str]],
        filename: str = None
    ) -> str:
        """Export individual email templates as text files."""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            folder = f"email_templates_{timestamp}"
        else:
            folder = filename

        folder_path = os.path.join(self.output_dir, folder)
        os.makedirs(folder_path, exist_ok=True)

        for company_name, email_data in emails.items():
            # Clean company name for filename
            safe_name = "".join(c for c in company_name if c.isalnum() or c in (' ', '-', '_'))
            safe_name = safe_name.replace(' ', '_')
            file_path = os.path.join(folder_path, f"{safe_name}.txt")

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"SUBJECT: {email_data.get('subject', '')}\n")
                f.write("="*80 + "\n\n")
                f.write(email_data.get('body', ''))
                f.write("\n\n" + "="*80 + "\n")
                f.write("ALTERNATIVE SUBJECT LINES:\n")
                for alt_subject in email_data.get('subject_variations', [])[1:]:
                    f.write(f"- {alt_subject}\n")

        logger.info(f"Exported {len(emails)} email templates to {folder_path}")
        return folder_path
