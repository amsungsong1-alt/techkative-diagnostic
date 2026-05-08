# Tech-Kative AI-Readiness Diagnostic

A structured institutional self-assessment instrument for African education systems. Assesses readiness to govern, deploy, and absorb AI across four pillars. Produces a readiness profile and a recommended pathway to a Stage 2 Diagnostic Engagement.

---

## Quick start

```bash
# 1. Activate virtual environment
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy env config (leave blank to use local outbox/ fallback)
cp .env.example .env

# 4. Run the app
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## Project structure

```
app.py            Streamlit entry point — 6-screen router
framework.py      Item bank, pillar defs, scoring config, observation templates
scoring.py        Pure scoring functions (no Streamlit dependency)
report.py         HTML report builder
email_service.py  SMTP sender with ./outbox/ local fallback
state.py          st.session_state helpers
styles.py         Brand CSS injected via st.markdown
assets/logo.png   Tech-Kative logo (supply your own — text fallback if absent)
tests/            Unit tests for scoring and observation logic
outbox/           Local email output (created automatically in dev mode)
```

---

## Running tests

```bash
python -m pytest tests/ -v
```

All scoring and observation logic is covered before any UI work runs.

---

## Email configuration

### Local development

Copy `.env.example` to `.env` and fill in your SMTP credentials.

| Variable | Description |
|---|---|
| `SMTP_HOST` | SMTP server (e.g. `smtp.gmail.com`) |
| `SMTP_PORT` | Port — typically `587` for STARTTLS |
| `SMTP_USER` | Login username |
| `SMTP_PASS` | Password or app-specific password (Gmail: create one at myaccount.google.com/apppasswords) |
| `FROM_ADDRESS` | Sender address shown to recipients |
| `TECHKATIVE_INBOX` | Internal notification address |

**Local dev fallback:** if no SMTP vars are set, emails are written to `./outbox/` as `.html` files and logged to the console.

---

## Deploying to Streamlit Community Cloud

1. **Push to GitHub** — push the project to a public or private GitHub repository. The `.gitignore` already excludes `.env` and `secrets.toml`.

2. **Create the app** — go to [share.streamlit.io](https://share.streamlit.io), sign in, click **New app**, and point it at your repo / `app.py`.

3. **Configure secrets** — in the Streamlit Cloud dashboard: **App settings → Secrets**. Paste the contents of `.streamlit/secrets.toml.example` with your real credentials filled in:

   ```toml
   SMTP_HOST = "smtp.gmail.com"
   SMTP_PORT = "587"
   SMTP_USER = "your.address@gmail.com"
   SMTP_PASS = "your_app_password_here"
   FROM_ADDRESS = "diagnostics@techkative.com"
   TECHKATIVE_INBOX = "info@techkative.com"
   ```

4. **Deploy** — click Deploy. Streamlit Cloud will install `requirements.txt` and start the app. The `_load_streamlit_secrets()` function in `app.py` automatically bridges the Cloud secrets into the email pipeline.

> **Note on the logo:** place `assets/logo.png` in the repo before deploying so it appears in the header. The app renders a text fallback if the file is absent.

---

## Adding or editing assessment items

All 24 items, pillar definitions, scoring thresholds, and observation templates live in **`framework.py`**. No application code needs to change when:

- Rewording a question or help text
- Adjusting a 5-point option label
- Changing tier thresholds
- Adding, removing, or reordering pillars or items (also update tests)

The scoring and observation engines read directly from `framework.PILLARS` and `framework.OBSERVATION_RULES`.

---

## Methodology

**Pillar score** = mean(item scores) × 20 → range 20–100

**Composite** = unweighted mean of four pillar scores

**Tiers:**

| Score | Tier |
|---|---|
| 0–39 | Pre-foundational |
| 40–59 | Foundational |
| 60–79 | Developing |
| 80–100 | Mature |

**Observation rules (deterministic, no LLM):**

| Rule | Condition | Pattern |
|---|---|---|
| R1 | Always | Lowest pillar + lowest item spotlight |
| R2 | p1 ≥ 60 AND p2 < 50 | Policy strong, data weak |
| R3 | p1 − p4 ≥ 20 | Ethics below governance |
| R4 | p3 lowest AND composite ≥ 50 AND gap ≥ 15 | Capacity drag |
| R5 | Fallback | Balanced profile |

---

## Deferred to v2

- Database persistence
- PDF report generation
- Admin dashboard
- Multilingual support
- Anonymised aggregate insights
- Authentication

---

## Contact

info@techkative.com
