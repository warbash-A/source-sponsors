"""Event data model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class Event:
    """Represents an event with its details."""

    name: str
    event_type: str  # conference, workshop, meetup, etc.
    industry: str  # tech, healthcare, finance, etc.
    description: str
    date: Optional[datetime] = None
    location: Optional[str] = None
    audience_size: Optional[int] = None
    url: Optional[str] = None
    sponsors: List['Sponsor'] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert event to dictionary."""
        return {
            'name': self.name,
            'event_type': self.event_type,
            'industry': self.industry,
            'description': self.description,
            'date': self.date.isoformat() if self.date else None,
            'location': self.location,
            'audience_size': self.audience_size,
            'url': self.url,
            'sponsor_count': len(self.sponsors)
        }
