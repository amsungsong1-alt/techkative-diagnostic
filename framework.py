"""
Tech-Kative AI-Readiness Diagnostic v2 — Framework Definition

Single source of truth for the diagnostic methodology, question bank,
scoring constants, and tier-based recommendations.

Regulatory anchors:
  Ghana:     Data Protection Act, 2012 (Act 843) | DPC Privacy Seal (January 2026)
  Nigeria:   NDPA 2023 / GAID 2025 (effective 19 September 2025)
  Continental: Africa Declaration on AI (Kigali, 4 April 2025)
               AU Continental AI Strategy (2024)
  Ghana AI:  Ghana National AI Strategy 2025-2035 (launched 24 April 2026)
"""

# ---------------------------------------------------------------------------
# Question type constants
# ---------------------------------------------------------------------------

YES_NO_OPTIONS     = ["Yes", "Partial", "No"]
FOUR_OPTION_LIKERT = ["Not yet", "Beginning", "Established", "Leading"]

YES_NO_SCORES  = {"Yes": 1.0, "Partial": 0.5, "No": 0.0}
LIKERT_SCORES  = {"Not yet": 0.0, "Beginning": 0.33, "Established": 0.67, "Leading": 1.0}

# ---------------------------------------------------------------------------
# Tier bands (Emerging / Developing / Established / Leading)
# ---------------------------------------------------------------------------

TIERS = [
    {"label": "Emerging",    "min": 0,  "max": 24,  "colour": "#b8651f"},
    {"label": "Developing",  "min": 25, "max": 49,  "colour": "#8b3fb8"},
    {"label": "Established", "min": 50, "max": 74,  "colour": "#2d8659"},
    {"label": "Leading",     "min": 75, "max": 100, "colour": "#1a1f3a"},
]

# ---------------------------------------------------------------------------
# Pilot codes — Tech-Kative x Standbasis joint pilot (June-July 2026)
# ---------------------------------------------------------------------------

PILOT_CODES = {"TKSB-GH-001", "TKSB-NG-001"}

# ---------------------------------------------------------------------------
# Pillar colours and order
# ---------------------------------------------------------------------------

PILLAR_COLOURS = {
    "p1": "#8b3fb8",  # purple  — Data Foundations
    "p2": "#1a1f3a",  # navy    — Governance & Protection
    "p3": "#2d8659",  # green   — AI Readiness
    "p4": "#b8651f",  # amber   — Responsible Deployment
}

PILLAR_ORDER = ["p1", "p2", "p3", "p4"]

# ---------------------------------------------------------------------------
# Dropdown options
# ---------------------------------------------------------------------------

INSTITUTION_TYPES = [
    "University / Tertiary Institution",
    "Polytechnic / Technical College",
    "Secondary School / High School",
    "Primary / Basic School",
    "Special Needs / Inclusive Education Institution",
    "Government Education Agency (MDA)",
    "NGO / Education Development Partner",
    "Other",
]

COUNTRY_OPTIONS = [
    "Ghana",
    "Nigeria",
    "Kenya",
    "South Africa",
    "Rwanda",
    "Ethiopia",
    "Senegal",
    "Tanzania",
    "Uganda",
    "Zambia",
    "Other",
]

# ---------------------------------------------------------------------------
# Pillar metadata (no embedded items — questions live in flat QUESTIONS list)
# ---------------------------------------------------------------------------

PILLARS = [
    {
        "id": "p1",
        "name": "Data Foundations",
        "short_name": "Data",
        "description": (
            "Whether the institution systematically collects, records, owns, and can export "
            "its data in a form that supports responsible AI use."
        ),
        "colour": PILLAR_COLOURS["p1"],
    },
    {
        "id": "p2",
        "name": "Governance & Protection",
        "short_name": "Governance",
        "description": (
            "Policies, consent procedures, incident response, and alignment with applicable "
            "national data protection law (Ghana Act 843; Nigeria NDPA 2023 / GAID 2025)."
        ),
        "colour": PILLAR_COLOURS["p2"],
    },
    {
        "id": "p3",
        "name": "AI Readiness",
        "short_name": "AI Readiness",
        "description": (
            "Whether the institution has a documented strategy, clear use-cases, technical "
            "capacity, and rigorous vendor evaluation processes for AI adoption."
        ),
        "colour": PILLAR_COLOURS["p3"],
    },
    {
        "id": "p4",
        "name": "Responsible Deployment",
        "short_name": "Deployment",
        "description": (
            "Bias checking, explainability, human oversight, recourse mechanisms, and data "
            "sovereignty — the operational layer that makes AI use defensible."
        ),
        "colour": PILLAR_COLOURS["p4"],
    },
]

# ---------------------------------------------------------------------------
# Question bank
# type:    "yes_no_partial" | "likert" (4-option) | "open_text" (not scored)
# country: None = universal; "Ghana" | "Nigeria" = shown only for that country
# ---------------------------------------------------------------------------

QUESTIONS = [

    # ── Pillar 1: Data Foundations ──────────────────────────────────────────
    {
        "id": "df_1",
        "pillar_id": "p1",
        "type": "yes_no_partial",
        "country": None,
        "text": (
            "Does your institution maintain a documented inventory of the data it collects "
            "from students, staff, and operations — including what is collected, where it is "
            "stored, and who has access?"
        ),
    },
    {
        "id": "df_2",
        "pillar_id": "p1",
        "type": "likert",
        "country": None,
        "text": (
            "How would you rate the consistency and reliability of how data is collected and "
            "recorded across your institution (e.g., attendance, assessments, teacher "
            "performance, student records)?"
        ),
    },
    {
        "id": "df_3",
        "pillar_id": "p1",
        "type": "yes_no_partial",
        "country": None,
        "text": (
            "Does your institution have documented standards or templates for how core data "
            "(enrolment, results, attendance) is recorded and maintained?"
        ),
    },
    {
        "id": "df_4",
        "pillar_id": "p1",
        "type": "yes_no_partial",
        "country": None,
        "text": (
            "If your institution stopped using its current digital systems or vendors tomorrow, "
            "could you export and retain all of your data in a usable format?"
        ),
    },
    {
        "id": "df_5",
        "pillar_id": "p1",
        "type": "likert",
        "country": None,
        "text": (
            "How clearly is ownership of institutional data assigned — i.e., who is accountable "
            "for data quality, access decisions, and corrections when something goes wrong?"
        ),
    },
    {
        "id": "df_6",
        "pillar_id": "p1",
        "type": "open_text",
        "country": None,
        "text": (
            "Briefly describe the biggest data-related challenge your institution faces today. "
            "(Optional — not scored)"
        ),
    },

    # ── Pillar 2: Governance & Protection ──────────────────────────────────
    {
        "id": "gp_1",
        "pillar_id": "p2",
        "type": "yes_no_partial",
        "country": None,
        "text": (
            "Does your institution have a written data protection policy that covers how "
            "personal data is collected, used, stored, and shared?"
        ),
    },
    {
        "id": "gp_2",
        "pillar_id": "p2",
        "type": "yes_no_partial",
        "country": None,
        "text": (
            "Do you have documented consent procedures for collecting personal data from "
            "students, parents, and staff — including a clear statement of purpose?"
        ),
    },
    {
        "id": "gp_3",
        "pillar_id": "p2",
        "type": "yes_no_partial",
        "country": None,
        "text": (
            "Is there a documented incident response procedure if data is lost, stolen, "
            "or accessed without authorisation?"
        ),
    },
    {
        "id": "gp_4",
        "pillar_id": "p2",
        "type": "likert",
        "country": None,
        "text": (
            "How transparently does your institution communicate its data practices to parents, "
            "students, and the wider school community?"
        ),
    },
    # Ghana-specific
    {
        "id": "gp_5_gh",
        "pillar_id": "p2",
        "type": "yes_no_partial",
        "country": "Ghana",
        "text": (
            "Is your institution registered as a data controller with Ghana's Data Protection "
            "Commission (DPC), as required under §27 of the Data Protection Act, 2012 (Act 843)?"
        ),
    },
    {
        "id": "gp_6_gh",
        "pillar_id": "p2",
        "type": "yes_no_partial",
        "country": "Ghana",
        "text": (
            "Does your institution hold the DPC Privacy Seal (effective January 2026), "
            "or is an application in progress?"
        ),
    },
    # Nigeria-specific
    {
        "id": "gp_5_ng",
        "pillar_id": "p2",
        "type": "yes_no_partial",
        "country": "Nigeria",
        "text": (
            "Is your institution registered with Nigeria's Data Protection Commission (NDPC), "
            "and if so, classified as a Data Controller/Processor of Major Importance (DCPMI) "
            "under GAID 2025?"
        ),
    },
    {
        "id": "gp_6_ng",
        "pillar_id": "p2",
        "type": "yes_no_partial",
        "country": "Nigeria",
        "text": (
            "Has a Data Protection Officer (DPO) been formally designated at your institution, "
            "with documented responsibility for compliance reporting?"
        ),
    },
    # Universal open-text
    {
        "id": "gp_7",
        "pillar_id": "p2",
        "type": "open_text",
        "country": None,
        "text": (
            "What is the most pressing data protection or governance concern at your institution "
            "today? (Optional — not scored)"
        ),
    },

    # ── Pillar 3: AI Readiness ─────────────────────────────────────────────
    {
        "id": "ar_1",
        "pillar_id": "p3",
        "type": "yes_no_partial",
        "country": None,
        "text": (
            "Does your institution have a documented AI strategy or written plan that defines "
            "how and where AI tools will be used?"
        ),
    },
    {
        "id": "ar_2",
        "pillar_id": "p3",
        "type": "likert",
        "country": None,
        "text": (
            "How clearly defined are the specific problems or use-cases your institution wants "
            "AI to address (e.g., personalised learning, administrative efficiency, student support)?"
        ),
    },
    {
        "id": "ar_3",
        "pillar_id": "p3",
        "type": "yes_no_partial",
        "country": None,
        "text": (
            "Does your institution have technical staff or external partners with the expertise "
            "to implement and oversee AI tools responsibly?"
        ),
    },
    {
        "id": "ar_4",
        "pillar_id": "p3",
        "type": "likert",
        "country": None,
        "text": (
            "Before adopting an AI tool, how rigorously does your institution evaluate whether "
            "AI is the right solution — including consideration of simpler, non-AI alternatives?"
        ),
    },
    {
        "id": "ar_5",
        "pillar_id": "p3",
        "type": "yes_no_partial",
        "country": None,
        "text": (
            "Does your institution's procurement or technology decision process require AI vendors "
            "to disclose how their systems were trained, what data they use, and where that "
            "data is stored?"
        ),
    },
    {
        "id": "ar_6",
        "pillar_id": "p3",
        "type": "open_text",
        "country": None,
        "text": (
            "What AI capability would be most valuable to your institution if it could be "
            "implemented responsibly? (Optional — not scored)"
        ),
    },

    # ── Pillar 4: Responsible Deployment ───────────────────────────────────
    {
        "id": "rd_1",
        "pillar_id": "p4",
        "type": "yes_no_partial",
        "country": None,
        "text": (
            "Does your institution have a documented process to check whether AI tools produce "
            "fair outcomes across different groups of students "
            "(gender, language, ability, background)?"
        ),
    },
    {
        "id": "rd_2",
        "pillar_id": "p4",
        "type": "likert",
        "country": None,
        "text": (
            "If an AI tool made a decision that affected a student or teacher, how clearly could "
            "a staff member explain to that person why the decision was made?"
        ),
    },
    {
        "id": "rd_3",
        "pillar_id": "p4",
        "type": "yes_no_partial",
        "country": None,
        "text": (
            "Is human review and approval required before AI-generated decisions are acted upon "
            "(e.g., for student placement, performance flags, or resource allocation)?"
        ),
    },
    {
        "id": "rd_4",
        "pillar_id": "p4",
        "type": "yes_no_partial",
        "country": None,
        "text": (
            "Does your institution have a documented way for students, parents, or staff to "
            "challenge or appeal an AI-influenced decision they believe is unfair?"
        ),
    },
    {
        "id": "rd_5",
        "pillar_id": "p4",
        "type": "yes_no_partial",
        "country": None,
        "text": (
            "Are student data and operational data stored on locally governed or "
            "African-headquartered infrastructure, consistent with the data sovereignty "
            "commitments of the Africa Declaration on AI (Kigali, 4 April 2025)?"
        ),
    },
    {
        "id": "rd_6",
        "pillar_id": "p4",
        "type": "open_text",
        "country": None,
        "text": (
            "What is your biggest concern about deploying AI in your institution? "
            "(Optional — not scored)"
        ),
    },
]

# ---------------------------------------------------------------------------
# Recommendations — 4 pillars x 4 tiers x 3 action items
# ---------------------------------------------------------------------------

RECOMMENDATIONS = {
    "p1": {
        "Emerging": [
            "Begin a basic data inventory this term: list every form of student, staff, and "
            "operational data your institution collects (paper or digital), where it is stored, "
            "and who can access it. A spreadsheet is sufficient to start.",
            "Designate one staff member — ideally a senior administrator — as the institution's "
            "data steward. Their role is to be the single point of accountability for data "
            "quality and access decisions.",
            "Identify the three most important datasets at your institution (e.g., enrolment, "
            "attendance, results) and document a one-page standard for how each is recorded "
            "and maintained.",
        ],
        "Developing": [
            "Convert your data inventory into a working data dictionary that all relevant staff "
            "can access. Include data definitions, retention periods, and access permissions.",
            "Establish a quarterly data quality check: a 30-minute review of completeness and "
            "accuracy in your three priority datasets, with documented corrections.",
            "Run a 'vendor exit' exercise: pick one digital tool you use and confirm you could "
            "export all your data from it in under one week. Document the export process.",
        ],
        "Established": [
            "Automate routine data quality checks where possible (e.g., flagging missing fields "
            "or outlier values on entry). For paper-based systems, build the check into the "
            "weekly admin workflow.",
            "Document inter-departmental data agreements that clarify who owns which datasets "
            "and who has authority to grant access — especially across teaching, finance, and "
            "pastoral care.",
            "Pilot a data portability test with a new vendor: require that any new system commit "
            "in writing to data export in standard formats before procurement.",
        ],
        "Leading": [
            "Publish an annual internal data report to staff and governors covering data quality, "
            "access events, and any incidents. Treat transparency as a feature of strong "
            "data culture.",
            "Contribute to sector-wide standards: share your data dictionary template with peer "
            "institutions or your education association, and adopt incoming improvements.",
            "Evaluate emerging school data platforms aligned with Ghana's National AI Strategy "
            "2025-2035 'data as national asset' pillar or NaCCA standards, and pilot one that "
            "strengthens interoperability with national education systems.",
        ],
    },
    "p2": {
        "Emerging": [
            "Draft a one-page institutional data protection policy this term covering: what data "
            "is collected, why, who can access it, how long it is kept, and how someone can "
            "request their data. Adapt from your national regulator's template (Ghana DPC or "
            "Nigeria NDPC).",
            "Begin the registration process with your national data protection authority: Ghana's "
            "Data Protection Commission under the Data Protection Act, 2012 (Act 843), or "
            "Nigeria's Data Protection Commission under NDPA 2023 / GAID 2025.",
            "Build a basic consent statement into all new data-collection forms (enrolment, "
            "parental contact, photo permissions) that clearly states purpose and who controls "
            "the data.",
        ],
        "Developing": [
            "Conduct a privacy walkthrough: for every digital tool in use, document what personal "
            "data flows into it, where the vendor stores it, and what your contract says about "
            "access and deletion.",
            "Develop and test a basic incident response procedure: who is called first if data "
            "is compromised, what is documented, and what is communicated to affected people.",
            "If operating in Nigeria, begin scoping a Data Protection Impact Assessment (DPIA) "
            "for your highest-risk system, as required by GAID 2025. If in Ghana, prepare your "
            "DPC Privacy Seal application materials.",
        ],
        "Established": [
            "Establish a small data governance committee (3-4 people including a senior leader, "
            "a teacher, and an administrator) that meets termly to review policy compliance "
            "and incidents.",
            "Run an annual privacy training for all staff handling student or parent data. "
            "Document attendance and refresh content yearly.",
            "Designate a Data Protection Officer or named privacy lead with a written role "
            "description, and ensure their work is reflected in semi-annual compliance reporting "
            "(GAID 2025 requirement in Nigeria).",
        ],
        "Leading": [
            "Publish a public-facing privacy notice that clearly explains data practices in "
            "language accessible to parents and students. Make it available on your institution's "
            "website or main entry point.",
            "Beyond regulatory compliance, develop institutional ethical guidelines for data use "
            "that reflect your school's community values (e.g., commitments around children's "
            "data, family privacy, or vulnerable students).",
            "Lead or contribute to sector-wide convenings on school data governance, partnering "
            "with national regulators, peer schools, or civil society organisations working on "
            "children's data rights.",
        ],
    },
    "p3": {
        "Emerging": [
            "Before considering any AI tool, write a one-page document answering: what problem "
            "are we trying to solve, who benefits, and what would success look like? Many AI "
            "projects fail because this step is skipped.",
            "Conduct a basic readiness audit: do you have reliable data (Pillar 1), governance "
            "in place (Pillar 2), and the staff capacity to oversee AI tools? If any answer is "
            "no, address those first.",
            "Educate your leadership team on what AI can and cannot do. Aim for one 90-minute "
            "literacy session this term that includes realistic cost, timeline, and "
            "failure-mode discussion.",
        ],
        "Developing": [
            "Draft a one-to-two page institutional AI strategy that names: priority use-cases, "
            "success metrics, who owns AI decisions, and what is explicitly out of scope.",
            "Build internal capacity through one of three routes: train an existing technical "
            "staff member, partner with a local AI-literate consultant, or join a community of "
            "practice with peer institutions.",
            "Pilot one small, low-risk AI use case (e.g., administrative scheduling, content "
            "drafting) with clear evaluation criteria. Document what worked, what did not, and "
            "what was learned about your institutional readiness.",
        ],
        "Established": [
            "Institutionalise AI procurement standards: require any AI vendor to disclose "
            "training data sources, intended use, known limitations, and data storage location "
            "before procurement.",
            "Develop a use-case evaluation framework: a short checklist your AI committee uses "
            "to screen new ideas for feasibility, alignment with strategy, and proportionality "
            "of risk.",
            "Align your AI plans with Ghana's National AI Strategy 2025-2035 four pillars "
            "(data, compute, talent, governance) or relevant Nigerian frameworks to position "
            "your institution for sector partnerships and funding.",
        ],
        "Leading": [
            "Scale your most successful AI pilot to a second use-case or department, with "
            "documented lessons learned and clear stop conditions.",
            "Contribute to sector knowledge: publish a case study, present at a conference, or "
            "share your evaluation framework with peer institutions or your national AI strategy "
            "implementation group.",
            "Establish strategic partnerships with African research institutions, universities, "
            "or AI organisations to keep your institution at the frontier of responsible AI "
            "in education.",
        ],
    },
    "p4": {
        "Emerging": [
            "Before deploying any AI tool, establish a basic accountability map: name the person "
            "who can override the AI, name the person who can be appealed to, and document "
            "both in writing.",
            "Conduct a simple fairness check on any AI tool already in use: ask whether outcomes "
            "differ across student groups (gender, language background, ability) and document "
            "what you find.",
            "Write a one-page statement of AI limitations for your institution: what the AI tool "
            "you use can do well, what it cannot do, and what kinds of decisions must always "
            "remain human.",
        ],
        "Developing": [
            "Implement an explainability requirement: any staff member using an AI tool to inform "
            "a decision must be able to explain in plain language why the AI gave that output. "
            "Test this with a real example.",
            "Establish a human-in-the-loop policy for all AI-influenced decisions affecting "
            "students (placement, performance flags, support recommendations). Require documented "
            "human review before any consequential action.",
            "Train all staff who use AI tools on responsible deployment principles, including "
            "bias, limitations, and the appeals process. Document training in personnel records.",
        ],
        "Established": [
            "Integrate responsible AI checks into your standard project review process: every "
            "new AI deployment gets a responsibility review before launch.",
            "Establish a documented appeals process: how students, parents, or staff can formally "
            "challenge an AI-influenced decision, who reviews the challenge, and what the "
            "timeline is for a response.",
            "Monitor AI systems in active use: review outputs quarterly for fairness drift, "
            "accuracy decline, or emerging issues. Document and respond to what you find.",
        ],
        "Leading": [
            "Embed responsible AI in your institutional identity, not just your policies. "
            "Communicate it externally to parents, the community, and prospective partners as "
            "part of how your institution operates.",
            "Contribute to the field: share frameworks, evaluation tools, or training materials "
            "with peer institutions, research bodies, or national education authorities working "
            "on AI in schools.",
            "Lead advocacy on responsible AI in education, particularly as it affects vulnerable "
            "populations. Partner with civil society, national regulators, or bodies aligned "
            "with the Africa Declaration on AI (Kigali, 4 April 2025) on policy positions.",
        ],
    },
}

# ---------------------------------------------------------------------------
# Privacy notice paragraphs (displayed on consent screen)
# ---------------------------------------------------------------------------

PRIVACY_NOTICE_PARAGRAPHS = [
    (
        "This diagnostic is operated by **Tech-Kative** (Accra, Ghana). "
        "When you complete the diagnostic, the following information is stored: "
        "your organisation name, type, country, and your role; your responses to all "
        "diagnostic questions; the maturity scores calculated from your responses; "
        "and the date and time of completion."
    ),
    (
        "**What we do with this data:** Generate your personalised HTML report; produce "
        "anonymous aggregated insights for research on AI readiness in African education; "
        "and (if a valid pilot code is entered) use the data for the "
        "Tech-Kative x Standbasis joint pilot research."
    ),
    (
        "**What we do NOT do:** Share your individual responses with any third party; "
        "use your data for marketing; or store any personal identifying information "
        "beyond what you provide."
    ),
    (
        "**Your rights:** You may request deletion of your data at any time by emailing "
        "info@techkative.com. "
        "For Ghana respondents: this collection is conducted in alignment with the "
        "Data Protection Act, 2012 (Act 843). "
        "For Nigeria respondents: this collection is conducted in alignment with "
        "NDPA 2023 / GAID 2025."
    ),
    (
        "By proceeding, you confirm that you have authority to complete this diagnostic "
        "on behalf of your institution."
    ),
]

# ---------------------------------------------------------------------------
# Convenience helpers
# ---------------------------------------------------------------------------

PILLAR_INTRODUCTIONS = {
    "p1": (
        "This section explores how reliably your institution captures and manages the data "
        "it produces. Strong data foundations are the prerequisite for any meaningful AI work "
        "— and for compliance with national data protection law."
    ),
    "p2": (
        "This section examines how your institution protects personal data and complies with "
        "applicable regulations. For schools, this is non-negotiable: student data is among "
        "the most sensitive categories under Ghana's Act 843 and Nigeria's NDPA 2023."
    ),
    "p3": (
        "This section assesses whether your institution has the strategy, expertise, and "
        "discipline to adopt AI tools responsibly. Readiness is not about having AI yet — "
        "it is about being able to evaluate AI offers critically."
    ),
    "p4": (
        "This section explores whether your institution can deploy AI in ways that are fair, "
        "explainable, and accountable to the students and families it serves. This is where "
        "most school-level AI projects fail without preparation."
    ),
}


def get_pillar(pillar_id: str) -> dict:
    for p in PILLARS:
        if p["id"] == pillar_id:
            return p
    raise KeyError(f"Unknown pillar id: {pillar_id}")


def get_question(question_id: str) -> dict:
    for q in QUESTIONS:
        if q["id"] == question_id:
            return q
    raise KeyError(f"Unknown question id: {question_id}")


def get_questions_for_user(country: str) -> list:
    """Universal questions plus country-matched questions."""
    return [q for q in QUESTIONS if q["country"] is None or q["country"] == country]


def get_scored_questions(country: str) -> list:
    """Questions that contribute to scores (excludes open_text)."""
    return [q for q in get_questions_for_user(country) if q["type"] != "open_text"]


def all_scored_question_ids(country: str) -> list:
    return [q["id"] for q in get_scored_questions(country)]


def get_tier(score: float) -> dict:
    for tier in TIERS:
        if tier["min"] <= score <= tier["max"]:
            return tier
    return TIERS[-1]
