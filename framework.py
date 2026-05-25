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
            "Does your institution keep a written record of what data it collects about "
            "students, staff, and operations — including where it is stored and who is "
            "allowed to see it?"
        ),
        "hint": (
            "Think of this as a 'what-we-hold' register. A school in Accra or Lagos typically "
            "holds: student admission forms, exam scores, attendance sheets, staff contracts, "
            "and payroll records. A data inventory simply writes all of these down — noting "
            "where each is kept (paper file, spreadsheet, School Management System) and who "
            "is allowed to see them."
        ),
    },
    {
        "id": "df_2",
        "pillar_id": "p1",
        "type": "likert",
        "country": None,
        "text": (
            "How consistently and reliably does your institution record key information — "
            "such as attendance, exam results, and staff performance — across all classes "
            "and departments?"
        ),
        "hint": (
            "This asks whether all teachers and staff record information in the same way. "
            "For example: if one class records attendance on paper, another uses a different "
            "app, and a third only marks absentees — your data is inconsistent. "
            "Inconsistent data cannot power reliable AI tools."
        ),
    },
    {
        "id": "df_3",
        "pillar_id": "p1",
        "type": "yes_no_partial",
        "country": None,
        "text": (
            "Does your institution use standard templates or formats that everyone follows "
            "when recording enrolment, results, or attendance — rather than each person "
            "choosing their own approach?"
        ),
        "hint": (
            "A standard means there is one official format everyone uses. For example: all "
            "teachers enter marks using the same grade sheet with the same fields in the same "
            "order. GES (Ghana) and the Federal Ministry of Education (Nigeria) both recommend "
            "standardised school record templates."
        ),
    },
    {
        "id": "df_4",
        "pillar_id": "p1",
        "type": "yes_no_partial",
        "country": None,
        "text": (
            "If your school switched software provider tomorrow, could you immediately export "
            "and keep all your existing student and staff data in a usable format?"
        ),
        "hint": (
            "Many schools in Accra or Abuja use a local edtech platform. If that provider "
            "goes offline, can you export three years of student results instantly — or would "
            "the data be lost? A usable format means Excel, CSV, or PDF files you own and control."
        ),
    },
    {
        "id": "df_5",
        "pillar_id": "p1",
        "type": "likert",
        "country": None,
        "text": (
            "Is there a named person or role at your institution who is responsible for keeping "
            "data accurate, deciding who can access it, and correcting errors when they occur?"
        ),
        "hint": (
            "In practice: if a student's exam result is entered incorrectly, is there a named "
            "person — such as the head teacher, data clerk, or ICT coordinator — whose specific "
            "job is to fix it and prevent it happening again? Or does responsibility fall "
            "between staff with no clear owner?"
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
            "Does your institution have a written data protection policy explaining what "
            "personal information you collect, why you collect it, how it is kept safe, "
            "and who is allowed to see it?"
        ),
        "hint": (
            "This is a short school rule — not a lengthy legal document — covering four "
            "things: what data you collect, why, how it is stored safely, and who has access. "
            "Under Ghana's Act 843 and Nigeria's NDPA 2023, every organisation collecting "
            "personal data must have one. A one-page version signed by the head teacher is "
            "a valid starting point."
        ),
    },
    {
        "id": "gp_2",
        "pillar_id": "p2",
        "type": "yes_no_partial",
        "country": None,
        "text": (
            "Do you have a written process for getting permission from students, parents, "
            "and staff before collecting their personal information — and for telling them "
            "clearly what it will be used for?"
        ),
        "hint": (
            "Consent means asking for permission before collecting information, and telling "
            "people why. For example: a parent enrolment form in Kumasi or Kano that says "
            "'Your child's photo may appear in our school newsletter — tick here if you agree' "
            "is a simple consent process. Collecting data without this step is a legal risk."
        ),
    },
    {
        "id": "gp_3",
        "pillar_id": "p2",
        "type": "yes_no_partial",
        "country": None,
        "text": (
            "Does your institution have a written step-by-step plan for what to do if "
            "student or staff data is lost, stolen, or accessed without permission?"
        ),
        "hint": (
            "For example: if a laptop with student records is stolen, this plan would say — "
            "who to notify inside the school, how quickly to inform the Data Protection "
            "Commission (Ghana DPC) or NDPC (Nigeria), and how to prevent a repeat. "
            "Without this plan, the response to a data breach is left to chance."
        ),
    },
    {
        "id": "gp_4",
        "pillar_id": "p2",
        "type": "likert",
        "country": None,
        "text": (
            "How openly does your institution inform parents, students, and the wider "
            "community about what data it holds about them and how that data is used?"
        ),
        "hint": (
            "For example: is there a privacy notice on your school's noticeboard, website, "
            "or included in the admission pack? Are parents told if their child's data is "
            "shared with an exam body, an NGO, or a third-party platform? Transparency is "
            "required under both Ghanaian and Nigerian law."
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
            "Commission (DPC), as required by Section 27 of the Data Protection Act, 2012 "
            "(Act 843)?"
        ),
        "hint": (
            "Ghana law requires every organisation that collects personal data — including "
            "schools — to register with the DPC. Registration is completed online at "
            "dataprotection.org.gh. If your school has not registered, this is a legal compliance gap. "
            "Registration fees range from GH₵ 150 to GH₵ 500 depending on "
            "institution size."
        ),
    },
    {
        "id": "gp_6_gh",
        "pillar_id": "p2",
        "type": "yes_no_partial",
        "country": "Ghana",
        "text": (
            "Does your institution hold the DPC Privacy Seal (introduced January 2026) — "
            "or is an application currently in progress?"
        ),
        "hint": (
            "The DPC Privacy Seal is a voluntary certification showing a Ghanaian school "
            "meets data protection standards. To apply, schools must have a registered "
            "policy, appoint a responsible officer, and show how personal data is protected. "
            "It signals trustworthiness to parents, funders, and partner organisations."
        ),
    },
    # Nigeria-specific
    {
        "id": "gp_5_ng",
        "pillar_id": "p2",
        "type": "yes_no_partial",
        "country": "Nigeria",
        "text": (
            "Is your institution registered with Nigeria's National Data Protection Commission "
            "(NDPC) — and if applicable, has it been classified as a Data Controller/Processor "
            "of Major Importance (DCPMI) under GAID 2025?"
        ),
        "hint": (
            "Under Nigeria's NDPA 2023 and GAID 2025 (effective September 2025), schools "
            "handling large volumes of personal data must register with the NDPC. Schools "
            "using AI tools or holding data on many students may be classified as DCPMI with "
            "additional compliance duties. Check ndpc.gov.ng for current registration "
            "thresholds."
        ),
    },
    {
        "id": "gp_6_ng",
        "pillar_id": "p2",
        "type": "yes_no_partial",
        "country": "Nigeria",
        "text": (
            "Has your institution formally appointed a Data Protection Officer (DPO) — a "
            "named person responsible for compliance with Nigeria's data protection law — "
            "with this role documented in writing?"
        ),
        "hint": (
            "A DPO is a named staff member or external consultant responsible for ensuring "
            "the school follows the NDPA 2023. This could be the head teacher, admin officer, "
            "or ICT lead — as long as the role is formally documented. Under the law, schools "
            "processing significant personal data must have one."
        ),
    },
    # Nigeria-specific (continued)
    {
        "id": "gp_7_ng",
        "pillar_id": "p2",
        "type": "yes_no_partial",
        "country": "Nigeria",
        "text": (
            "Has your institution completed a Data Protection Impact Assessment (DPIA) for "
            "high-risk activities involving student or staff data — such as using AI tools, "
            "biometric attendance systems, or processing children's data at scale?"
        ),
        "hint": (
            "A DPIA is a structured risk assessment done before starting activities that pose "
            "high privacy risks. Under GAID 2025, schools using AI tools or processing "
            "children's data are likely to trigger this requirement. For example: before "
            "deploying an AI-powered student performance tracking system in Lagos or Kano, "
            "a DPIA would assess what data is collected, the privacy risks, and how they are "
            "mitigated. If your school uses any AI tools and has not done a DPIA, this is "
            "a compliance gap under Nigerian law."
        ),
    },
    {
        "id": "gp_8_ng",
        "pillar_id": "p2",
        "type": "yes_no_partial",
        "country": "Nigeria",
        "text": (
            "Does your institution maintain a Record of Processing Activities (RoPA) — a "
            "living document listing every way you collect, use, store, and share personal "
            "data — updated at least every six months?"
        ),
        "hint": (
            "A RoPA is a master log of what your institution does with personal data. Under "
            "NDPA 2023 / GAID 2025, schools must keep this up to date. For example: a school "
            "in Abuja would list in its RoPA — student admissions, payroll, exam result "
            "sharing with WAEC/NECO, CCTV footage, and any third-party ed-tech platforms — "
            "with the date it was last reviewed. It is a practical compliance tool and a "
            "core accountability requirement for your appointed DPO."
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
            "Does your institution have a written plan that sets out which AI tools will be "
            "used, what they will be used for, who is responsible for overseeing them, and "
            "how student data will be protected?"
        ),
        "hint": (
            "An AI strategy does not need to be a lengthy document. A one-page plan approved "
            "by school leadership is sufficient. For example: a secondary school in Accra or "
            "Lagos using an AI-assisted marking tool should document the tool's purpose, the "
            "teacher oversight required, and how student data is protected — signed off by "
            "the head teacher."
        ),
    },
    {
        "id": "ar_2",
        "pillar_id": "p3",
        "type": "likert",
        "country": None,
        "text": (
            "How clearly has your institution identified the specific problems it wants AI "
            "to solve — such as reducing administrative work, improving student feedback, "
            "or identifying learners who need extra support?"
        ),
        "hint": (
            "'We want to use AI' is not a clear use-case. A clear example is: 'We want AI "
            "to send weekly SMS alerts to parents of students who miss more than three days "
            "of school.' That is specific, measurable, and actionable. Vague goals lead to "
            "poor AI choices and wasted resources."
        ),
    },
    {
        "id": "ar_3",
        "pillar_id": "p3",
        "type": "yes_no_partial",
        "country": None,
        "text": (
            "Does your institution have staff with the digital or technical skills to set up "
            "and oversee AI tools responsibly — or reliable external partners who can provide "
            "this support?"
        ),
        "hint": (
            "You do not need a full data science team. This could be a contracted ed-tech "
            "vendor, a teacher with digital skills who manages the tools, or a university or "
            "NGO partnership. For example: a school in Port Harcourt or Tamale partnering "
            "with a local IT firm — with at least one staff member trained to oversee the "
            "platform day-to-day."
        ),
    },
    {
        "id": "ar_4",
        "pillar_id": "p3",
        "type": "likert",
        "country": None,
        "text": (
            "Before adopting any new AI tool, how thoroughly does your institution ask "
            "critical questions — such as whether AI is the right solution, what data will "
            "be collected, and whether a simpler approach could achieve the same result?"
        ),
        "hint": (
            "For example: before signing up to an AI-powered attendance system, does a "
            "senior staff member check — what data does it collect, is sharing student "
            "biometric data with this vendor proportionate, and could a well-designed "
            "spreadsheet or teacher-led process achieve the same goal at lower risk?"
        ),
    },
    {
        "id": "ar_5",
        "pillar_id": "p3",
        "type": "yes_no_partial",
        "country": None,
        "text": (
            "When selecting an AI vendor or platform, does your institution require the "
            "provider to explain how their system was built, what data it uses, and where "
            "student data will be stored and protected?"
        ),
        "hint": (
            "Many free or low-cost ed-tech platforms across Africa do not disclose this by "
            "default. For example: before a Ghanaian or Nigerian school signs up to an AI "
            "grading platform, does the procurement process ask the vendor to confirm that "
            "the AI was not trained on your students' data without consent, and that data "
            "is stored on servers with adequate legal protections?"
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
            "Does your institution have a process for checking whether AI tools produce fair "
            "results for all students — including across different genders, languages, "
            "abilities, and backgrounds?"
        ),
        "hint": (
            "AI tools can produce unfair results without anyone intending it. For example: "
            "an AI reading assessment trained on English-medium data may systematically "
            "underrate students whose home language is Twi, Yoruba, Hausa, or Igbo. Does "
            "your school check AI recommendations across student groups — even informally?"
        ),
    },
    {
        "id": "rd_2",
        "pillar_id": "p4",
        "type": "likert",
        "country": None,
        "text": (
            "If an AI tool produced a result affecting a student or staff member — such as "
            "a grade, risk flag, or recommendation — how clearly could a teacher explain to "
            "that person specifically why that result was produced?"
        ),
        "hint": (
            "If the best answer is 'the system gave us that result', your AI tool lacks "
            "explainability. For example: if an AI platform recommends a student be placed "
            "in a remedial class, a teacher should be able to explain to the parent which "
            "specific factors (attendance, test scores, submission rate) influenced that "
            "recommendation — in plain language, without jargon."
        ),
    },
    {
        "id": "rd_3",
        "pillar_id": "p4",
        "type": "yes_no_partial",
        "country": None,
        "text": (
            "Before acting on any AI-generated recommendation — such as a student placement "
            "decision, performance flag, or resource allocation — is a human required to "
            "review and approve it?"
        ),
        "hint": (
            "AI tools can and do make mistakes, especially in African school contexts where "
            "training data is limited. For example: if an AI tool recommends a student "
            "repeat a class, should the head teacher or a review committee formally confirm "
            "this before the student is informed? Human oversight prevents errors from "
            "becoming unfair outcomes."
        ),
    },
    {
        "id": "rd_4",
        "pillar_id": "p4",
        "type": "yes_no_partial",
        "country": None,
        "text": (
            "Does your institution have a written process for students, parents, or staff "
            "to challenge or appeal a decision that was influenced by an AI tool?"
        ),
        "hint": (
            "For example: if an AI attendance system marks a student as absent when they "
            "were present, is there a clear formal route for the parent to raise this and "
            "have the record corrected? Without a complaints process, affected families have "
            "no recourse — which is a rights issue under both Ghanaian and Nigerian law."
        ),
    },
    {
        "id": "rd_5",
        "pillar_id": "p4",
        "type": "yes_no_partial",
        "country": None,
        "text": (
            "Is your institution's student and operational data stored on servers that are "
            "governed by African or local law — rather than solely on platforms based in "
            "the US, Europe, or other regions outside Africa?"
        ),
        "hint": (
            "Data sovereignty means your school's data is subject to African or local laws, "
            "not solely foreign frameworks. For example: a Ghanaian school storing all "
            "student data on US-based servers means that data is governed primarily by US "
            "law, limiting Ghana's Act 843 protections. The Africa Declaration on AI "
            "(Kigali, April 2025) calls on African institutions to prioritise locally or "
            "regionally governed data infrastructure."
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
        "**Ghana respondents:** this collection is conducted under the lawful processing "
        "basis in the Data Protection Act, 2012 (Act 843 §18). Cross-border data transfers "
        "are subject to Act 843 §30(4) — your data is processed within Ghana-governed "
        "infrastructure where practicable. "
        "**Nigeria respondents:** this collection is conducted in alignment with NDPA 2023 "
        "and the GAID 2025 Article 18 cross-border transfer obligations — your data stays "
        "within Nigeria-governed infrastructure where practicable. "
        "**Continental context:** aligned with the Africa Declaration on AI, Kigali, "
        "4 April 2025."
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
