"""Google OAuth2 authentication service."""

from datetime import datetime, timezone

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from sqlalchemy import select

from cass.config import settings
from cass.database import async_session
from cass.models.db_models import GoogleToken

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/calendar.events",
]


class GoogleAuthService:
    """Handles Google OAuth2 flow and credential management."""

    @staticmethod
    def _build_flow() -> Flow:
        """Build an OAuth2 flow from application settings."""
        client_config = {
            "web": {
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [settings.google_redirect_uri],
            }
        }
        flow = Flow.from_client_config(client_config, scopes=SCOPES)
        flow.redirect_uri = settings.google_redirect_uri
        return flow

    @staticmethod
    def get_auth_url() -> str:
        """Generate a Google OAuth2 authorization URL."""
        flow = GoogleAuthService._build_flow()
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        return auth_url

    @staticmethod
    async def handle_callback(code: str) -> None:
        """Exchange authorization code for tokens and store them in the database."""
        flow = GoogleAuthService._build_flow()
        flow.fetch_token(code=code)
        creds = flow.credentials

        async with async_session() as session:
            # Check for existing token row
            result = await session.execute(select(GoogleToken).limit(1))
            token_row = result.scalar_one_or_none()

            if token_row:
                token_row.access_token = creds.token
                token_row.refresh_token = creds.refresh_token or token_row.refresh_token
                token_row.token_uri = creds.token_uri
                token_row.scopes = " ".join(creds.scopes or SCOPES)
                token_row.expiry = creds.expiry
            else:
                token_row = GoogleToken(
                    access_token=creds.token,
                    refresh_token=creds.refresh_token,
                    token_uri=creds.token_uri,
                    scopes=" ".join(creds.scopes or SCOPES),
                    expiry=creds.expiry,
                )
                session.add(token_row)

            await session.commit()

    @staticmethod
    async def get_credentials() -> Credentials:
        """Load stored tokens from the database and refresh if expired.

        Returns a google.oauth2.credentials.Credentials instance ready for API use.
        Raises ValueError if no stored tokens are found.
        """
        async with async_session() as session:
            result = await session.execute(select(GoogleToken).limit(1))
            token_row = result.scalar_one_or_none()

        if not token_row:
            raise ValueError(
                "No Google credentials found. Please authenticate via /auth/google first."
            )

        creds = Credentials(
            token=token_row.access_token,
            refresh_token=token_row.refresh_token,
            token_uri=token_row.token_uri,
            client_id=settings.google_client_id,
            client_secret=settings.google_client_secret,
            scopes=token_row.scopes.split() if token_row.scopes else SCOPES,
        )

        if creds.expiry:
            creds.expiry = creds.expiry.replace(tzinfo=None)

        # Refresh if expired
        if creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request

            creds.refresh(Request())

            # Persist refreshed tokens
            async with async_session() as session:
                result = await session.execute(select(GoogleToken).limit(1))
                token_row = result.scalar_one_or_none()
                if token_row:
                    token_row.access_token = creds.token
                    token_row.expiry = creds.expiry
                    await session.commit()

        return creds
