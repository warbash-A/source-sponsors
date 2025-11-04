"""Sponsor data model."""

from dataclasses import dataclass, field
from typing import Optional, List, Set


@dataclass
class Sponsor:
    """Represents a sponsor company with contact information."""

    company_name: str
    website: Optional[str] = None
    industry: Optional[str] = None
    tier: Optional[str] = None  # platinum, gold, silver, etc.
    contact_emails: List[str] = field(default_factory=list)
    linkedin_url: Optional[str] = None
    events_sponsored: Set[str] = field(default_factory=set)
    logo_url: Optional[str] = None

    def add_event(self, event_name: str):
        """Add an event to the list of sponsored events."""
        self.events_sponsored.add(event_name)

    def get_primary_email(self) -> Optional[str]:
        """Get the primary contact email."""
        priority_prefixes = ['sponsorships', 'partnerships', 'events', 'marketing']

        # First, look for priority emails
        for prefix in priority_prefixes:
            for email in self.contact_emails:
                if email.startswith(prefix):
                    return email

        # Otherwise, return the first email if available
        return self.contact_emails[0] if self.contact_emails else None

    def to_dict(self) -> dict:
        """Convert sponsor to dictionary."""
        return {
            'company_name': self.company_name,
            'website': self.website,
            'industry': self.industry,
            'tier': self.tier,
            'contact_emails': self.contact_emails,
            'primary_email': self.get_primary_email(),
            'linkedin_url': self.linkedin_url,
            'events_sponsored': list(self.events_sponsored),
            'events_count': len(self.events_sponsored),
            'logo_url': self.logo_url
        }
