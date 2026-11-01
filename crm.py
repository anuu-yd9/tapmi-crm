"""
crm.py  -  the "mini CRM" brain.

What this file does (these are the CRM capabilities your teacher asked for):
  1. LEAD CAPTURE ........ save_lead()           (called by the website forms)
  2. LEAD QUALIFICATION .. score_lead()          (BANT-style rules -> Hot / Warm / Cold)
  3. PIPELINE ............ change_stage()        (separate B2B and B2C stages)
  4. AUTOMATED FOLLOW-UPS  schedule_sequence(), run_automations()
  5. RETENTION / DEVELOPMENT  on_stage_change() schedules post-sale emails
  6. DASHBOARD NUMBERS ... dashboard_data()

Plain sqlite3 is used on purpose (it ships with Python, nothing to install).
"""
import json
import os
import sqlite3
from datetime import datetime, timedelta

import content as C

DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(os.path.dirname(__file__), "crm.db"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT, name TEXT, email TEXT, phone TEXT, org TEXT, job_title TEXT,
    situation TEXT, programme TEXT, kind TEXT, source TEXT,
    role TEXT, budget TEXT, timeline TEXT, seats INTEGER,
    years_exp INTEGER, funding TEXT, concern TEXT, message TEXT, wants_call INTEGER,
    score INTEGER, band TEXT, score_detail TEXT, est_value INTEGER,
    stage TEXT, ai_json TEXT, is_demo INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT, lead_id INTEGER, created_at TEXT, due_at TEXT,
    title TEXT, kind TEXT, template TEXT, status TEXT DEFAULT 'open', auto INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT, lead_id INTEGER, created_at TEXT,
    subject TEXT, body TEXT, status TEXT, made_by TEXT
);
CREATE TABLE IF NOT EXISTS activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT, lead_id INTEGER, created_at TEXT, text TEXT
);
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT);
"""


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db()
    conn.executescript(SCHEMA)
    conn.commit()
    conn.close()


def get_setting(key, default=None):
    conn = db()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key, value):
    conn = db()
    conn.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)", (key, str(value)))
    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# The CRM clock. "Demo days" lets you fast-forward time so you can SHOW the
# automated follow-ups firing in your 5-minute screen recording.
# ---------------------------------------------------------------------------
FMT = "%Y-%m-%d %H:%M:%S"


def now():
    offset = int(get_setting("clock_offset_days", "0"))
    return datetime.utcnow() + timedelta(days=offset)


def ts(dt):
    return dt.strftime(FMT)


def parse(s):
    return datetime.strptime(s, FMT)


def log(conn, lead_id, text, when=None):
    conn.execute("INSERT INTO activity(lead_id,created_at,text) VALUES(?,?,?)",
                 (lead_id, ts(when or now()), text))


# ---------------------------------------------------------------------------
# 2. LEAD QUALIFICATION  -  explainable scoring (max 100)
#    B2B uses BANT  : Budget, Authority, Need/timeline, (plus size + engagement)
#    B2C uses a "fit + funding + intent" model
# ---------------------------------------------------------------------------
SOURCE_POINTS = {"referral": 10, "salesvisit": 10, "webinar": 6, "linkedin": 6,
                 "email": 4, "poster": 4, "website": 3}


def score_lead(d):
    """d is a dict of lead fields. Returns (score, band, detail list)."""
    detail = []

    def add(label, points, maximum, why):
        detail.append({"factor": label, "points": points, "max": maximum, "why": why})

    src = d.get("source", "website")
    if d["kind"] == "B2B":
        role = d.get("role")
        add("Authority", {"decider": 25, "budget_owner": 25, "influencer": 15, "initiator": 10,
                          "user": 5}.get(role, 0), 25,
            "Can this person approve the spend? (Decision-Making Unit role from Milestone 1)")
        add("Budget", {"approved": 25, "seeking": 12, "none": 0}.get(d.get("budget"), 0), 25,
            "Is money already allocated?")
        add("Timeline", {"3m": 20, "6m": 12, "later": 4, "exploring": 0}.get(d.get("timeline"), 0), 20,
            "How soon do they need it?")
        seats = int(d.get("seats") or 1)
        add("Size of need", 15 if seats >= 10 else 9 if seats >= 3 else 4, 15,
            f"{seats} participant(s). Bigger groups mean bigger contracts")
        add("Source quality", SOURCE_POINTS.get(src, 3), 10, "Referrals and personal selling convert best")
        add("Asked for a call", 5 if d.get("wants_call") else 0, 5, "Active buying signal")
    else:
        yrs = int(d.get("years_exp") or 0)
        if d["programme"] == "emba":
            fit = 25 if 6 <= yrs <= 12 else 15 if (4 <= yrs <= 5 or 13 <= yrs <= 18) else 5
            why = "Ideal Executive MBA profile is about 6-12 years of experience (the 'Aspiring General Manager')"
        else:
            fit = 25 if 2 <= yrs <= 10 else 15 if (yrs == 1 or 11 <= yrs <= 15) else 5
            why = "Ideal certification profile is about 2-10 years (the 'Strategic Upskiller')"
        add("Profile fit", fit, 25, why)
        add("Funding", {"self": 25, "self_emi": 20, "employer_maybe": 10}.get(d.get("funding"), 0), 25,
            "Can they actually pay, and how?")
        add("Timeline", {"3m": 25, "6m": 15, "later": 5, "exploring": 0}.get(d.get("timeline"), 0), 25,
            "How soon do they want to start?")
        add("Source quality", SOURCE_POINTS.get(src, 3), 10, "Where did they come from?")
        add("Asked for a counselling call", 15 if d.get("wants_call") else 0, 15, "Active buying signal")

    score = min(100, sum(x["points"] for x in detail))
    band = "Hot" if score >= 70 else "Warm" if score >= 40 else "Cold"
    return score, band, detail


# ---------------------------------------------------------------------------
# Email templates used by the automated sequences (all simulated, never sent
# to a real inbox). {first}, {prog}, {org} are filled in per lead.
# ---------------------------------------------------------------------------
def render(template, lead):
    first = (lead["name"] or "there").split()[0]
    prog = C.PROGRAMMES[lead["programme"]]["name"]
    org = lead["org"] or "your organisation"
    b2b = lead["kind"] == "B2B"
    sign = "Admissions and Corporate Relations Team\n(Student project, not an official TAPMI offering.)"

    T = {
        "welcome": (
            f"Thanks for your interest in the {prog}",
            f"Hi {first},\n\nThanks for getting in touch about the {prog}"
            + (f" for {org}" if b2b else "")
            + ". A counsellor will reply within 1 working day. "
            + ("In the meantime, here is the overview of how the programme is delivered and priced."
               if not b2b else
               "In the meantime, here is the overview of how the programme works for sponsoring organisations.")
            + f"\n\n{sign}"),
        "nurture_1": (
            f"How organisations use the {prog}" if b2b else f"What the {prog} looks like week to week",
            f"Hi {first},\n\n"
            + ("Here is a short customer story showing how a sponsoring organisation used the programme "
               "to build its leadership pipeline, and the questions HR teams usually ask us."
               if b2b else
               "Many professionals in your position worry about fitting this around a full-time job. "
               "Here is a sample weekly schedule and what current students say about the workload.")
            + f"\n\n{sign}"),
        "nurture_2": (
            f"Is the timing right for the {prog}?",
            f"Hi {first},\n\nJust checking in. If it helps, we can arrange a 20-minute call to talk through "
            + ("budget, cohort size and how the programme would run alongside your business calendar."
               if b2b else "fees, EMI or payment options, and whether this programme is the right fit.")
            + f"\n\n{sign}"),
        "proposal_nudge": (
            f"Your {prog} proposal: any questions?",
            f"Hi {first},\n\nWe shared the next steps for the {prog}"
            + (" including a draft proposal. Happy to adjust cohort size, schedule or customisation."
               if b2b else ". The application is open. We can help with documents and payment options.")
            + f"\n\n{sign}"),
        "welcome_won": (
            f"Welcome aboard: the {prog}",
            f"Hi {first},\n\nWe're delighted that {org if b2b else 'you'} will be joining the {prog}. "
            f"You will hear from the programme office with onboarding details shortly.\n\n{sign}"),
        "retention_90": (
            "How is the programme going?",
            f"Hi {first},\n\nIt has been about three months. We'd like to hear how things are going and "
            + ("whether another cohort or a customised Management Development Programme would help other teams "
               "at " + org + "." if b2b else "whether you would like to explore the next step in your learning.")
            + f"\n\n{sign}"),
        "expansion": (
            "Next step for your people development plan",
            f"Hi {first},\n\n"
            + ("Following the first cohort, here is how organisations typically expand: repeat MDP cohorts, "
               "certification progression for the same employees, and Executive MBA nominations for high-potential staff."
               if b2b else
               "Your certification credits can be stacked into the Executive MBA within 24 months, which reduces "
               "future MBA time and cost. Want to talk it through?")
            + f"\n\n{sign}"),
        "referral": (
            "Know someone who would benefit?",
            f"Hi {first},\n\nIf a colleague or friend is thinking about a similar step, we'd be glad to speak to them. "
            f"Refer them and we'll make sure they get a personal counselling call.\n\n{sign}"),
    }
    return T[template]


# ---------------------------------------------------------------------------
# 1. LEAD CAPTURE
# ---------------------------------------------------------------------------
def save_lead(form, created_at=None, is_demo=0):
    """form: dict with the answers. Returns the new lead id."""
    sit = C.SITUATIONS[form["situation"]]
    d = {
        "name": form["name"].strip(), "email": form["email"].strip().lower(),
        "phone": (form.get("phone") or "").strip(), "org": (form.get("org") or "").strip(),
        "job_title": (form.get("job_title") or "").strip(),
        "situation": form["situation"], "programme": sit["programme"], "kind": sit["kind"],
        "source": form.get("source") if form.get("source") in C.SOURCES else "website",
        "role": form.get("role"), "budget": form.get("budget"), "timeline": form.get("timeline"),
        "seats": int(form.get("seats") or 1), "years_exp": int(form.get("years_exp") or 0),
        "funding": form.get("funding"), "concern": form.get("concern"),
        "message": (form.get("message") or "").strip()[:1000],
        "wants_call": 1 if form.get("wants_call") else 0,
    }
    score, band, detail = score_lead(d)
    when = created_at or now()
    value = C.estimate_value(d["situation"], d["seats"])
    # Auto-qualification: Hot leads skip straight to "Qualified (SQL)".
    stage = "Qualified (SQL)" if band == "Hot" else "New enquiry"

    conn = db()
    cur = conn.execute(
        """INSERT INTO leads(created_at,name,email,phone,org,job_title,situation,programme,kind,source,
           role,budget,timeline,seats,years_exp,funding,concern,message,wants_call,score,band,
           score_detail,est_value,stage,is_demo)
           VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (ts(when), d["name"], d["email"], d["phone"], d["org"], d["job_title"], d["situation"],
         d["programme"], d["kind"], d["source"], d["role"], d["budget"], d["timeline"], d["seats"],
         d["years_exp"], d["funding"], d["concern"], d["message"], d["wants_call"], score, band,
         json.dumps(detail), value, stage, is_demo))
    lead_id = cur.lastrowid
    log(conn, lead_id, f"Lead captured from {C.SOURCES[d['source']]} via the {sit['label']} form.", when)
    log(conn, lead_id, f"Scored {score}/100 ({band}). "
        + ("Auto-qualified as SQL (score 70 or more)." if band == "Hot"
           else "Marketing-qualified: placed in nurture." if band == "Warm"
           else "Low score: long, low-touch nurture."), when)
    conn.commit()
    conn.close()
    schedule_sequence(lead_id, when)
    return lead_id


# ---------------------------------------------------------------------------
# 4. AUTOMATED FOLLOW-UPS
# ---------------------------------------------------------------------------
def add_task(conn, lead_id, due, title, kind, template=None, auto=1):
    conn.execute("INSERT INTO tasks(lead_id,created_at,due_at,title,kind,template,auto) VALUES(?,?,?,?,?,?,?)",
                 (lead_id, ts(now()), ts(due), title, kind, template, auto))


def schedule_sequence(lead_id, start):
    """The follow-up plan depends on the lead's band (Hot / Warm / Cold)."""
    conn = db()
    lead = conn.execute("SELECT * FROM leads WHERE id=?", (lead_id,)).fetchone()
    day = lambda n: start + timedelta(days=n)
    who = "buyer" if lead["kind"] == "B2B" else "applicant"

    add_task(conn, lead_id, start, "Auto-reply: welcome email", "email", "welcome")
    if lead["band"] == "Hot":
        add_task(conn, lead_id, day(1), f"Call the {who} within 24 hours (hot lead)", "call", auto=0)
        add_task(conn, lead_id, day(3), "Auto-email: story / schedule", "email", "nurture_1")
        add_task(conn, lead_id, day(7), "Reminder: send proposal or application link if not done", "reminder", auto=0)
    elif lead["band"] == "Warm":
        add_task(conn, lead_id, day(2), "Auto-email: story / schedule", "email", "nurture_1")
        add_task(conn, lead_id, day(5), f"Reminder: book a discovery / counselling call with the {who}", "reminder", auto=0)
        add_task(conn, lead_id, day(9), "Auto-email: check-in", "email", "nurture_2")
    else:
        add_task(conn, lead_id, day(7), "Auto-email: story / schedule", "email", "nurture_1")
        add_task(conn, lead_id, day(21), "Auto-email: check-in", "email", "nurture_2")
        add_task(conn, lead_id, day(30), "Reminder: re-score this lead", "reminder", auto=0)
    conn.commit()
    conn.close()


def send_message(conn, lead_id, subject, body, status="sent", made_by="automation", when=None):
    conn.execute("INSERT INTO messages(lead_id,created_at,subject,body,status,made_by) VALUES(?,?,?,?,?,?)",
                 (lead_id, ts(when or now()), subject, body, status, made_by))


def run_automations():
    """Fire every automatic email whose due date has arrived. Returns how many were sent."""
    conn = db()
    sent = 0
    rows = conn.execute("""SELECT t.*, l.name FROM tasks t JOIN leads l ON l.id=t.lead_id
                           WHERE t.status='open' AND t.kind='email' AND t.auto=1 AND t.due_at<=?""",
                        (ts(now()),)).fetchall()
    for t in rows:
        lead = conn.execute("SELECT * FROM leads WHERE id=?", (t["lead_id"],)).fetchone()
        subject, body = render(t["template"], lead)
        due = parse(t["due_at"])
        send_message(conn, lead["id"], subject, body, "sent", "automation", due)
        conn.execute("UPDATE tasks SET status='done' WHERE id=?", (t["id"],))
        log(conn, lead["id"], f"Automation sent email: {subject}", due)
        sent += 1
    conn.commit()
    conn.close()
    return sent


# ---------------------------------------------------------------------------
# 3. PIPELINE + 5. RETENTION / DEVELOPMENT
# ---------------------------------------------------------------------------
def change_stage(lead_id, new_stage, who="Admin"):
    conn = db()
    lead = conn.execute("SELECT * FROM leads WHERE id=?", (lead_id,)).fetchone()
    if new_stage not in C.stage_names(lead["kind"]) or new_stage == lead["stage"]:
        conn.close()
        return
    conn.execute("UPDATE leads SET stage=? WHERE id=?", (new_stage, lead_id))
    log(conn, lead_id, f"{who} moved stage: {lead['stage']} to {new_stage}")
    on_stage_change(conn, lead, new_stage)
    conn.commit()
    conn.close()


def on_stage_change(conn, lead, stage):
    """Stage-triggered automations (this is where customer ACQUISITION turns into RETENTION and DEVELOPMENT)."""
    lid, t0, b2b = lead["id"], now(), lead["kind"] == "B2B"
    day = lambda n: t0 + timedelta(days=n)

    if stage == "Qualified (SQL)":
        add_task(conn, lid, day(1), "Book discovery / counselling call", "call", auto=0)
    elif stage in ("Proposal / MoU", "Application"):
        add_task(conn, lid, day(4), "Auto-email: proposal / application nudge", "email", "proposal_nudge")
        add_task(conn, lid, day(7), "Reminder: personal follow-up call on the proposal", "reminder", auto=0)
    elif stage == "Won - enrolled":
        add_task(conn, lid, t0, "Auto-email: welcome aboard", "email", "welcome_won")
        add_task(conn, lid, day(90), "Auto-email: 90-day check-in", "email", "retention_90")
        if b2b:
            add_task(conn, lid, day(120), "Reminder: pitch a repeat MDP cohort or certification progression", "reminder", auto=0)
            add_task(conn, lid, day(180), "Auto-email: expansion options", "email", "expansion")
        else:
            add_task(conn, lid, day(150), "Auto-email: stackable credits / next step", "email", "expansion")
        # nurture mail is pointless once they have bought
        conn.execute("""UPDATE tasks SET status='cancelled' WHERE lead_id=? AND status='open'
                        AND template IN ('nurture_1','nurture_2','proposal_nudge')""", (lid,))
    elif stage in ("Retention & expansion", "Alumni & referral"):
        add_task(conn, lid, day(14), "Auto-email: referral request", "email", "referral")
    elif stage == "Nurture":
        add_task(conn, lid, day(14), "Auto-email: check-in", "email", "nurture_2")
    elif stage == "Lost":
        conn.execute("UPDATE tasks SET status='cancelled' WHERE lead_id=? AND status='open'", (lid,))


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
def get_spend():
    out = {}
    for k, v in C.DEFAULT_SPEND.items():
        out[k] = int(get_setting("spend_" + k, v))
    return out


def dashboard_data():
    conn = db()
    leads = [dict(r) for r in conn.execute("SELECT * FROM leads").fetchall()]
    overdue = conn.execute("""SELECT COUNT(*) c FROM tasks WHERE status='open' AND auto=0 AND due_at<=?""",
                           (ts(now()),)).fetchone()["c"]
    conn.close()

    def idx(l):
        names = [s for s, _ in C.pipeline_for(l["kind"])]
        return names.index(l["stage"]) if l["stage"] in names else 0

    won = [l for l in leads if idx(l) >= 4 and l["stage"] not in C.SIDE_STAGES]
    open_ = [l for l in leads if l["stage"] not in ("Lost",) and idx(l) < 4]
    total = len(leads)

    funnel_labels = ["Enquiry", "Call booked", "Qualified (SQL)", "Proposal / application", "Enrolled / contracted"]
    funnel = []
    for i, label in enumerate(funnel_labels):
        funnel.append({"label": label, "count": sum(1 for l in leads if idx(l) >= i and l["stage"] != "Lost")})

    spend = get_spend()
    by_source = []
    for key, label in C.SOURCES.items():
        ls = [l for l in leads if l["source"] == key]
        w = [l for l in ls if idx(l) >= 4]
        sp = spend.get(key, 0)
        by_source.append({"key": key, "label": label, "leads": len(ls),
                          "sql": sum(1 for l in ls if idx(l) >= 2 and l["stage"] != "Lost"),
                          "won": len(w), "spend": sp,
                          "cpl": round(sp / len(ls)) if ls and sp else 0,
                          "cpa": round(sp / len(w)) if w and sp else 0})

    by_sit = []
    for key, s in C.SITUATIONS.items():
        ls = [l for l in leads if l["situation"] == key]
        by_sit.append({"key": key, "label": s["short"], "leads": len(ls),
                       "hot": sum(1 for l in ls if l["band"] == "Hot"),
                       "won": sum(1 for l in ls if idx(l) >= 4),
                       "value": sum(l["est_value"] for l in ls if l["stage"] != "Lost")})

    pipeline_value = sum(l["est_value"] for l in open_)
    weighted = round(sum(l["est_value"] * C.stage_probability(l["kind"], l["stage"]) for l in open_))
    won_value = sum(l["est_value"] for l in won)
    total_spend = sum(spend.values())
    bands = {b: sum(1 for l in leads if l["band"] == b) for b in ("Hot", "Warm", "Cold")}

    return {
        "total": total, "bands": bands,
        "sql_rate": round(100 * sum(1 for l in leads if idx(l) >= 2 and l["stage"] != "Lost") / total) if total else 0,
        "win_rate": round(100 * len(won) / total) if total else 0,
        "won_count": len(won), "won_value": won_value,
        "pipeline_value": pipeline_value, "weighted": weighted,
        "overdue": overdue, "total_spend": total_spend,
        "blended_cpl": round(total_spend / total) if total else 0,
        "blended_cpa": round(total_spend / len(won)) if won else 0,
        "funnel": funnel, "by_source": by_source, "by_sit": by_sit,
        "target_leads": int(get_setting("target_leads", 30)),
        "target_wins": int(get_setting("target_wins", 5)),
        "spend": spend,
    }


# ---------------------------------------------------------------------------
# Demo data: one or more TEST LEADS per buyer situation (dummy people only)
# ---------------------------------------------------------------------------
DEMO = [
    # (days ago, situation, name, email, org, title, role, budget, timeline, seats, yrs, funding, source, wants_call, stage)
    (24, "EMBA_B2B", "Meera Iyer", "meera@example.com", "Northwind GCC (dummy)", "Head of Talent", "decider", "approved", "3m", 6, 0, None, "salesvisit", 1, "Proposal / MoU"),
    (20, "EMBA_B2B", "Rohit Menon", "rohit@example.com", "Bluepeak Bank (dummy)", "HR Business Partner", "influencer", "seeking", "6m", 3, 0, None, "linkedin", 0, "New enquiry"),
    (22, "EMBA_B2C", "Aarav Shah", "aarav@example.com", "", "Senior Manager, Operations", None, None, "3m", 1, 9, "self_emi", "linkedin", 1, "Won - enrolled"),
    (11, "EMBA_B2C", "Neha Kulkarni", "neha@example.com", "", "Product Lead", None, None, "exploring", 1, 7, "employer_maybe", "website", 0, "New enquiry"),
    (18, "MDP_B2B", "Sanjay Rao", "sanjay@example.com", "Orbit Systems (dummy)", "Head of L&D", "budget_owner", "approved", "3m", 25, 0, None, "referral", 1, "Won - enrolled"),
    (9, "MDP_B2B", "Priya Nair", "priya@example.com", "Granite Auto (dummy)", "L&D Manager", "initiator", "none", "later", 12, 0, None, "webinar", 0, "Discovery call"),
    (15, "CERT_B2B", "Kavita Desai", "kavita@example.com", "Helix Retail (dummy)", "Manager, Learning", "decider", "approved", "3m", 40, 0, None, "email", 1, "Qualified (SQL)"),
    (6, "CERT_B2B", "Imran Qureshi", "imran@example.com", "Finwise Services (dummy)", "Team Lead", "user", "none", "exploring", 4, 0, None, "poster", 0, "New enquiry"),
    (13, "CERT_B2C", "Ananya Pillai", "ananya@example.com", "", "Business Analyst", None, None, "3m", 1, 4, "self", "poster", 1, "Application"),
    (4, "CERT_B2C", "Vikram Joshi", "vikram@example.com", "", "Marketing Executive", None, None, "6m", 1, 3, "self_emi", "website", 0, "New enquiry"),
    (2, "CERT_B2C", "Rhea Banerjee", "rhea@example.com", "", "Analyst", None, None, "exploring", 1, 1, "employer_maybe", "email", 0, "New enquiry"),
    (21, "MDP_B2B", "Dev Malhotra", "dev@example.com", "Zenith Tech (dummy)", "VP HR", "decider", "seeking", "3m", 20, 0, None, "salesvisit", 1, "Lost"),
]


def seed_demo():
    """Only runs when the database is empty, so your real test leads are never wiped."""
    conn = db()
    n = conn.execute("SELECT COUNT(*) c FROM leads").fetchone()["c"]
    conn.close()
    if n:
        return
    for (ago, sit, name, email, org, title, role, budget, tl, seats, yrs, fund, src, call, stage) in DEMO:
        when = now() - timedelta(days=ago)
        lid = save_lead({"situation": sit, "name": name, "email": email, "org": org, "job_title": title,
                         "role": role, "budget": budget, "timeline": tl, "seats": seats, "years_exp": yrs,
                         "funding": fund, "source": src, "wants_call": call,
                         "message": "Demo lead (dummy data)."}, created_at=when, is_demo=1)
        if stage != "New enquiry":
            change_stage_at(lid, stage, when + timedelta(days=2))
    run_automations()
    # Pretend the team already handled the older call/reminder tasks, so the demo
    # starts with only a few genuinely overdue items.
    conn = db()
    conn.execute("UPDATE tasks SET status='done' WHERE auto=0 AND status='open' AND due_at < ?",
                 (ts(now() - timedelta(days=6)),))
    conn.commit()
    conn.close()


def change_stage_at(lead_id, stage, when):
    """Seed helper: same as change_stage but stamped in the past so tasks/dates look natural."""
    conn = db()
    lead = conn.execute("SELECT * FROM leads WHERE id=?", (lead_id,)).fetchone()
    if lead["stage"] != stage:
        conn.execute("UPDATE leads SET stage=? WHERE id=?", (stage, lead_id))
        log(conn, lead_id, f"Admin moved stage: {lead['stage']} to {stage}", when)
        # temporarily schedule relative to 'when'
        global now
        real_now = now
        now = lambda: when
        try:
            on_stage_change(conn, lead, stage)
        finally:
            now = real_now
        conn.commit()
    conn.close()
