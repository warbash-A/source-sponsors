"""Service for finding contact information for sponsors."""

import re
from typing import Dict
from urllib.parse import urlparse

from ..models import Sponsor
from ..utils.email_utils import generate_email_variants, extract_emails_from_website
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class ContactFinderService:
    """Service to find contact information for sponsors."""

    def __init__(self):
        """Initialize the contact finder service."""
        pass

    def enrich_sponsors_with_contacts(self, sponsors: Dict[str, Sponsor]) -> Dict[str, Sponsor]:
        """Enrich sponsor data with contact information."""
        logger.info(f"Finding contact information for {len(sponsors)} sponsors")

        for company_name, sponsor in sponsors.items():
            logger.info(f"Finding contacts for: {company_name}")

            # Extract emails from website if available
            if sponsor.website:
                try:
                    found_emails = extract_emails_from_website(sponsor.website)
                    sponsor.contact_emails.extend(list(found_emails))
                    logger.info(f"Found {len(found_emails)} emails from website")
                except Exception as e:
                    logger.warning(f"Failed to extract emails from {sponsor.website}: {str(e)}")

                # Generate email variants based on domain
                domain = self._extract_domain(sponsor.website)
                if domain:
                    email_variants = generate_email_variants(domain)
                    # Add variants that we haven't already found
                    for email in email_variants:
                        if email not in sponsor.contact_emails:
                            sponsor.contact_emails.append(email)

            # Try to find LinkedIn company page
            if not sponsor.linkedin_url:
                linkedin_url = self._generate_linkedin_url(company_name)
                sponsor.linkedin_url = linkedin_url

            # Deduplicate emails
            sponsor.contact_emails = list(dict.fromkeys(sponsor.contact_emails))

        logger.info("Contact enrichment completed")
        return sponsors

    @staticmethod
    def _extract_domain(url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            # Remove www. prefix
            domain = domain.replace('www.', '')
            return domain
        except:
            return ''

    @staticmethod
    def _generate_linkedin_url(company_name: str) -> str:
        """Generate a LinkedIn company page URL."""
        # Clean company name
        clean_name = re.sub(r'[^\w\s-]', '', company_name.lower())
        clean_name = re.sub(r'\s+', '-', clean_name.strip())

        return f"https://www.linkedin.com/company/{clean_name}"
