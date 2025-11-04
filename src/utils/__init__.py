"""Utility functions for the sponsor outreach system."""

from .email_utils import generate_email_variants, validate_email, extract_emails_from_website
from .logger import setup_logger

__all__ = [
    'generate_email_variants',
    'validate_email',
    'extract_emails_from_website',
    'setup_logger'
]
