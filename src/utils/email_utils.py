"""Email-related utility functions."""

import re
from typing import List, Set
from email_validator import validate_email as validate_email_address, EmailNotValidError
import requests
from bs4 import BeautifulSoup


def validate_email(email: str) -> bool:
    """Validate an email address."""
    try:
        validate_email_address(email)
        return True
    except EmailNotValidError:
        return False


def generate_email_variants(company_domain: str) -> List[str]:
    """Generate common email variants for a company domain."""
    if not company_domain:
        return []

    # Remove www. and http(s):// if present
    domain = company_domain.replace('http://', '').replace('https://', '').replace('www.', '')
    domain = domain.split('/')[0]  # Get just the domain part

    common_prefixes = [
        'sponsorships',
        'partnerships',
        'events',
        'marketing',
        'info',
        'contact',
        'hello',
        'sales',
        'business'
    ]

    return [f"{prefix}@{domain}" for prefix in common_prefixes]


def extract_emails_from_website(url: str, timeout: int = 10) -> Set[str]:
    """Extract email addresses from a website."""
    emails = set()

    try:
        # Add headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.text, 'lxml')

        # Extract emails from mailto links
        for link in soup.find_all('a', href=re.compile(r'^mailto:')):
            email = link['href'].replace('mailto:', '').split('?')[0]
            if validate_email(email):
                emails.add(email.lower())

        # Extract emails from text using regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        found_emails = re.findall(email_pattern, response.text)

        for email in found_emails:
            email = email.lower()
            if validate_email(email) and not email.endswith(('.png', '.jpg', '.gif')):
                emails.add(email)

        # Try common contact/sponsorship pages
        contact_pages = ['/contact', '/sponsors', '/sponsorship', '/partnerships', '/about']
        for page in contact_pages:
            try:
                page_url = url.rstrip('/') + page
                response = requests.get(page_url, headers=headers, timeout=5)
                if response.status_code == 200:
                    found_emails = re.findall(email_pattern, response.text)
                    for email in found_emails:
                        email = email.lower()
                        if validate_email(email):
                            emails.add(email)
            except:
                continue

    except Exception as e:
        # Silently fail and return what we have
        pass

    return emails
