"""
Tech-Kative AI-Readiness Diagnostic — Framework Definition

This module is the single source of truth for the diagnostic methodology.
Edit here to evolve the item bank, scoring thresholds, or observation templates
without touching any application or scoring code.
"""

# ---------------------------------------------------------------------------
# Scoring constants
# ---------------------------------------------------------------------------

SCORE_SCALE_FACTOR = 20  # pillar score = mean(item scores) × 20 → range 20–100

TIERS = [
    {"label": "Pre-foundational", "min": 0,  "max": 39,  "colour": "#b8651f"},
    {"label": "Foundational",     "min": 40, "max": 59,  "colour": "#8b3fb8"},
    {"label": "Developing",       "min": 60, "max": 79,  "colour": "#2d8659"},
    {"label": "Mature",           "min": 80, "max": 100, "colour": "#1a1f3a"},
]

PILLAR_COLOURS = {
    "p1": "#8b3fb8",  # purple/magenta — Governance & Policy
    "p2": "#1a1f3a",  # deep navy      — Data Foundations
    "p3": "#2d8659",  # accent green   — Organisational Capacity
    "p4": "#b8651f",  # warm amber     — Ethical Infrastructure
}

PILLAR_ORDER = ["p1", "p2", "p3", "p4"]

# ---------------------------------------------------------------------------
# Institution types (profile screen)
# ---------------------------------------------------------------------------

INSTITUTION_TYPES = [
    "University / Tertiary Institution",
    "Polytechnic / Technical College",
    "Secondary School / High School",
    "Primary School",
    "Special Needs / Inclusive Education Institution",
    "Government Education Agency (MDA)",
    "NGO / Education Development Partner",
    "Other",
]

# ---------------------------------------------------------------------------
# Helper: build a 5-option list from labels
# ---------------------------------------------------------------------------

def _opts(*labels):
    return [{"score": i + 1, "label": label} for i, label in enumerate(labels)]


# ---------------------------------------------------------------------------
# Item bank — four pillars, six items each
# ---------------------------------------------------------------------------

PILLARS = [
    # -----------------------------------------------------------------------
    # Pillar 1 — Governance & Policy
    # -----------------------------------------------------------------------
    {
        "id": "p1",
        "name": "Governance & Policy",
        "short_name": "Governance",
        "description": (
            "Data protection alignment, consent architecture, accountability lines, "
            "decision rights, and regulatory posture against NDPR and equivalent African regimes."
        ),
        "colour": PILLAR_COLOURS["p1"],
        "items": [
            {
                "id": "1.1",
                "pillar_id": "p1",
                "sequence": 1,
                "short_label": "External data sharing governance",
                "question": (
                    "When student or teacher data is shared with a ministry, "
                    "government agency (MDA), or external partner, how is that data flow governed?"
                ),
                "help_text": (
                    "Consider whether a documented data-sharing protocol exists, who has authority "
                    "to authorise the flow, what consent basis applies, and whether the institution "
                    "retains visibility into downstream use of the data. Select the option that most "
                    "accurately describes current practice — not aspiration."
                ),
                "options": _opts(
                    "No protocol exists; data is shared on request without formal process.",
                    "Data is shared informally based on verbal agreements or individual judgment.",
                    "A sharing protocol exists on paper but is not consistently followed.",
                    "A documented protocol is in place and applied to all external data transfers.",
                    "Protocol is documented, consistently applied, and periodically audited; downstream use is tracked.",
                ),
            },
            {
                "id": "1.2",
                "pillar_id": "p1",
                "sequence": 2,
                "short_label": "Consent collection and recording",
                "question": (
                    "When personal data is collected from students, parents, or staff, "
                    "how is informed consent obtained and recorded?"
                ),
                "help_text": (
                    "Consider whether consent is sought before collection, whether the purpose "
                    "is clearly explained in plain language, how consent records are stored, and "
                    "whether withdrawal of consent is supported. Select the option that most "
                    "accurately describes current practice — not aspiration."
                ),
                "options": _opts(
                    "No consent process exists; data is collected without notification.",
                    "Consent is assumed or obtained verbally without records.",
                    "A consent form exists but is not consistently used or stored.",
                    "Consent is formally sought, recorded, and linked to specific data processing purposes.",
                    "Consent records are systematically maintained and reviewed; consent withdrawal is operationally supported.",
                ),
            },
            {
                "id": "1.3",
                "pillar_id": "p1",
                "sequence": 3,
                "short_label": "Incident accountability and escalation",
                "question": (
                    "When a data-related incident occurs — such as a breach, misuse, or loss — "
                    "how is accountability determined and escalation managed?"
                ),
                "help_text": (
                    "Consider whether there is a named data protection officer or equivalent role, "
                    "whether an incident response procedure exists, and how incidents are communicated "
                    "to affected parties and regulators. Select the option that most accurately "
                    "describes current practice — not aspiration."
                ),
                "options": _opts(
                    "No accountability structure exists; incidents are handled ad hoc.",
                    "A person is informally responsible but no response procedure exists.",
                    "An accountability structure is documented but not consistently activated during incidents.",
                    "Roles, escalation paths, and notification obligations are documented and applied.",
                    "All of the above, plus regular incident response drills; post-incident reviews inform policy updates.",
                ),
            },
            {
                "id": "1.4",
                "pillar_id": "p1",
                "sequence": 4,
                "short_label": "AI procurement decision rights",
                "question": (
                    "When decisions are made about which AI tools or data systems to procure or adopt, "
                    "how are decision rights distributed across the institution?"
                ),
                "help_text": (
                    "Consider who has authority to approve AI procurement, whether ICT, academic, "
                    "and administrative leadership are involved, and whether there is a formal "
                    "evaluation or approval process. Select the option that most accurately "
                    "describes current practice — not aspiration."
                ),
                "options": _opts(
                    "Procurement decisions are made individually without institutional oversight.",
                    "Decisions are made by one department without cross-functional input.",
                    "A review process exists but participation is inconsistent; decisions sometimes bypass it.",
                    "Decision rights are defined, documented, and a multi-stakeholder review process is consistently applied.",
                    "All of the above, plus post-adoption review to assess alignment with institutional policy.",
                ),
            },
            {
                "id": "1.5",
                "pillar_id": "p1",
                "sequence": 5,
                "short_label": "Regulatory alignment and compliance",
                "question": (
                    "When the institution engages with Nigeria's NDPR, Ghana's Data Protection Act, "
                    "Kenya's PDPA, or any applicable regional data protection regime, "
                    "how is regulatory alignment maintained?"
                ),
                "help_text": (
                    "Consider whether the institution has mapped its data processing activities "
                    "against the applicable legal framework, whether compliance obligations are "
                    "assigned to named roles, and whether the institution responds to regulatory "
                    "guidance proactively. Select the option that most accurately describes "
                    "current practice — not aspiration."
                ),
                "options": _opts(
                    "No awareness or engagement with applicable data protection regulations.",
                    "Regulations are known at senior level but no mapping or compliance activity has taken place.",
                    "Some compliance activities have occurred (e.g., a privacy policy exists) but are not systematically maintained.",
                    "A formal compliance programme is in place with assigned ownership and documented controls.",
                    "All of the above, plus active engagement with regulatory updates; the institution monitors sector-level guidance.",
                ),
            },
            {
                "id": "1.6",
                "pillar_id": "p1",
                "sequence": 6,
                "short_label": "Policy lifecycle management",
                "question": (
                    "When policies governing data use are written or updated, "
                    "how is that process managed and communicated to staff?"
                ),
                "help_text": (
                    "Consider whether there is a policy lifecycle covering drafting, approval, and review; "
                    "whether staff are informed when policies change; and whether policy documents are "
                    "accessible to those whose work they govern. Select the option that most accurately "
                    "describes current practice — not aspiration."
                ),
                "options": _opts(
                    "No formal policies exist; practice is entirely informal.",
                    "Some policies exist but were written once and have not been updated or communicated.",
                    "Policies exist and are updated occasionally, but communication to staff is inconsistent.",
                    "A policy lifecycle is in place; updates are communicated through defined channels.",
                    "All of the above, plus staff acknowledgment is recorded and policy effectiveness is assessed periodically.",
                ),
            },
        ],
    },

    # -----------------------------------------------------------------------
    # Pillar 2 — Data Foundations
    # -----------------------------------------------------------------------
    {
        "id": "p2",
        "name": "Data Foundations",
        "short_name": "Data",
        "description": (
            "Data quality, standardisation, integrity controls, ownership clarity, "
            "portability, and whether the institution's data substrate is structured for AI use."
        ),
        "colour": PILLAR_COLOURS["p2"],
        "items": [
            {
                "id": "2.1",
                "pillar_id": "p2",
                "sequence": 1,
                "short_label": "Data quality assurance at entry",
                "question": (
                    "When student academic or administrative records are created or updated, "
                    "how is data quality assured?"
                ),
                "help_text": (
                    "Consider whether there are validation rules at point of entry, whether "
                    "duplicate records are detected and resolved, and whether there is a process "
                    "for identifying and correcting errors over time. Select the option that most "
                    "accurately describes current practice — not aspiration."
                ),
                "options": _opts(
                    "No quality controls exist; data is entered without validation.",
                    "Staff apply personal judgment to catch errors; no institutional standard exists.",
                    "Some validation rules exist in certain systems, but coverage is partial and inconsistent.",
                    "Data quality standards are defined, validation is applied at entry, and errors are tracked and resolved.",
                    "All of the above, plus automated quality monitoring and quality metrics are reviewed by leadership.",
                ),
            },
            {
                "id": "2.2",
                "pillar_id": "p2",
                "sequence": 2,
                "short_label": "Cross-system data standardisation",
                "question": (
                    "When data is recorded across different departments or systems — "
                    "such as admissions, finance, and academic records — "
                    "how is consistency of formats and definitions maintained?"
                ),
                "help_text": (
                    "Consider whether the institution uses a common data dictionary or terminology "
                    "standard, whether a student ID or other key identifier links records across "
                    "systems, and whether data can be reliably combined. Select the option that "
                    "most accurately describes current practice — not aspiration."
                ),
                "options": _opts(
                    "Each department uses its own formats and definitions with no coordination.",
                    "Informal agreements exist between some departments, but no institutional standard is in place.",
                    "A partial standard exists for one data category but does not cover the full data landscape.",
                    "A data dictionary or standardisation framework covers major data categories and is actively maintained.",
                    "All of the above, plus cross-system linkage is tested regularly and standardisation extends to partner data.",
                ),
            },
            {
                "id": "2.3",
                "pillar_id": "p2",
                "sequence": 3,
                "short_label": "Data integrity investigation process",
                "question": (
                    "When data integrity is questioned — for example, if a record appears "
                    "inconsistent or anomalous — how is that concern investigated and resolved?"
                ),
                "help_text": (
                    "Consider whether there is a formal process for flagging and investigating "
                    "data integrity concerns, whether records of investigations are kept, and "
                    "whether systemic issues are escalated. Select the option that most accurately "
                    "describes current practice — not aspiration."
                ),
                "options": _opts(
                    "No process exists; anomalies are ignored or corrected informally without records.",
                    "Staff escalate concerns informally; resolution depends on individual initiative.",
                    "A process exists for some data categories but not others; investigations are inconsistently recorded.",
                    "A documented integrity investigation process exists, is applied consistently, and outcomes are recorded.",
                    "All of the above, plus integrity metrics are tracked over time and findings inform system or process improvements.",
                ),
            },
            {
                "id": "2.4",
                "pillar_id": "p2",
                "sequence": 4,
                "short_label": "Data ownership and stewardship",
                "question": (
                    "When institutional data assets are created, maintained, or transferred, "
                    "how is data ownership and stewardship responsibility assigned?"
                ),
                "help_text": (
                    "Consider whether named roles — not just departments — are responsible for "
                    "specific data sets, whether those roles understand their responsibilities, "
                    "and whether ownership transfers when staff change. Select the option that "
                    "most accurately describes current practice — not aspiration."
                ),
                "options": _opts(
                    "No ownership is assigned; responsibility is assumed informally or not at all.",
                    "Ownership is informally understood but not documented or consistently upheld.",
                    "Ownership is documented for some major data sets but gaps exist; handover is inconsistent.",
                    "Data ownership is formally assigned for all major data assets, documented, and reviewed when staff change.",
                    "All of the above, plus stewards are trained, supported, and held accountable through formal processes.",
                ),
            },
            {
                "id": "2.5",
                "pillar_id": "p2",
                "sequence": 5,
                "short_label": "Data portability and accessibility",
                "question": (
                    "When the institution needs to extract, move, or share a data set — "
                    "for reporting, analysis, or a system migration — "
                    "how portable and accessible is that data?"
                ),
                "help_text": (
                    "Consider whether data can be exported in interoperable formats such as "
                    "CSV or JSON, whether extraction is possible without specialist vendor support, "
                    "and whether there are known barriers to data portability. Select the option "
                    "that most accurately describes current practice — not aspiration."
                ),
                "options": _opts(
                    "Data is locked in systems; extraction is not possible without significant vendor intervention.",
                    "Some data can be extracted informally, but the process is inconsistent and poorly documented.",
                    "Export capability exists for major systems, but formats are not standardised and some data is inaccessible.",
                    "Data can be extracted in documented, interoperable formats from all major systems with internal capability.",
                    "All of the above, plus portability is tested regularly and vendor contracts include data portability provisions.",
                ),
            },
            {
                "id": "2.6",
                "pillar_id": "p2",
                "sequence": 6,
                "short_label": "AI-substrate readiness of data",
                "question": (
                    "When considering whether institutional data is ready to serve as a training "
                    "substrate or inference input for an AI system, "
                    "how would you characterise the current state?"
                ),
                "help_text": (
                    "Consider whether key data sets are structured, labelled, and sufficiently "
                    "complete for analytical or machine-learning use; whether data volumes meet "
                    "minimum thresholds; and whether known quality gaps would undermine model "
                    "reliability. If this question is outside your direct knowledge, select the "
                    "option that best reflects what you know of the institution's data systems. "
                    "Select the option that most accurately describes current practice — not aspiration."
                ),
                "options": _opts(
                    "Data is largely unstructured, incomplete, or unavailable in digital form.",
                    "Some structured data exists, but significant gaps in completeness and labelling make AI use impractical.",
                    "Core data sets are structured and reasonably complete, but inconsistencies remain that would require remediation.",
                    "Most key data sets are structured, labelled, sufficiently complete, and quality has been assessed against AI-use requirements.",
                    "All of the above, plus AI-readiness of data is regularly reviewed, enriched, and documented for specific use cases.",
                ),
            },
        ],
    },

    # -----------------------------------------------------------------------
    # Pillar 3 — Organisational Capacity
    # -----------------------------------------------------------------------
    {
        "id": "p3",
        "name": "Organisational Capacity",
        "short_name": "Capacity",
        "description": (
            "Leadership alignment, technical capability, change-management readiness, "
            "training infrastructure, and the human systems that determine whether AI "
            "is absorbed or rejected by the institution."
        ),
        "colour": PILLAR_COLOURS["p3"],
        "items": [
            {
                "id": "3.1",
                "pillar_id": "p3",
                "sequence": 1,
                "short_label": "Senior leadership alignment on AI",
                "question": (
                    "When AI strategy or technology investment decisions are discussed at senior level, "
                    "how aligned is leadership on the institution's direction and priorities?"
                ),
                "help_text": (
                    "Consider whether a formal AI strategy or digital transformation strategy exists, "
                    "whether senior leadership — academic and administrative — share a common "
                    "understanding of its content, and whether it is referenced in institutional "
                    "planning. Select the option that most accurately describes current practice — "
                    "not aspiration."
                ),
                "options": _opts(
                    "No AI or technology strategy exists; leadership has no shared position.",
                    "Individual leaders have personal views on AI but there is no institutional consensus or documented position.",
                    "A strategy document exists or is in progress, but leadership alignment is partial or contested.",
                    "A formal strategy exists, is endorsed by senior leadership, and is reflected in operational planning.",
                    "All of the above, plus strategy is reviewed regularly and progress is reported to governing bodies.",
                ),
            },
            {
                "id": "3.2",
                "pillar_id": "p3",
                "sequence": 2,
                "short_label": "Internal technical capability",
                "question": (
                    "When AI tools or data systems are to be implemented, "
                    "what is the technical capability available within the institution "
                    "to configure, manage, and support them?"
                ),
                "help_text": (
                    "Consider the skills profile of ICT and data staff — not just leadership — "
                    "whether technical roles relevant to AI and data management exist, and "
                    "whether staff can operate independently or are dependent on external vendors. "
                    "Select the option that most accurately describes current practice — not aspiration."
                ),
                "options": _opts(
                    "No technical staff with relevant AI or data skills exist; the institution is entirely vendor-dependent.",
                    "Basic ICT staff exist but have no training or experience relevant to AI or data management.",
                    "Some technical capability exists in pockets — one or two individuals — but is not institutional; significant vendor dependency remains.",
                    "A team with relevant technical capability exists, roles are defined, and the institution can manage AI tools with limited vendor support.",
                    "All of the above, plus internal capability is mapped, succession-planned, and developed through ongoing professional learning.",
                ),
            },
            {
                "id": "3.3",
                "pillar_id": "p3",
                "sequence": 3,
                "short_label": "Change management practice",
                "question": (
                    "When significant technology or operational changes are introduced, "
                    "how does the institution manage the transition and support staff through it?"
                ),
                "help_text": (
                    "Consider whether there is a change management methodology or practice, "
                    "how communication about changes is structured, whether staff concerns are "
                    "surfaced and addressed, and whether adoption is monitored. Select the option "
                    "that most accurately describes current practice — not aspiration."
                ),
                "options": _opts(
                    "Change is implemented with no structured management; staff adapt without institutional support.",
                    "Change communications happen informally; no structured methodology is applied.",
                    "Some elements of change management are applied — such as briefings or training — but not consistently.",
                    "A change management approach is applied to significant technology changes, covering communication, training, and adoption monitoring.",
                    "All of the above, plus change readiness is assessed before implementation; feedback loops inform how changes are rolled out.",
                ),
            },
            {
                "id": "3.4",
                "pillar_id": "p3",
                "sequence": 4,
                "short_label": "Training infrastructure for technology",
                "question": (
                    "When staff need training on data systems, digital tools, or AI-related skills, "
                    "how is that training designed, delivered, and sustained?"
                ),
                "help_text": (
                    "Consider whether a training plan or learning and development framework exists "
                    "for technology topics, whether training is delivered on an ad hoc or structured "
                    "basis, and whether its effectiveness is evaluated. Select the option that most "
                    "accurately describes current practice — not aspiration."
                ),
                "options": _opts(
                    "No formal training exists; staff learn informally through individual initiative.",
                    "Training is provided occasionally in response to specific needs, without a broader plan.",
                    "A training programme exists but is not updated to reflect current technology or tied to strategic priorities.",
                    "A structured training programme for technology and data skills is in place, linked to institutional priorities, and delivered consistently.",
                    "All of the above, plus training outcomes are evaluated and the programme evolves based on performance data and emerging needs.",
                ),
            },
            {
                "id": "3.5",
                "pillar_id": "p3",
                "sequence": 5,
                "short_label": "Human-AI workflow definition",
                "question": (
                    "When AI or data systems are introduced, "
                    "how are the human roles, responsibilities, and workflows "
                    "that interact with those systems defined and managed?"
                ),
                "help_text": (
                    "Consider whether process maps or workflow documentation exist for AI-adjacent roles, "
                    "whether staff understand how AI outputs are to be used in their work, and whether "
                    "role boundaries between human judgment and automated output are clearly defined. "
                    "Select the option that most accurately describes current practice — not aspiration."
                ),
                "options": _opts(
                    "No definition of roles or workflows in relation to AI systems; integration is entirely informal.",
                    "Some informal understanding exists among directly involved staff, but no documentation or institutional definition.",
                    "Roles and workflows are documented for some AI use cases but not consistently across the institution.",
                    "Roles, workflows, and human-AI decision boundaries are defined and documented for all active AI implementations.",
                    "All of the above, plus role definitions are reviewed as AI systems evolve and staff have clear channels to raise concerns.",
                ),
            },
            {
                "id": "3.6",
                "pillar_id": "p3",
                "sequence": 6,
                "short_label": "Institutional AI self-assessment",
                "question": (
                    "When the institution assesses its own readiness for AI adoption, "
                    "how honest and systematic is that self-assessment process?"
                ),
                "help_text": (
                    "Consider whether the institution conducts formal internal assessments such as "
                    "maturity reviews or gap analyses, whether external perspectives are sought, "
                    "whether findings are acted upon, and whether leadership engages critically "
                    "with weaknesses. Select the option that most accurately describes current "
                    "practice — not aspiration."
                ),
                "options": _opts(
                    "No formal self-assessment takes place; the institution has no structured view of its own readiness.",
                    "Informal or anecdotal views on readiness circulate at leadership level but are not tested against evidence.",
                    "Some assessments have been conducted — such as a one-time review — but are not systematic or consistently acted upon.",
                    "Structured self-assessment occurs periodically, findings are documented, and improvement actions are tracked.",
                    "All of the above, plus external benchmarking is used and self-assessment findings directly inform strategy and investment decisions.",
                ),
            },
        ],
    },

    # -----------------------------------------------------------------------
    # Pillar 4 — Ethical Infrastructure
    # -----------------------------------------------------------------------
    {
        "id": "p4",
        "name": "Ethical Infrastructure",
        "short_name": "Ethics",
        "description": (
            "Bias mitigation posture, explainability standards for non-technical users, "
            "recourse mechanisms, equity considerations, and stakeholder representation "
            "in AI governance processes."
        ),
        "colour": PILLAR_COLOURS["p4"],
        "items": [
            {
                "id": "4.1",
                "pillar_id": "p4",
                "sequence": 1,
                "short_label": "Bias assessment and mitigation",
                "question": (
                    "When AI tools are selected or data models are built, "
                    "how is the risk of bias — particularly in relation to gender, ethnicity, "
                    "disability, or socioeconomic status — assessed and mitigated?"
                ),
                "help_text": (
                    "Consider whether bias assessment is part of any procurement or development process, "
                    "whether training data representativeness is evaluated, and whether there is a named "
                    "role or process responsible for bias review. Select the option that most accurately "
                    "describes current practice — not aspiration."
                ),
                "options": _opts(
                    "Bias risk is not considered as part of AI tool selection or data model design.",
                    "Awareness of bias risk exists informally, but no structured assessment is conducted.",
                    "Bias assessment occurs occasionally or for specific projects but is not applied systematically.",
                    "A bias assessment process is formally applied to AI tool procurement and development, with documented findings.",
                    "All of the above, plus bias monitoring continues post-deployment; findings feed back into model updates or procurement decisions.",
                ),
            },
            {
                "id": "4.2",
                "pillar_id": "p4",
                "sequence": 2,
                "short_label": "AI output explainability standards",
                "question": (
                    "When AI systems produce outputs used in decisions affecting students or staff — "
                    "such as flagging, scoring, or recommendations — "
                    "how are those outputs explained to non-technical users?"
                ),
                "help_text": (
                    "Consider whether outputs are accompanied by plain-language explanations of how "
                    "they were generated, whether staff using AI outputs can articulate the basis of "
                    "those outputs to affected individuals, and whether explanation standards are "
                    "defined. Select the option that most accurately describes current practice — "
                    "not aspiration."
                ),
                "options": _opts(
                    "No explanation is provided; AI outputs are used as black boxes.",
                    "Technical staff can explain outputs informally, but no standard exists for communicating to non-technical users.",
                    "Some explanatory documentation exists, but it is not consistently applied or accessible to operational staff.",
                    "Plain-language explanation standards are defined, applied to all AI-assisted decisions, and operational staff are trained to communicate them.",
                    "All of the above, plus explanation quality is reviewed; affected individuals can request additional explanation through a formal channel.",
                ),
            },
            {
                "id": "4.3",
                "pillar_id": "p4",
                "sequence": 3,
                "short_label": "Recourse mechanisms for AI decisions",
                "question": (
                    "When a student, parent, or staff member believes they have been adversely "
                    "affected by an AI-assisted decision, how is their recourse path defined?"
                ),
                "help_text": (
                    "Consider whether a formal complaints or appeals process applies to AI-assisted "
                    "decisions, whether that process is communicated to affected parties, whether "
                    "decisions can be reviewed by a human, and whether outcomes are recorded. "
                    "Select the option that most accurately describes current practice — not aspiration."
                ),
                "options": _opts(
                    "No recourse mechanism exists for AI-assisted decisions.",
                    "General grievance processes exist but do not explicitly cover AI-assisted decisions; affected parties are unclear on their options.",
                    "A recourse path is informally understood internally but not communicated to affected parties or consistently applied.",
                    "A formal, communicated recourse path applies to all AI-assisted decisions, including human review and recorded outcomes.",
                    "All of the above, plus recourse uptake and outcomes are monitored; patterns inform AI system adjustments.",
                ),
            },
            {
                "id": "4.4",
                "pillar_id": "p4",
                "sequence": 4,
                "short_label": "Equity impact assessment",
                "question": (
                    "When deploying or procuring AI in contexts involving students — "
                    "particularly under-resourced, rural, or marginalised groups — "
                    "how are equity implications assessed?"
                ),
                "help_text": (
                    "Consider whether equity impact assessment is part of any AI deployment process, "
                    "whether the institution has a definition of equitable AI outcomes relevant to "
                    "its student population, and whether deployment decisions are adjusted in response "
                    "to equity concerns. Select the option that most accurately describes current "
                    "practice — not aspiration."
                ),
                "options": _opts(
                    "Equity implications are not assessed as part of AI deployment decisions.",
                    "Equity concerns are occasionally raised informally but are not systematically evaluated.",
                    "Equity considerations are documented in some AI projects but not as a universal requirement.",
                    "Equity impact assessment is a formal requirement for AI deployments, with documented outcomes.",
                    "All of the above, plus equity outcomes are monitored post-deployment and inform both AI configurations and institutional policy.",
                ),
            },
            {
                "id": "4.5",
                "pillar_id": "p4",
                "sequence": 5,
                "short_label": "Stakeholder representation in ethics",
                "question": (
                    "When AI governance or ethics policies are developed, "
                    "how are the perspectives of students, parents, frontline staff, "
                    "and community representatives included?"
                ),
                "help_text": (
                    "Consider whether consultative processes exist for AI policy development, "
                    "whether affected communities have channels to provide input, and whether "
                    "their input demonstrably shapes policy rather than being nominal. "
                    "Select the option that most accurately describes current practice — not aspiration."
                ),
                "options": _opts(
                    "No stakeholder consultation occurs in AI governance or ethics policy development.",
                    "Some engagement takes place informally or selectively, but it is not structured or documented.",
                    "Consultation processes exist but participation is inconsistent or limited to selected stakeholders.",
                    "A structured consultation process is applied to AI governance policy development, with documented input from diverse stakeholders.",
                    "All of the above, plus stakeholder input demonstrably changes policy outcomes; engagement is reported back to participants.",
                ),
            },
            {
                "id": "4.6",
                "pillar_id": "p4",
                "sequence": 6,
                "short_label": "Holistic ethics review mechanism",
                "question": (
                    "When the institution reflects on the cumulative ethical posture of its AI activity — "
                    "across bias, explainability, recourse, equity, and representation — "
                    "how is that posture monitored and reviewed?"
                ),
                "help_text": (
                    "Consider whether a holistic ethics review mechanism exists — such as an ethics "
                    "committee or structured self-assessment — whether it has authority to halt or "
                    "modify AI implementations, and whether it meets regularly. Select the option "
                    "that most accurately describes current practice — not aspiration."
                ),
                "options": _opts(
                    "No ethics review mechanism of any kind exists for AI activity.",
                    "Ethics concerns are raised ad hoc by individuals; no institutional review structure exists.",
                    "An ethics review process has been discussed or piloted but is not formally established or consistently active.",
                    "A formal ethics review mechanism is established, meets regularly, and has documented authority over AI implementations.",
                    "All of the above, plus the mechanism participates in sector-level ethics networks; its findings are shared externally.",
                ),
            },
        ],
    },
]


# ---------------------------------------------------------------------------
# Observation template registry
# ---------------------------------------------------------------------------
# Each entry defines one rule in the observation engine.
# Rules are evaluated in order by scoring.generate_observations().
# Templates use {PLACEHOLDER} tokens populated from the scores dict.
# ---------------------------------------------------------------------------

OBSERVATION_RULES = [
    {
        "rule_id": "R1",
        "label": "Lowest pillar + lowest item spotlight",
        "always": True,  # fires unconditionally as the first observation
        "condition_description": "Always fires.",
        "template": (
            "Within your profile, {LOWEST_PILLAR_NAME} represents the area of most acute "
            "development need, with a pillar score of {LOWEST_PILLAR_SCORE}. The specific "
            "practice that scores lowest within this pillar concerns {LOWEST_ITEM_SHORT_LABEL} "
            "(Item {LOWEST_ITEM_ID}, rated {LOWEST_ITEM_SCORE}/5). This item often anchors "
            "the broader pillar score and is a productive starting point for focused remediation."
        ),
        "placeholders": [
            "LOWEST_PILLAR_NAME",
            "LOWEST_PILLAR_SCORE",
            "LOWEST_ITEM_SHORT_LABEL",
            "LOWEST_ITEM_ID",
            "LOWEST_ITEM_SCORE",
        ],
    },
    {
        "rule_id": "R2",
        "label": "Policy strong, data weak divergence",
        "always": False,
        "condition_description": "p1 >= 60 AND p2 < 50",
        "template": (
            "Your profile shows a notable divergence between Governance & Policy "
            "(scored {P1_SCORE}) and Data Foundations (scored {P2_SCORE}) — a gap of "
            "{GAP} points. This pattern is common in institutions that have prioritised "
            "compliance documentation ahead of data substrate work. The practical effect "
            "is that strong policies govern data practices that are not yet structured "
            "well enough to support them. Closing this gap typically requires targeted "
            "data architecture and quality investment rather than further policy development."
        ),
        "placeholders": ["P1_SCORE", "P2_SCORE", "GAP"],
    },
    {
        "rule_id": "R3",
        "label": "Ethics below governance — written policy without operationalisation",
        "always": False,
        "condition_description": "p1 - p4 >= 20",
        "template": (
            "Ethical Infrastructure (scored {P4_SCORE}) scores materially below "
            "Governance & Policy (scored {P1_SCORE}). This configuration — strong written "
            "governance, weaker operational ethics — is worth noting because ethics "
            "infrastructure requires active institutional machinery: review mechanisms, "
            "recourse paths, and consultation processes, rather than policy language alone. "
            "The gap suggests that policy commitments have not yet been fully operationalised "
            "into practice-level structures."
        ),
        "placeholders": ["P4_SCORE", "P1_SCORE"],
    },
    {
        "rule_id": "R4",
        "label": "Organisational capacity drag on an otherwise strong profile",
        "always": False,
        "condition_description": "p3 is lowest pillar AND composite >= 50 AND composite - p3 >= 15",
        "template": (
            "Your composite profile ({TIER}) is held at {COMPOSITE} in part because "
            "Organisational Capacity (scored {P3_SCORE}) falls {DRAG} points below your "
            "composite average. This configuration — stronger policy, data, and ethics posture "
            "relative to human capacity — is a common constraint in under-resourced settings. "
            "It suggests that further gains in the other pillars may be constrained until "
            "leadership alignment, technical skills, and change management capability are "
            "strengthened."
        ),
        "placeholders": ["TIER", "COMPOSITE", "P3_SCORE", "DRAG"],
    },
    {
        "rule_id": "R5",
        "label": "Balanced profile",
        "always": False,
        "condition_description": "spread < 15 AND R2/R3/R4 all missed (or forced as fallback)",
        "template": {
            "A": (  # composite >= 60
                "Your profile is notably balanced across all four pillars, with a spread of "
                "{SPREAD} points between your highest and lowest pillar score. At a composite "
                "of {COMPOSITE} ({TIER}), this indicates consistent institutional development "
                "rather than uneven progress. Balanced profiles at this tier typically benefit "
                "most from deepening practice within each pillar concurrently, rather than "
                "targeted remediation of any single area."
            ),
            "B": (  # composite < 60
                "Your profile is balanced across all four pillars, with a spread of {SPREAD} "
                "points between your highest and lowest pillar score. At a composite of "
                "{COMPOSITE} ({TIER}), this balance reflects a consistent — if early-stage — "
                "development posture across the institution. Because no single pillar is "
                "dramatically weaker, capacity-building investment can be broadly distributed "
                "rather than concentrated."
            ),
        },
        "placeholders": ["SPREAD", "COMPOSITE", "TIER"],
    },
]


# ---------------------------------------------------------------------------
# Convenience helpers used by other modules
# ---------------------------------------------------------------------------

def get_pillar(pillar_id: str) -> dict:
    for p in PILLARS:
        if p["id"] == pillar_id:
            return p
    raise KeyError(f"Unknown pillar id: {pillar_id}")


def get_item(item_id: str) -> dict:
    for p in PILLARS:
        for item in p["items"]:
            if item["id"] == item_id:
                return item
    raise KeyError(f"Unknown item id: {item_id}")


def all_item_ids() -> list[str]:
    return [item["id"] for p in PILLARS for item in p["items"]]


def items_for_pillar(pillar_id: str) -> list[dict]:
    return get_pillar(pillar_id)["items"]


def get_tier(composite: float) -> dict:
    for tier in TIERS:
        if tier["min"] <= composite <= tier["max"]:
            return tier
    return TIERS[-1]
