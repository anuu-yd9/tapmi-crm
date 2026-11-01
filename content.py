"""
content.py  -  ALL the words, prices and rules for the website live here.

Every fact below comes from your Milestone 1 (positioning) and Milestone 2
(offering design + pricing) reports. If your group changed a decision, change
it HERE and the whole website + CRM updates automatically.
"""

DISCLAIMER = "Student project, not an official TAPMI offering."

# ---------------------------------------------------------------------------
# The 5 buyer situations (Milestone 3 brief, section 2)
# ---------------------------------------------------------------------------
SITUATIONS = {
    "EMBA_B2B": {
        "programme": "emba", "kind": "B2B",
        "label": "Executive MBA for organisations",
        "short": "EMBA · Organisation",
        "audience": "HR heads, L&D leaders and business heads sponsoring high-potential employees",
        "positioning": ("Build stronger future leaders from your existing high-potential talent, "
                        "without removing them from their careers."),
    },
    "EMBA_B2C": {
        "programme": "emba", "kind": "B2C",
        "label": "Executive MBA for individuals",
        "short": "EMBA · Individual",
        "audience": "Mid-career professionals who have hit the ceiling of functional expertise",
        "positioning": ("An applied, career-compatible management experience that takes you "
                        "beyond your function and into broader leadership."),
    },
    "MDP_B2B": {
        "programme": "mdp", "kind": "B2B",
        "label": "Management Development Programme for organisations",
        "short": "MDP · Organisation",
        "audience": "L&D heads, HR business partners and business unit heads closing a group capability gap",
        "positioning": ("Customised, experiential learning that turns your organisation's "
                        "capability gap into practical workplace application."),
    },
    "CERT_B2B": {
        "programme": "cert", "kind": "B2B",
        "label": "Management Certifications for organisations",
        "short": "Certification · Organisation",
        "audience": "Managers and L&D teams upskilling employees for a specific role-related gap",
        "positioning": ("Focused, credible upskilling your employees can apply at work, "
                        "with an employer-verifiable credential."),
    },
    "CERT_B2C": {
        "programme": "cert", "kind": "B2C",
        "label": "Management Certifications for individuals",
        "short": "Certification · Individual",
        "audience": "Early-to-mid career professionals (about 3-8 years) who want a focused skill upgrade",
        "positioning": ("Business-school learning without the time and cost of a full MBA, "
                        "and credits that stack into the Executive MBA."),
    },
}

# ---------------------------------------------------------------------------
# The 3 programmes
# ---------------------------------------------------------------------------
PROGRAMMES = {
    "emba": {
        "name": "Executive MBA",
        "tagline": "Lead beyond your function, while you keep working.",
        "summary": ("An 18-month weekend-and-blended management programme with an applied, "
                    "workplace-linked project, built for working professionals."),
        "facts": [
            ("Duration", "18 months, 6 terms of 3 months each"),
            ("Format", "Alternate weekends on campus + live virtual sessions + asynchronous modules"),
            ("Immersion", "2 residential immersion weeks (orientation and capstone)"),
            ("Faculty", "TAPMI full-time faculty plus visiting industry faculty"),
        ],
        "b2b_points": [
            "Workplace-linked business impact project each term, with sponsor involvement",
            "Elective clusters aligned to Technology/GCC, BFSI and Manufacturing sponsors",
            "Sponsor-side progress reporting for HR and the reporting manager",
        ],
        "b2c_points": [
            "Career Transition Lab: resume and LinkedIn positioning, mock general-management interviews",
            "No-cost EMI/financing partnership and a deferred-fee option for a single term",
            "Peer network of experienced professionals",
        ],
        "price_headline_b2b": "₹9,50,000 per participant + GST",
        "price_headline_b2c": "₹9,50,000 + GST",
        "b2b_table": [  # Milestone 2, Table 5
            ("1-2 seats", "0%", "₹9,50,000"),
            ("3-5 seats", "2%", "₹9,31,000"),
            ("6-9 seats", "4%", "₹9,12,000"),
            ("10-14 seats", "5%", "₹9,02,500"),
            ("15+ seats", "7%", "₹8,83,500"),
        ],
        "b2b_table_cols": ("Seats from one organisation", "Discount", "Fee per participant (before GST)"),
        "b2c_note": "Same list price as organisations. EMI and a single-term deferred-fee option are available.",
        "unit_price": 950000,
    },
    "mdp": {
        "name": "Management Development Programme",
        "tagline": "Close a capability gap across a whole cohort.",
        "summary": ("A customised 3-month blended programme for groups of up to 25 managers, "
                    "designed around your organisation's own challenges."),
        "facts": [
            ("Duration", "3 months, blended"),
            ("Format", "2 campus immersions (3 days each, Bengaluru) + live online weekend classes + bi-weekly group coaching"),
            ("Cohort", "Up to 25 participants per group"),
            ("Faculty", "TAPMI faculty with C-suite industry experts and executive coaches"),
        ],
        "b2b_points": [
            "Starts with a diagnostic call and competency-gap mapping",
            "Sponsor-linked projects and a final results review",
            "A dedicated Academic Programme Director and Enterprise Client Director for your account",
        ],
        "b2c_points": [],
        "price_headline_b2b": "₹25,00,000 per group of up to 25 + GST",
        "price_headline_b2c": "",
        "b2b_table": [],
        "b2b_table_cols": (),
        "b2b_note": ("Starting price for evaluation. Customisation beyond the standard design is "
                     "priced separately. Repeat groups and long-term agreements can be discussed."),
        "unit_price": 2500000,
    },
    "cert": {
        "name": "Management Certifications",
        "tagline": "One focused skill. A credential that holds up.",
        "summary": ("A 3-month blended certification with a company-linked mini-project and "
                    "verified digital credentials."),
        "facts": [
            ("Duration", "3 months"),
            ("Format", "Weekend live online lectures + self-paced content + 1 optional Saturday campus masterclass"),
            ("Content", "4 targeted modules plus a 3-week mini-project"),
            ("Credential", "Online proctored evaluation and an employer-verifiable digital credential"),
        ],
        "b2b_points": [
            "Mini-project solves a real problem in the employee's own department",
            "Volume pricing that rewards larger teams",
            "Supports repeat upskilling for the same employees",
        ],
        "b2c_points": [
            "Career Velocity Lab: resume, LinkedIn credentialing and career positioning guidance",
            "Credits stack into TAPMI's Executive MBA within 24 months",
            "Two-instalment payment plan available",
        ],
        "price_headline_b2b": "₹18,000 per learner + GST",
        "price_headline_b2c": "₹18,000 + GST",
        "b2b_table": [  # Milestone 2, B.3.2
            ("1-9 learners", "0%", "₹18,000"),
            ("10-24 learners", "8%", "₹16,560"),
            ("25-49 learners", "12.5%", "₹15,750"),
            ("50-99 learners", "17%", "₹14,940"),
            ("100+ learners", "22%", "from ₹14,040 (subject to approval)"),
        ],
        "b2b_table_cols": ("Learners from one organisation", "Discount", "Fee per learner (before GST)"),
        "b2c_note": ("Limited-time trial offer of ₹15,750. Optional payment plan of two payments of "
                     "₹9,500 (total ₹19,000). The full cost is shown up front."),
        "unit_price": 18000,
    },
}

# ---------------------------------------------------------------------------
# Estimated deal value (used by the dashboard to calculate pipeline value)
# ---------------------------------------------------------------------------
def b2b_unit_price(programme, seats):
    """Fee per seat after the volume discount tables from Milestone 2."""
    if programme == "emba":
        for lo, price in [(15, 883500), (10, 902500), (6, 912000), (3, 931000), (1, 950000)]:
            if seats >= lo:
                return price
    if programme == "cert":
        for lo, price in [(100, 14040), (50, 14940), (25, 15750), (10, 16560), (1, 18000)]:
            if seats >= lo:
                return price
    return PROGRAMMES[programme]["unit_price"]


def estimate_value(situation, seats):
    """Rough rupee value of a lead, so the dashboard can show pipeline value."""
    s = SITUATIONS[situation]
    p = s["programme"]
    seats = max(1, int(seats or 1))
    if p == "mdp":
        groups = max(1, -(-seats // 25))  # ceiling division: 1 group per 25 people
        return groups * 2500000
    if s["kind"] == "B2B":
        return seats * b2b_unit_price(p, seats)
    return PROGRAMMES[p]["unit_price"]


# ---------------------------------------------------------------------------
# Lead sources  (source tracking = ?src=xxx on the link, see "Campaign links")
# ---------------------------------------------------------------------------
SOURCES = {
    "website": "Website (organic / direct)",
    "linkedin": "LinkedIn",
    "email": "Email campaign",
    "webinar": "Webinar / event",
    "referral": "Referral",
    "poster": "Poster QR code",
    "salesvisit": "Sales visit (personal selling)",
}

# Marketing spend per source in rupees. DUMMY ASSUMPTIONS: replace with your
# Milestone 3 Task A budget so the "cost per lead / enrolment" numbers are yours.
DEFAULT_SPEND = {
    "website": 0, "linkedin": 40000, "email": 5000, "webinar": 25000,
    "referral": 0, "poster": 10000, "salesvisit": 60000,
}

# ---------------------------------------------------------------------------
# Pipelines (lifecycle stages). B2B and B2C buy differently -> different stages.
# (name, win-probability used for weighted pipeline value)
# ---------------------------------------------------------------------------
PIPELINE_B2B = [
    ("New enquiry", 0.05),
    ("Discovery call", 0.15),
    ("Qualified (SQL)", 0.30),
    ("Proposal / MoU", 0.55),
    ("Won - enrolled", 1.00),
    ("Retention & expansion", 1.00),
]
PIPELINE_B2C = [
    ("New enquiry", 0.05),
    ("Counselling call", 0.15),
    ("Qualified (SQL)", 0.30),
    ("Application", 0.55),
    ("Won - enrolled", 1.00),
    ("Alumni & referral", 1.00),
]
SIDE_STAGES = ["Nurture", "Lost"]   # any lead can be parked here


def pipeline_for(kind):
    return PIPELINE_B2B if kind == "B2B" else PIPELINE_B2C


def stage_names(kind):
    return [s for s, _ in pipeline_for(kind)] + SIDE_STAGES


def stage_probability(kind, stage):
    for s, p in pipeline_for(kind):
        if s == stage:
            return p
    return 0.0


# ---------------------------------------------------------------------------
# Form choices
# ---------------------------------------------------------------------------
ROLES_B2B = [   # these are the DMU roles from Milestone 1
    ("decider", "Decider: I approve the investment"),
    ("budget_owner", "Budget owner: I control the funds"),
    ("influencer", "Influencer: I advise the decision"),
    ("initiator", "Initiator: I raised the need"),
    ("user", "User: I or my team would attend"),
]
BUDGET_B2B = [
    ("approved", "Budget approved"),
    ("seeking", "Budget being sought"),
    ("none", "No budget yet"),
]
TIMELINE = [
    ("3m", "Within 3 months"),
    ("6m", "In 3 to 6 months"),
    ("later", "More than 6 months away"),
    ("exploring", "Just exploring"),
]
FUNDING_B2C = [
    ("self", "Self-funded"),
    ("self_emi", "Self-funded, would need EMI / payment plan"),
    ("employer_maybe", "Hoping my employer will sponsor"),
]
CONCERNS = [
    ("cost", "Cost and return on investment"),
    ("time", "Time alongside a full-time job"),
    ("credibility", "Credibility of the credential"),
    ("fit", "Not sure which programme fits me"),
]


# ---------------------------------------------------------------------------
# Task B assets hosted/linked on the website. Paste your Canva / YouTube /
# Drive links between the quotes. Empty = the page shows "coming soon".
# ---------------------------------------------------------------------------
ASSET_TYPES = [("av", "Video (60-120 sec)"), ("brochure", "Brochure"), ("poster", "Poster"),
               ("story", "Customer story / case study")]
ASSET_LINKS = {
    "EMBA_B2B": {"av": "", "brochure": "", "poster": "", "story": ""},
    "EMBA_B2C": {"av": "", "brochure": "", "poster": "", "story": ""},
    "MDP_B2B":  {"av": "", "brochure": "", "poster": "", "story": ""},
    "CERT_B2B": {"av": "", "brochure": "", "poster": "", "story": ""},
    "CERT_B2C": {"av": "", "brochure": "", "poster": "", "story": ""},
}
