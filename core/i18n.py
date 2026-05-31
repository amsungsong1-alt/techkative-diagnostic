"""
Tech-Kative Diagnostic — Internationalisation (i18n)

DRAFT translations — confirm with a native speaker before the June pilot.
English is the source of truth; updating a translation is a one-line change per key.
"""

from pathlib import Path

LANGUAGES = {"en": "English", "tw": "Twi", "dag": "Dagbani"}

_AUDIO_FILES = {
    "en": "assets/intro_en.mp3",
    "tw": "assets/intro_tw.mp3",
    "dag": "assets/intro_dg.mp3",
}

T: dict[str, dict[str, str]] = {
    "en": {
        "welcome_intro": (
            "Welcome to the Tech-Kative AI-Readiness Diagnostic. This tool helps your "
            "institution understand its readiness to govern, deploy, and absorb AI "
            "responsibly across four pillars."
        ),
        "audio_btn": "▶ Listen to welcome in English",
    },
    # DRAFT — confirm with a Twi native speaker before any headteacher sees this.
    "tw": {
        "welcome_intro": (
            "Akwaaba kɔ Tech-Kative AI-Readiness Diagnostic mu. "
            "Saa adwinnadeɛ yi boa wo dwumadibea ma ɛte aseɛ sɛdeɛ ɛyɛ krado sɛ "
            "ɛbɛhwɛ AI so, ɛde adi dwuma, na ɛde ayɛ adwuma wɔ ɔkwan pa so "
            "wɔ afa anan no nyinaa so."
        ),
        "audio_btn": "▶ Tie w'akwaaba wɔ Twi",
    },
    # DRAFT — confirm with a Dagbani native speaker before any headteacher sees this.
    "dag": {
        "welcome_intro": (
            "Maraaba ni Tech-Kative AI-Readiness Diagnostic. "
            "Tuuntuili ɔɛ maa sɛɔdi a tuma shee ka di baɔ di tariga ni di ni tooi gbibi, "
            "n-zaɔ tum tuma, ka deei AI ni yɛlimaɔli viɛla zuɛŋu, anahi maa zaa zuɛŋu."
        ),
        "audio_btn": "▶ Wuhigi di maraaba Dagbani",
    },
}


def t(key: str, lang: str = "en") -> str:
    """Return the localised string, falling back to English if missing."""
    return T.get(lang, T["en"]).get(key, T["en"].get(key, ""))


def audio_path(lang: str) -> Path:
    """Return the Path to the audio file for the given language code."""
    return Path(_AUDIO_FILES.get(lang, _AUDIO_FILES["en"]))
