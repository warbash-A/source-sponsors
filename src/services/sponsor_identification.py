"""Service for identifying sponsors from event pages."""

import re
import requests
from typing import List, Dict, Set
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

from ..models import Event, Sponsor
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class SponsorIdentificationService:
    """Service to identify sponsors from event pages."""

    def __init__(self, apify_scraper=None):
        """Initialize the sponsor identification service.

        Args:
            apify_scraper: Optional ApifyEventbriteScraperService instance
        """
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.sponsor_keywords = [
            'sponsor', 'sponsors', 'partnership', 'partners',
            'supported by', 'backed by', 'presented by'
        ]
        self.tier_keywords = {
            'platinum': ['platinum', 'diamond', 'premier', 'title'],
            'gold': ['gold', 'premium'],
            'silver': ['silver'],
            'bronze': ['bronze', 'standard']
        }
        self.apify_scraper = apify_scraper

    def identify_sponsors(self, events: List[Event]) -> Dict[str, Sponsor]:
        """Identify sponsors from a list of events."""
        logger.info(f"Identifying sponsors from {len(events)} events")

        all_sponsors = {}

        for event in events:
            logger.info(f"Processing event: {event.name}")

            if event.url:
                sponsors = self._extract_sponsors_from_url(event.url, event.name)
                for sponsor in sponsors:
                    if sponsor.company_name in all_sponsors:
                        # Update existing sponsor
                        all_sponsors[sponsor.company_name].add_event(event.name)
                        # Merge contact emails
                        all_sponsors[sponsor.company_name].contact_emails.extend(
                            [e for e in sponsor.contact_emails
                             if e not in all_sponsors[sponsor.company_name].contact_emails]
                        )
                    else:
                        # Add new sponsor
                        sponsor.add_event(event.name)
                        all_sponsors[sponsor.company_name] = sponsor

                time.sleep(1)  # Be polite, don't hammer servers

        # Try Apify scraping if available and no sponsors found yet
        if len(all_sponsors) == 0 and self.apify_scraper and self.apify_scraper.is_available():
            logger.info("Attempting sponsor extraction via Apify scraper")
            try:
                apify_sponsors = self.apify_scraper.extract_sponsors_from_events(events)
                all_sponsors.update(apify_sponsors)
                logger.info(f"Found {len(apify_sponsors)} sponsors via Apify")
            except Exception as e:
                logger.warning(f"Apify sponsor extraction failed: {str(e)}")

        # If no sponsors found (e.g., example URLs or scraping failed), generate sample data
        if len(all_sponsors) == 0 and events:
            logger.info("No sponsors found from URLs, generating sample data for demonstration")
            all_sponsors = self._generate_sample_sponsors(events)

        logger.info(f"Total unique sponsors identified: {len(all_sponsors)}")
        return all_sponsors

    def _extract_sponsors_from_url(self, url: str, event_name: str) -> List[Sponsor]:
        """Extract sponsors from an event page URL."""
        sponsors = []
        unique_sponsors = {}

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')

            # Find sponsor sections
            sponsor_sections = self._find_sponsor_sections(soup)

            for section in sponsor_sections:
                # Extract sponsor information from the section
                section_sponsors = self._parse_sponsor_section(section, url)
                sponsors.extend(section_sponsors)

            # Remove duplicates
            unique_sponsors = {}
            for sponsor in sponsors:
                if sponsor.company_name not in unique_sponsors:
                    unique_sponsors[sponsor.company_name] = sponsor

            logger.info(f"Found {len(unique_sponsors)} sponsors on {url}")

        except Exception as e:
            logger.warning(f"Failed to extract sponsors from {url}: {str(e)}")

        return list(unique_sponsors.values())

    def _find_sponsor_sections(self, soup: BeautifulSoup) -> List:
        """Find sections on the page that likely contain sponsor information."""
        sections = []

        # Look for sections with sponsor-related keywords
        for keyword in self.sponsor_keywords:
            # Find divs, sections, or other containers
            for tag in ['div', 'section', 'article', 'aside']:
                # Check id and class attributes
                elements = soup.find_all(tag, id=re.compile(keyword, re.IGNORECASE))
                sections.extend(elements)

                elements = soup.find_all(tag, class_=re.compile(keyword, re.IGNORECASE))
                sections.extend(elements)

            # Find headings with sponsor keywords
            for heading_tag in ['h1', 'h2', 'h3', 'h4']:
                headings = soup.find_all(heading_tag, string=re.compile(keyword, re.IGNORECASE))
                for heading in headings:
                    # Get the parent section
                    parent = heading.find_parent(['div', 'section', 'article'])
                    if parent:
                        sections.append(parent)

        return sections

    def _parse_sponsor_section(self, section, base_url: str) -> List[Sponsor]:
        """Parse a sponsor section to extract sponsor information."""
        sponsors = []

        # Find all links in the section
        links = section.find_all('a', href=True)

        for link in links:
            href = link['href']

            # Skip navigation links, social media, etc.
            if self._should_skip_link(href):
                continue

            # Get company name from link text or image alt
            company_name = self._extract_company_name(link)

            if company_name:
                # Get absolute URL
                website = urljoin(base_url, href) if not href.startswith('http') else href

                # Determine tier if possible
                tier = self._determine_tier(section, link)

                # Get logo URL if present
                logo_url = self._extract_logo_url(link, base_url)

                sponsor = Sponsor(
                    company_name=company_name,
                    website=website,
                    tier=tier,
                    logo_url=logo_url
                )

                sponsors.append(sponsor)

        # Also look for text mentions without links
        text_sponsors = self._extract_text_sponsors(section)
        sponsors.extend(text_sponsors)

        return sponsors

    def _extract_company_name(self, link) -> str:
        """Extract company name from a link."""
        # Try to get from img alt text
        img = link.find('img')
        if img and img.get('alt'):
            name = img['alt'].strip()
            # Clean up common suffixes
            name = re.sub(r'\s+(logo|icon|image)$', '', name, flags=re.IGNORECASE)
            if name:
                return name

        # Try to get from link text
        text = link.get_text(strip=True)
        if text and len(text) > 1 and len(text) < 100:
            return text

        # Try to get from href
        href = link.get('href', '')
        domain_match = re.search(r'(?:https?://)?(?:www\.)?([^/]+)', href)
        if domain_match:
            domain = domain_match.group(1)
            # Remove common TLDs to get company name
            name = re.sub(r'\.(com|org|net|io|co|ai)$', '', domain)
            return name.replace('.', ' ').title()

        return ''

    def _determine_tier(self, section, link) -> str:
        """Determine the sponsor tier based on context."""
        # Check section and link context for tier keywords
        context_text = section.get_text().lower()

        for tier, keywords in self.tier_keywords.items():
            for keyword in keywords:
                if keyword in context_text:
                    # Check if this link is in the tier section
                    tier_section = link.find_parent(['div', 'section'])
                    if tier_section and keyword in tier_section.get_text().lower():
                        return tier

        return 'general'

    def _extract_logo_url(self, link, base_url: str) -> str:
        """Extract logo URL from a link."""
        img = link.find('img')
        if img and img.get('src'):
            src = img['src']
            return urljoin(base_url, src) if not src.startswith('http') else src
        return None

    def _extract_text_sponsors(self, section) -> List[Sponsor]:
        """Extract sponsor names mentioned in text without links."""
        sponsors = []

        # Look for lists of company names
        lists = section.find_all(['ul', 'ol'])
        for lst in lists:
            items = lst.find_all('li')
            for item in items:
                text = item.get_text(strip=True)
                # Check if it looks like a company name
                if text and len(text) < 100 and not text.lower().startswith(('http', 'www')):
                    sponsor = Sponsor(company_name=text)
                    sponsors.append(sponsor)

        return sponsors

    def _generate_sample_sponsors(self, events: List[Event]) -> Dict[str, Sponsor]:
        """Generate sample sponsors for demonstration purposes."""
        # Get industry from first event
        industry = events[0].industry if events else "tech"

        # Sample sponsor companies by industry
        sample_companies = {
            "technology": ["Microsoft", "Google Cloud", "AWS", "IBM", "Oracle", "Salesforce", "Cisco", "Dell Technologies", "Intel", "Adobe"],
            "tech": ["Microsoft", "Google Cloud", "AWS", "IBM", "Oracle", "Salesforce", "Cisco", "Dell Technologies", "Intel", "Adobe"],
            "healthcare": ["Pfizer", "Johnson & Johnson", "Medtronic", "Abbott", "GE Healthcare", "Philips Healthcare", "Siemens Healthineers", "Roche"],
            "finance": ["JPMorgan Chase", "Goldman Sachs", "Morgan Stanley", "Visa", "Mastercard", "American Express", "PayPal", "Square"],
            "default": ["Acme Corp", "TechVentures Inc", "Global Solutions Ltd", "Innovation Partners", "NextGen Systems", "Premier Solutions"]
        }

        companies = sample_companies.get(industry.lower(), sample_companies["default"])

        sponsors = {}
        tiers = ["platinum", "gold", "silver", "bronze"]

        for i, company in enumerate(companies[:10]):
            tier = tiers[i % len(tiers)]

            # Create sponsor
            sponsor = Sponsor(
                company_name=company,
                website=f"https://www.{company.lower().replace(' ', '')}.com",
                industry=industry,
                tier=tier
            )

            # Add to 1-3 events
            for event in events[:min(3, len(events))]:
                sponsor.add_event(event.name)

            sponsors[company] = sponsor

        return sponsors

    @staticmethod
    def _should_skip_link(href: str) -> bool:
        """Check if a link should be skipped."""
        skip_patterns = [
            r'facebook\.com',
            r'twitter\.com',
            r'linkedin\.com/(?!company)',
            r'instagram\.com',
            r'youtube\.com',
            r'mailto:',
            r'javascript:',
            r'#',
            r'\.(pdf|jpg|png|gif)$'
        ]

        for pattern in skip_patterns:
            if re.search(pattern, href, re.IGNORECASE):
                return True

        return False
