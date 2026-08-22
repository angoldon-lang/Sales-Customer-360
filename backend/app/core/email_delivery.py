from abc import ABC, abstractmethod
from typing import List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import get_settings


class EmailProvider(ABC):
    """Abstract base class for email delivery providers."""

    @abstractmethod
    async def send(
        self,
        to_emails: List[str],
        subject: str,
        body_text: str,
        body_html: str,
    ) -> bool:
        """Send email and return success status."""
        pass


class SMTPEmailProvider(EmailProvider):
    """SMTP email provider."""

    async def send(
        self,
        to_emails: List[str],
        subject: str,
        body_text: str,
        body_html: str,
    ) -> bool:
        """Send email via SMTP."""
        settings = get_settings()

        if not settings.smtp_user or not settings.smtp_password:
            # Mock mode if not configured
            print(f"[MOCK EMAIL] To: {', '.join(to_emails)}")
            print(f"[MOCK EMAIL] Subject: {subject}")
            return True

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.smtp_from_email
            msg["To"] = ", ".join(to_emails)

            part1 = MIMEText(body_text, "plain")
            part2 = MIMEText(body_html, "html")
            msg.attach(part1)
            msg.attach(part2)

            with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_password)
                server.sendmail(settings.smtp_from_email, to_emails, msg.as_string())

            return True
        except Exception as e:
            print(f"[EMAIL ERROR] {str(e)}")
            return False


class MockEmailProvider(EmailProvider):
    """Mock email provider for development/testing."""

    async def send(
        self,
        to_emails: List[str],
        subject: str,
        body_text: str,
        body_html: str,
    ) -> bool:
        """Mock email send."""
        print(f"[MOCK EMAIL] To: {', '.join(to_emails)}")
        print(f"[MOCK EMAIL] Subject: {subject}")
        return True


class EmailDelivery:
    """Facade for email delivery with pluggable providers."""

    def __init__(self, provider: EmailProvider = None):
        self.provider = provider or MockEmailProvider()

    async def send(
        self,
        to_emails: List[str],
        subject: str,
        body_text: str,
        body_html: str,
    ) -> bool:
        """Send email."""
        return await self.provider.send(to_emails, subject, body_text, body_html)
