import logging
import os

from dotenv import load_dotenv

load_dotenv()


def _split_csv(value: str) -> list:
    return [item.strip() for item in value.split(",") if item.strip()]


class Config:
    """Central place for every environment-driven setting. Defaults match
    what the app has always shipped with, so an existing deployment that
    only sets DATABASE_URL/SECRET_KEY/FLASK_ENV keeps working unchanged."""

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SECRET_KEY = os.environ.get("SECRET_KEY", "supersecret")

    # Falls back to the historical hardcoded dev secret so already-issued
    # tokens in any environment that doesn't set this explicitly keep working.
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "chave_dev_super_secreta")
    JWT_ACCESS_TOKEN_EXPIRES_HOURS = int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES_HOURS", "8"))

    CORS_ORIGINS = _split_csv(
        os.environ.get("CORS_ORIGINS", "https://memora.lkasta.com,http://localhost:3000")
    )

    # Storage credentials, used only to delete files that no memory references
    # any more. UPLOADTHING_TOKEN is the exact value the frontend already uses
    # (base64 JSON wrapping the API key); UPLOADTHING_API_KEY takes a raw
    # "sk_..." instead. With neither set the app still tracks images in the
    # database - it just leaves the files themselves in the bucket.
    UPLOADTHING_TOKEN = os.environ.get("UPLOADTHING_TOKEN")
    UPLOADTHING_API_KEY = os.environ.get("UPLOADTHING_API_KEY")
    UPLOADTHING_API_URL = os.environ.get(
        "UPLOADTHING_API_URL", "https://api.uploadthing.com"
    ).rstrip("/")

    FLASK_ENV = os.environ.get("FLASK_ENV", "production")
    DEBUG = FLASK_ENV == "development"
    PORT = int(os.environ.get("PORT", "5000"))

    @classmethod
    def validate(cls):
        """Fail fast with a clear message instead of letting a missing
        DATABASE_URL surface as a confusing SQLAlchemy error later on."""
        if not cls.SQLALCHEMY_DATABASE_URI:
            raise RuntimeError(
                "DATABASE_URL is not set. Copy .env.example to .env and fill it in."
            )
        if cls.FLASK_ENV != "development" and cls.JWT_SECRET_KEY == "chave_dev_super_secreta":
            logging.getLogger(__name__).warning(
                "JWT_SECRET_KEY is not set outside development; using the insecure "
                "default. Set JWT_SECRET_KEY in the environment before deploying."
            )
        if not cls.UPLOADTHING_TOKEN and not cls.UPLOADTHING_API_KEY:
            logging.getLogger(__name__).warning(
                "Neither UPLOADTHING_TOKEN nor UPLOADTHING_API_KEY is set; images "
                "will be tracked in the database but never removed from storage."
            )
