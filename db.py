"""
Tech-Kative AI-Readiness Diagnostic v2 — Supabase Persistence Layer

Requires Streamlit secrets or env vars: SUPABASE_URL, SUPABASE_KEY.
Falls back silently if not configured — the app continues without saving.

Supabase table schema (run in Supabase SQL editor):

    CREATE TABLE assessments (
        id               UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        created_at       TIMESTAMPTZ DEFAULT now(),
        institution_name TEXT,
        institution_type TEXT,
        country          TEXT,
        contact_email    TEXT,
        role             TEXT,
        pilot_code       TEXT,
        assessment_phase TEXT,
        consent_given_at TIMESTAMPTZ,
        responses        JSONB,
        pillar_scores    JSONB,
        composite        FLOAT,
        tier             TEXT,
        regulatory_flags JSONB
    );
"""

import json
import os


def _client():
    """Return a Supabase client or None if credentials are not configured."""
    try:
        import streamlit as st
        from supabase import create_client
        url = (
            st.secrets.get("SUPABASE_URL")
            if hasattr(st, "secrets")
            else None
        ) or os.environ.get("SUPABASE_URL")
        key = (
            st.secrets.get("SUPABASE_KEY")
            if hasattr(st, "secrets")
            else None
        ) or os.environ.get("SUPABASE_KEY")
        if url and key:
            return create_client(url, key)
    except Exception:
        pass
    return None


def save_assessment(
    profile: dict,
    scores: dict,
    flags: list,
    responses: dict,
) -> bool:
    """
    Persist a completed assessment to Supabase.
    Returns True on success, False on failure or when Supabase is not configured.
    The caller should continue regardless of the return value.
    """
    client = _client()
    if not client:
        return False
    try:
        row = {
            "institution_name":  profile.get("institution_name"),
            "institution_type":  profile.get("institution_type"),
            "country":           profile.get("country"),
            "contact_email":     profile.get("contact_email"),
            "role":              profile.get("role"),
            "pilot_code":        profile.get("pilot_code", ""),
            "assessment_phase":  profile.get("assessment_phase", ""),
            "consent_given_at":  profile.get("consent_given_at"),
            "responses":         json.dumps(responses),
            "pillar_scores":     json.dumps(scores.get("pillar_scores", {})),
            "composite":         scores.get("composite"),
            "tier":              scores.get("tier"),
            "regulatory_flags":  json.dumps(flags or []),
        }
        client.table("assessments").insert(row).execute()
        return True
    except Exception:
        return False
