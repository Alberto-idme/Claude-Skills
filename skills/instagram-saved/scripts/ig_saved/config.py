"""Runtime configuration, resolved from CLI flags then environment."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

# The public web app id every instagram.com page sends. Required on /api/v1/ calls.
IG_APP_ID = "936619743392459"

DEFAULT_ROOT = Path(os.environ.get("IG_SAVED_HOME", "~/.ig-saved")).expanduser()


@dataclass
class Config:
    root: Path = DEFAULT_ROOT
    """Everything the tool writes lives under here."""

    apify_token: str | None = field(
        default_factory=lambda: os.environ.get("APIFY_TOKEN")
    )
    apify_actor: str = field(
        default_factory=lambda: os.environ.get(
            "APIFY_ACTOR", "patient_discovery/instagram-posts"
        )
    )
    apify_url_field: str = field(
        default_factory=lambda: os.environ.get("APIFY_URL_FIELD", "startUrls")
    )

    whisper_model: str = field(
        default_factory=lambda: os.environ.get("IG_SAVED_WHISPER_MODEL", "small")
    )

    # Pacing. Instagram's private endpoints are unpublished and unmetered; going
    # fast from one account is the single most reliable way to earn a checkpoint.
    min_delay: float = 1.5
    max_delay: float = 4.0

    @property
    def db_path(self) -> Path:
        return self.root / "saved.db"

    @property
    def media_dir(self) -> Path:
        return self.root / "media"

    @property
    def browser_profile(self) -> Path:
        return self.root / "chrome-profile"

    def ensure_dirs(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        self.media_dir.mkdir(parents=True, exist_ok=True)
