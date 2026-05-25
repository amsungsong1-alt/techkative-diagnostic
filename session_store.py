"""
Tech-Kative Diagnostic — URL-token session store.

Saves drafts to session_store/{token}.json for in-session resume via ?token=.
Note: Streamlit Cloud uses an ephemeral filesystem; tokens survive only while
the instance is running. The JSON download (welcome screen) is the cross-restart
resume mechanism.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

STORE_DIR = Path("session_store")
EXPIRY_DAYS = 7


def new_token() -> str:
    return uuid.uuid4().hex[:16]


def save(token: str, payload: dict) -> None:
    STORE_DIR.mkdir(exist_ok=True)
    (STORE_DIR / f"{token}.json").write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8"
    )


def load(token: str) -> dict | None:
    path = STORE_DIR / f"{token}.json"
    if not path.exists():
        return None
    age_days = (
        datetime.now(tz=timezone.utc)
        - datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    ).days
    if age_days > EXPIRY_DAYS:
        try:
            path.unlink()
        except Exception:
            pass
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
