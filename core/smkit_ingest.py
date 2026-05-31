"""
Tech-Kative Diagnostic — SMKit Headteacher Diary Ingestion

Accepts JSON or CSV exported from the Standbasis SMKit platform.
Validates, coerces types, and returns a list of DiaryEntry objects.

To remap real SMKit column names: update FIELD_MAP at the top of this file.
"""

import csv
import io
import json
from dataclasses import dataclass, field
from datetime import date
from typing import Any

# ---------------------------------------------------------------------------
# Column name remapping — update these to match the actual SMKit export headers
# without touching any logic below.
# ---------------------------------------------------------------------------

FIELD_MAP: dict[str, str] = {
    "school_id":             "school_id",
    "school_name":           "school_name",
    "week_ending":           "week_ending",
    "enrolment":             "enrolment",
    "attendance_present":    "attendance_present",
    "staff_total":           "staff_total",
    "staff_present":         "staff_present",
    "lessons_planned":       "lessons_planned",
    "lessons_delivered":     "lessons_delivered",
    "record_keeping":        "record_keeping",
    "consent_on_file":       "consent_on_file",
    "data_storage":          "data_storage",
    "ai_tools_used":         "ai_tools_used",
    "ai_policy_in_place":    "ai_policy_in_place",
    "safeguarding_incidents": "safeguarding_incidents",
    "notes":                 "notes",
}

REQUIRED_FIELDS = {
    "school_id", "school_name", "week_ending", "enrolment",
    "attendance_present", "staff_total", "staff_present",
    "lessons_planned", "lessons_delivered", "record_keeping",
    "consent_on_file", "data_storage", "ai_tools_used",
    "ai_policy_in_place", "safeguarding_incidents",
}

VALID_RECORD_KEEPING = {"none", "paper", "spreadsheet", "digital_system"}
VALID_DATA_STORAGE   = {"none", "paper", "personal_device", "school_device", "cloud"}


@dataclass
class DiaryEntry:
    school_id:              str
    school_name:            str
    week_ending:            date
    enrolment:              int
    attendance_present:     int
    staff_total:            int
    staff_present:          int
    lessons_planned:        int
    lessons_delivered:      int
    record_keeping:         str
    consent_on_file:        bool
    data_storage:           str
    ai_tools_used:          list[str]
    ai_policy_in_place:     bool
    safeguarding_incidents: int
    notes:                  str = ""


def _remap(row: dict) -> dict:
    """Apply FIELD_MAP to convert SMKit column names to our internal names."""
    inv = {v: k for k, v in FIELD_MAP.items()}
    return {inv.get(k, k): v for k, v in row.items()}


def _coerce(raw: dict, idx: int) -> DiaryEntry:
    """Coerce and validate one raw dict row. Raises ValueError on failure."""
    context = f"row {idx + 1} (school_id={raw.get('school_id', '?')!r}, week_ending={raw.get('week_ending', '?')!r})"

    missing = REQUIRED_FIELDS - set(raw.keys())
    if missing:
        raise ValueError(f"{context}: missing required fields: {sorted(missing)}")

    def _int(key: str) -> int:
        v = raw[key]
        try:
            n = int(v)
        except (TypeError, ValueError):
            raise ValueError(f"{context}: '{key}' must be an integer, got {v!r}")
        if n < 0:
            raise ValueError(f"{context}: '{key}' must be ≥ 0, got {n}")
        return n

    def _bool(key: str) -> bool:
        v = raw[key]
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            if v.strip().lower() in ("true", "1", "yes"):
                return True
            if v.strip().lower() in ("false", "0", "no"):
                return False
        if isinstance(v, int):
            return bool(v)
        raise ValueError(f"{context}: '{key}' must be true/false, got {v!r}")

    def _date(key: str) -> date:
        v = raw[key]
        if isinstance(v, date):
            return v
        try:
            return date.fromisoformat(str(v))
        except Exception:
            raise ValueError(f"{context}: '{key}' must be ISO date (yyyy-mm-dd), got {v!r}")

    def _str_enum(key: str, valid: set) -> str:
        v = str(raw.get(key, "")).strip().lower()
        if v not in valid:
            raise ValueError(f"{context}: '{key}' must be one of {sorted(valid)}, got {v!r}")
        return v

    def _list_str(key: str) -> list[str]:
        v = raw[key]
        if isinstance(v, list):
            return [str(x).strip() for x in v]
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("["):
                try:
                    parsed = json.loads(v)
                    if isinstance(parsed, list):
                        return [str(x).strip() for x in parsed]
                except Exception:
                    pass
            return [x.strip() for x in v.split(",") if x.strip()]
        return []

    enrolment          = _int("enrolment")
    attendance_present = _int("attendance_present")
    staff_total        = _int("staff_total")
    staff_present      = _int("staff_present")
    lessons_planned    = _int("lessons_planned")
    lessons_delivered  = _int("lessons_delivered")
    safeguarding       = _int("safeguarding_incidents")

    if attendance_present > enrolment:
        raise ValueError(f"{context}: 'attendance_present' ({attendance_present}) > 'enrolment' ({enrolment})")
    if staff_present > staff_total:
        raise ValueError(f"{context}: 'staff_present' ({staff_present}) > 'staff_total' ({staff_total})")
    if lessons_planned > 0 and lessons_delivered > lessons_planned:
        raise ValueError(f"{context}: 'lessons_delivered' ({lessons_delivered}) > 'lessons_planned' ({lessons_planned})")

    return DiaryEntry(
        school_id=str(raw["school_id"]).strip(),
        school_name=str(raw.get("school_name", "")).strip(),
        week_ending=_date("week_ending"),
        enrolment=enrolment,
        attendance_present=attendance_present,
        staff_total=staff_total,
        staff_present=staff_present,
        lessons_planned=lessons_planned,
        lessons_delivered=lessons_delivered,
        record_keeping=_str_enum("record_keeping", VALID_RECORD_KEEPING),
        consent_on_file=_bool("consent_on_file"),
        data_storage=_str_enum("data_storage", VALID_DATA_STORAGE),
        ai_tools_used=_list_str("ai_tools_used"),
        ai_policy_in_place=_bool("ai_policy_in_place"),
        safeguarding_incidents=safeguarding,
        notes=str(raw.get("notes", "")).strip(),
    )


def load_entries(path_or_buffer) -> list[DiaryEntry]:
    """
    Load DiaryEntry records from a JSON array or CSV file/buffer.

    Accepts: file path (str/Path), readable buffer, or str containing JSON.
    Raises ValueError with human-readable messages listing offending rows.
    """
    # Detect and read raw content
    if hasattr(path_or_buffer, "read"):
        raw_bytes = path_or_buffer.read()
        if isinstance(raw_bytes, bytes):
            content = raw_bytes.decode("utf-8-sig")
        else:
            content = raw_bytes
    else:
        content_path = str(path_or_buffer)
        try:
            with open(content_path, encoding="utf-8-sig") as f:
                content = f.read()
        except (OSError, TypeError):
            content = str(path_or_buffer)

    content = content.strip()

    # Reject HTML files early (e.g. diagnostic report downloaded by mistake)
    if content.lstrip().startswith("<"):
        raise ValueError(
            "This looks like an HTML file (e.g. a downloaded diagnostic report), "
            "not an SMKit diary export.\n\n"
            "Please click '📥 Download sample data' to get the correct JSON file, "
            "save it to your device, and upload that file instead."
        )

    # Parse: JSON or CSV
    rows: list[dict[str, Any]]
    if content.startswith("[") or content.startswith("{"):
        try:
            parsed = json.loads(content)
            rows = parsed if isinstance(parsed, list) else [parsed]
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Could not parse JSON: {e}\n\n"
                "Make sure you are uploading the SMKit diary export (JSON or CSV), "
                "not a diagnostic report or draft file."
            ) from e
    else:
        reader = csv.DictReader(io.StringIO(content))
        rows = [dict(r) for r in reader]

    if not rows:
        raise ValueError("No data rows found in the file.")

    # Remap field names and coerce
    errors: list[str] = []
    entries: list[DiaryEntry] = []
    for i, row in enumerate(rows):
        remapped = _remap(row)
        try:
            entries.append(_coerce(remapped, i))
        except ValueError as e:
            errors.append(str(e))

    if errors:
        raise ValueError("Validation errors:\n" + "\n".join(f"  • {e}" for e in errors))

    return entries
