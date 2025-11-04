"""Service for generating personalized outreach emails."""

import os
import random
from typing import Dict, List, Optional
from ..models import Event, Sponsor
from ..utils.logger import setup_logger

logger = setup_logger(__name__)


class EmailGeneratorService:
    """Service to generate personalized outreach emails."""

    def __init__(self, openai_api_key: Optional[str] = None):
        """Initialize the email generator service."""
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        self.use_ai = bool(self.openai_api_key)

        if self.use_ai:
            try:
                import openai
                self.openai = openai
                self.openai.api_key = self.openai_api_key
                logger.info("OpenAI integration enabled for email generation")
            except ImportError:
                logger.warning("OpenAI package not installed, using template-based generation")
                self.use_ai = False

    def generate_emails(
        self,
        event: Event,
        sponsors: Dict[str, Sponsor],
        num_variations: int = 3
    ) -> Dict[str, Dict[str, str]]:
        """Generate personalized emails for each sponsor."""
        logger.info(f"Generating emails for {len(sponsors)} sponsors")

        emails = {}

        for company_name, sponsor in sponsors.items():
            logger.info(f"Generating email for: {company_name}")

            email_content = self._generate_email_for_sponsor(event, sponsor)
            subject_variations = self._generate_subject_variations(event, sponsor, num_variations)

            emails[company_name] = {
                'subject': subject_variations[0],  # Primary subject
                'subject_variations': subject_variations,
                'body': email_content
            }

        return emails

    def _generate_email_for_sponsor(self, event: Event, sponsor: Sponsor) -> str:
        """Generate a personalized email for a specific sponsor."""
        if self.use_ai:
            return self._generate_ai_email(event, sponsor)
        else:
            return self._generate_template_email(event, sponsor)

    def _generate_ai_email(self, event: Event, sponsor: Sponsor) -> str:
        """Generate email using OpenAI API."""
        try:
            events_list = ", ".join(list(sponsor.events_sponsored)[:3])

            prompt = f"""Write a professional, personalized sponsorship outreach email with the following details:

Sponsor Company: {sponsor.company_name}
Their Past Sponsorships: {events_list if events_list else "Research shows they sponsor similar events"}

Our Event Details:
- Name: {event.name}
- Type: {event.event_type}
- Industry: {event.industry}
- Date: {event.date.strftime('%B %Y') if event.date else 'TBD'}
- Location: {event.location or 'TBD'}
- Expected Audience: {event.audience_size or 'TBD'} attendees
- Description: {event.description}

Requirements:
- Professional but warm tone
- Highlight their past sponsorship of similar events
- Explain why they're a great fit for our event
- Mention the alignment between their brand and our audience
- Include a clear call to action
- Keep it concise (under 200 words)
- Don't include subject line
- End with a signature placeholder: [YOUR NAME]

Format the email ready to send."""

            response = self.openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional event organizer writing sponsorship outreach emails."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            logger.warning(f"AI email generation failed: {str(e)}, falling back to template")
            return self._generate_template_email(event, sponsor)

    def _generate_template_email(self, event: Event, sponsor: Sponsor) -> str:
        """Generate email using templates."""
        # Get sponsor's past events for personalization
        past_events = list(sponsor.events_sponsored)[:3]

        # Build past sponsorship mention
        if past_events:
            if len(past_events) == 1:
                past_mention = f"I noticed that {sponsor.company_name} sponsored {past_events[0]}"
            else:
                events_str = ", ".join(past_events[:-1]) + f", and {past_events[-1]}"
                past_mention = f"I noticed that {sponsor.company_name} has sponsored events like {events_str}"
        else:
            past_mention = f"I've been following {sponsor.company_name}'s involvement in the {event.industry} space"

        # Event details
        date_str = event.date.strftime('%B %Y') if event.date else 'upcoming'
        location_str = event.location or 'hybrid format'
        audience_str = f"{event.audience_size:,}" if event.audience_size else "several hundred"

        # Template variations
        templates = [
            f"""Dear {sponsor.company_name} Partnerships Team,

{past_mention}, and I wanted to reach out about an exciting opportunity.

We're organizing {event.name}, a {event.event_type} taking place in {date_str} at {location_str}. This event brings together {audience_str} professionals in the {event.industry} industry.

Given your previous support of similar events, I believe {event.name} would be an excellent fit for {sponsor.company_name}. Our audience aligns perfectly with your target market, and we have several sponsorship tiers available that offer excellent visibility and engagement opportunities.

Would you be interested in learning more about our sponsorship packages? I'd be happy to schedule a brief call to discuss how we can create a partnership that delivers real value for {sponsor.company_name}.

Looking forward to hearing from you!

Best regards,
[YOUR NAME]
[YOUR TITLE]
[YOUR CONTACT INFO]""",

            f"""Hi there,

I hope this email finds you well! {past_mention}, which really impressed me.

I'm reaching out because we're hosting {event.name} in {date_str}, and I think {sponsor.company_name} would be a perfect partner. Our event focuses on {event.industry} and will attract approximately {audience_str} attendees who are decision-makers and influencers in this space.

We have several sponsorship opportunities that would give {sponsor.company_name} excellent brand exposure and direct engagement with our audience. Based on your previous sponsorship activities, I believe this could be a great fit.

Would you be open to a quick conversation about partnership opportunities? I'd love to share more details about the event and explore how we might work together.

Thanks for considering!

Best,
[YOUR NAME]
[YOUR TITLE]""",

            f"""Hello,

{past_mention}, which inspired me to reach out regarding {event.name}.

We're bringing together the {event.industry} community for a {event.event_type} in {date_str}, expecting {audience_str} attendees. The event provides a unique platform for companies like {sponsor.company_name} to connect with key stakeholders and showcase your solutions.

Our sponsorship packages are designed to deliver measurable ROI through:
- Brand visibility across all event materials and platforms
- Speaking opportunities and thought leadership positioning
- Direct access to qualified leads
- Post-event content and engagement opportunities

I'd be delighted to discuss how a partnership could benefit {sponsor.company_name}. Are you available for a brief call next week?

Best regards,
[YOUR NAME]"""
        ]

        return random.choice(templates)

    def _generate_subject_variations(
        self,
        event: Event,
        sponsor: Sponsor,
        num_variations: int = 3
    ) -> List[str]:
        """Generate multiple subject line variations."""
        company = sponsor.company_name

        subject_templates = [
            f"Partnership Opportunity: {event.name}",
            f"Sponsorship Inquiry for {event.name}",
            f"{company} + {event.name}: Let's Partner",
            f"Exciting {event.industry.title()} Event Partnership",
            f"Would {company} be interested in sponsoring {event.name}?",
            f"{event.name} - Sponsorship Opportunity for {company}",
            f"Following up on your {event.industry} sponsorship activities",
            f"Perfect fit: {company} x {event.name}",
            f"Invitation to sponsor {event.name}",
            f"{event.event_type.title()} sponsorship opportunity - {event.name}"
        ]

        # Shuffle and return requested number
        random.shuffle(subject_templates)
        return subject_templates[:num_variations]
