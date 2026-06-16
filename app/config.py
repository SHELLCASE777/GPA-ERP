import warnings
from functools import lru_cache

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_SECRET_KEY = "dev-secret-key-replace-in-production"
# Also catch the .env placeholder value shipped with the repo
_PLACEHOLDER_SECRET_KEYS = {
    _DEFAULT_SECRET_KEY,
    "change-me-to-a-very-long-random-string-in-production",
}
_DEFAULT_DB_PASSWORD_FRAGMENT = "gpa_pass"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    DATABASE_URL: str = "postgresql://gpa_user:gpa_pass@localhost:5432/gpa_erp"

    # JWT
    SECRET_KEY: str = _DEFAULT_SECRET_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480

    # App
    APP_NAME: str = "GPA-ERP"
    APP_VERSION: str = "5.0.0"
    DEBUG: bool = False
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://localhost:5173"

    # Seed
    SEED_SUPER_ADMIN_EMAIL: str = "admin@gpa.local"
    SEED_SUPER_ADMIN_PASSWORD: str = "ChangeMe123!"
    SEED_SUPER_ADMIN_NAME: str = "System Administrator"

    # Uploads
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_MB: int = 10

    # SMTP email (optional — leave blank to disable email notifications)
    SMTP_HOST:     str = ""
    SMTP_PORT:     int = 587
    SMTP_USER:     str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM:     str = "GPA ERP <noreply@gpa.local>"
    SMTP_USE_TLS:  bool = True

    @field_validator("SECRET_KEY", mode="after")
    @classmethod
    def _validate_secret_key(cls, v: str) -> str:
        # Validation against DEBUG is done in model_validator below; just return here.
        return v

    @model_validator(mode="after")
    def _security_checks(self) -> "Settings":
        # In production (DEBUG=False), reject any known placeholder SECRET_KEY.
        if not self.DEBUG and self.SECRET_KEY in _PLACEHOLDER_SECRET_KEYS:
            raise ValueError(
                "SECRET_KEY is still set to the insecure development default. "
                "Set a strong random SECRET_KEY before running in production (DEBUG=False)."
            )

        # Always warn if the DATABASE_URL still uses the default dev password.
        if _DEFAULT_DB_PASSWORD_FRAGMENT in self.DATABASE_URL:
            warnings.warn(
                f"WARNING: DATABASE_URL still contains the default dev password "
                f"('{_DEFAULT_DB_PASSWORD_FRAGMENT}'). "
                "Update DATABASE_URL with a strong password before deploying to production.",
                stacklevel=2,
            )

        return self

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()
