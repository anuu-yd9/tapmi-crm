"""
app.py  -  the web server. Run it with:   python app.py
Every page of the website and the CRM admin area is defined here.
"""
import json
import os
import re
from functools import wraps

from flask import (Flask, Response, abort, flash, redirect, render_template, request,
                   session, url_for)

import ai
import content as C
import crm

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "tapmi-demo")
SITE_PASSWORD = os.environ.get("SITE_PASSWORD", "")   # optional: password-protect the WHOLE site
SITE_USER = os.environ.get("SITE_USER", "instructor")

crm.init_db()
crm.seed_demo()


# ---------------------------------------------------------------------------
# Template helpers
# ---------------------------------------------------------------------------
@app.template_filter("inr")
def inr(n):
    """1250000 -> ₹12,50,000 (Indian digit grouping)."""
    n = int(round(n or 0))
    s = str(abs(n))
    if len(s) > 3:
        head, tail = s[:-3], s[-3:]
        parts = []
        while len(head) > 2:
            parts.insert(0, head[-2:])
            head = head[:-2]
        if head:
            parts.insert(0, head)
        s = ",".join(parts + [tail])
    return ("-" if n < 0 else "") + "₹" + s


@app.template_filter("inr_short")
def inr_short(n):
    """Compact rupees for tiles: 12471000 -> ₹1.25 Cr, 3450000 -> ₹34.5 L."""
    n = n or 0
    if n >= 10000000:
        return "₹%.2f Cr" % (n / 10000000)
    if n >= 100000:
        return "₹%.1f L" % (n / 100000)
    return inr(n)


@app.template_filter("ist")
def ist(value, fmt="%d %b %Y, %H:%M"):
    """Database stores UTC; show India time."""
    from datetime import timedelta
    return (crm.parse(value) + timedelta(hours=5, minutes=30)).strftime(fmt)


@app.context_processor
def inject():
    return {"DISCLAIMER": C.DISCLAIMER, "SITUATIONS": C.SITUATIONS, "PROGRAMMES": C.PROGRAMMES,
            "SOURCES": C.SOURCES, "is_admin": session.get("admin", False)}


@app.before_request
def site_gate():
    """If SITE_PASSWORD is set, the whole site asks for a username/password (instructor access)."""
    if not SITE_PASSWORD or request.path == "/healthz":
        return None
    auth = request.authorization
    if auth and auth.username == SITE_USER and auth.password == SITE_PASSWORD:
        return None
    return Response("Password needed.", 401, {"WWW-Authenticate": 'Basic realm="Student project"'})


def admin_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if not session.get("admin"):
            return redirect(url_for("login", next=request.path))
        return f(*a, **kw)
    return wrapper


# ---------------------------------------------------------------------------
# PUBLIC WEBSITE
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/for-organisations")
def for_orgs():
    return render_template("pathway.html", kind="B2B")


@app.route("/for-individuals")
def for_people():
    return render_template("pathway.html", kind="B2C")


@app.route("/programme/<code>")
def programme(code):
    if code not in C.PROGRAMMES:
        abort(404)
    kind = request.args.get("for", "B2B" if code == "mdp" else "B2B")
    return render_template("programme.html", code=code, p=C.PROGRAMMES[code], kind=kind)


@app.route("/assets")
def assets():
    return render_template("assets.html", types=C.ASSET_TYPES, links=C.ASSET_LINKS)


@app.route("/how-it-works")
def how_it_works():
    return render_template("how.html")


FIELD_ERRORS = {
    "name": "Enter your full name.",
    "email": "Enter a valid email address, like name@company.com.",
    "consent": "Tick the box so we can contact you about this enquiry.",
}


@app.route("/enquire/<situation>", methods=["GET", "POST"])
def enquire(situation):
    if situation not in C.SITUATIONS:
        abort(404)
    sit = C.SITUATIONS[situation]
    form = request.form if request.method == "POST" else {}
    errors = {}
    if request.method == "POST":
        if request.form.get("company_website"):          # honeypot: bots fill this, humans never see it
            return redirect(url_for("thanks", situation=situation))
        if len(form.get("name", "").strip()) < 2:
            errors["name"] = FIELD_ERRORS["name"]
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", form.get("email", "").strip()):
            errors["email"] = FIELD_ERRORS["email"]
        if not form.get("consent"):
            errors["consent"] = FIELD_ERRORS["consent"]
        if sit["kind"] == "B2B" and not form.get("org", "").strip():
            errors["org"] = "Enter your organisation's name."
        for f in ("seats", "years_exp"):
            if form.get(f) and not form.get(f).isdigit():
                errors[f] = "Enter a whole number."
        if not errors:
            data = dict(form)
            data["situation"] = situation
            crm.save_lead(data)
            return redirect(url_for("thanks", situation=situation))
    src = request.args.get("src") or form.get("source") or session.get("src") or "website"
    if src in C.SOURCES:
        session["src"] = src
    return render_template("enquire.html", sit=sit, key=situation, form=form, errors=errors,
                           src=src if src in C.SOURCES else "website",
                           roles=C.ROLES_B2B, budgets=C.BUDGET_B2B, timelines=C.TIMELINE,
                           fundings=C.FUNDING_B2C, concerns=C.CONCERNS)


@app.route("/thanks/<situation>")
def thanks(situation):
    if situation not in C.SITUATIONS:
        abort(404)
    return render_template("thanks.html", sit=C.SITUATIONS[situation], key=situation)


@app.route("/robots.txt")
def robots():
    return Response("User-agent: *\nDisallow: /\n", mimetype="text/plain")


@app.route("/healthz")
def healthz():
    return "ok"


# ---------------------------------------------------------------------------
# ADMIN / CRM
# ---------------------------------------------------------------------------
@app.route("/admin/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(request.args.get("next") or url_for("dashboard"))
        error = "That password is not right. Try again."
    return render_template("admin/login.html", error=error)


@app.route("/admin/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("home"))


@app.route("/admin")
@admin_required
def dashboard():
    return render_template("admin/dashboard.html", d=crm.dashboard_data(),
                           offset=int(crm.get_setting("clock_offset_days", "0")),
                           sources=C.SOURCES)


@app.route("/admin/leads")
@admin_required
def leads():
    q = {"situation": request.args.get("situation", ""), "band": request.args.get("band", ""),
         "stage": request.args.get("stage", "")}
    sql, args = "SELECT * FROM leads WHERE 1=1", []
    for col, val in q.items():
        if val:
            sql += f" AND {col}=?"
            args.append(val)
    sql += " ORDER BY score DESC, created_at DESC"
    conn = crm.db()
    rows = conn.execute(sql, args).fetchall()
    conn.close()
    all_stages = sorted({s for k in ("B2B", "B2C") for s in C.stage_names(k)})
    return render_template("admin/leads.html", leads=rows, q=q, all_stages=all_stages)


@app.route("/admin/leads/<int:lead_id>")
@admin_required
def lead_detail(lead_id):
    conn = crm.db()
    lead = conn.execute("SELECT * FROM leads WHERE id=?", (lead_id,)).fetchone()
    if not lead:
        conn.close()
        abort(404)
    tasks = conn.execute("SELECT * FROM tasks WHERE lead_id=? ORDER BY due_at", (lead_id,)).fetchall()
    msgs = conn.execute("SELECT * FROM messages WHERE lead_id=? ORDER BY created_at DESC, id DESC", (lead_id,)).fetchall()
    acts = conn.execute("SELECT * FROM activity WHERE lead_id=? ORDER BY created_at DESC, id DESC", (lead_id,)).fetchall()
    conn.close()
    pipeline = [s for s, _ in C.pipeline_for(lead["kind"])]
    return render_template("admin/lead.html", lead=lead, tasks=tasks, msgs=msgs, acts=acts,
                           detail=json.loads(lead["score_detail"]),
                           ai=json.loads(lead["ai_json"]) if lead["ai_json"] else None,
                           pipeline=pipeline, side=C.SIDE_STAGES, now=crm.ts(crm.now()))


@app.route("/admin/leads/<int:lead_id>/stage", methods=["POST"])
@admin_required
def set_stage(lead_id):
    crm.change_stage(lead_id, request.form["stage"])
    return redirect(url_for("lead_detail", lead_id=lead_id))


@app.route("/admin/leads/<int:lead_id>/ai", methods=["POST"])
@admin_required
def run_ai(lead_id):
    conn = crm.db()
    lead = conn.execute("SELECT * FROM leads WHERE id=?", (lead_id,)).fetchone()
    result = ai.analyse(dict(lead))
    conn.execute("UPDATE leads SET ai_json=? WHERE id=?", (json.dumps(result), lead_id))
    crm.send_message(conn, lead_id, result["draft_subject"], result["draft_body"], "draft", "ai")
    crm.log(conn, lead_id, f"AI analysis run ({result['mode']} mode). Follow-up email drafted for human approval.")
    conn.commit()
    conn.close()
    return redirect(url_for("lead_detail", lead_id=lead_id))


@app.route("/admin/messages/<int:msg_id>/approve", methods=["POST"])
@admin_required
def approve_message(msg_id):
    conn = crm.db()
    m = conn.execute("SELECT * FROM messages WHERE id=?", (msg_id,)).fetchone()
    subject = request.form.get("subject", m["subject"])
    body = request.form.get("body", m["body"])
    conn.execute("UPDATE messages SET status='sent', subject=?, body=?, created_at=? WHERE id=?",
                 (subject, body, crm.ts(crm.now()), msg_id))
    crm.log(conn, m["lead_id"], "A human approved and sent the AI-drafted email (simulated send).")
    conn.commit()
    conn.close()
    return redirect(url_for("lead_detail", lead_id=m["lead_id"]))


@app.route("/admin/tasks")
@admin_required
def tasks():
    conn = crm.db()
    rows = conn.execute("""SELECT t.*, l.name, l.situation FROM tasks t JOIN leads l ON l.id=t.lead_id
                           WHERE t.status='open' ORDER BY t.due_at""").fetchall()
    conn.close()
    return render_template("admin/tasks.html", tasks=rows, now=crm.ts(crm.now()))


@app.route("/admin/tasks/<int:task_id>/done", methods=["POST"])
@admin_required
def task_done(task_id):
    conn = crm.db()
    t = conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
    conn.execute("UPDATE tasks SET status='done' WHERE id=?", (task_id,))
    crm.log(conn, t["lead_id"], f"Task completed: {t['title']}")
    conn.commit()
    conn.close()
    return redirect(request.form.get("back") or url_for("tasks"))


@app.route("/admin/outbox")
@admin_required
def outbox():
    conn = crm.db()
    rows = conn.execute("""SELECT m.*, l.name FROM messages m JOIN leads l ON l.id=m.lead_id
                           ORDER BY m.created_at DESC, m.id DESC LIMIT 100""").fetchall()
    conn.close()
    return render_template("admin/outbox.html", msgs=rows)


@app.route("/admin/run", methods=["POST"])
@admin_required
def run_now():
    n = crm.run_automations()
    flash(f"Automations ran: {n} follow-up email(s) sent.")
    return redirect(request.form.get("back") or url_for("dashboard"))


@app.route("/admin/clock", methods=["POST"])
@admin_required
def clock():
    days = int(request.form.get("days", 0))
    if days == 0:
        crm.set_setting("clock_offset_days", 0)
        flash("Demo clock reset to real time.")
    else:
        crm.set_setting("clock_offset_days", int(crm.get_setting("clock_offset_days", "0")) + days)
        n = crm.run_automations()
        flash(f"Fast-forwarded {days} day(s). Automations ran: {n} follow-up email(s) sent.")
    return redirect(url_for("dashboard"))


@app.route("/admin/settings", methods=["POST"])
@admin_required
def settings():
    for k in C.SOURCES:
        v = request.form.get("spend_" + k, "")
        if v.isdigit():
            crm.set_setting("spend_" + k, v)
    for k in ("target_leads", "target_wins"):
        v = request.form.get(k, "")
        if v.isdigit() and int(v) > 0:
            crm.set_setting(k, v)
    flash("Targets and spend saved.")
    return redirect(url_for("dashboard") + "#assumptions")


@app.route("/admin/reset-demo", methods=["POST"])
@admin_required
def reset_demo():
    conn = crm.db()
    for t in ("leads", "tasks", "messages", "activity", "settings"):
        conn.execute(f"DELETE FROM {t}")
    conn.commit()
    conn.close()
    crm.seed_demo()
    flash("Everything was reset to the starting demo data.")
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 5001)))
