# Milestone 3, Part C: step-by-step guide (for a complete beginner)

You are building **one website + one mini-CRM** for the three programmes (Executive MBA, MDP, Certifications) and five buyer situations from Milestones 1 and 2. Everything is already written. Your job is to run it, put it on GitHub, deploy it, fill in a few blanks, and record the walkthrough.

> **Time needed:** about 2 to 3 hours the first time. Deadline: **Tuesday 3 November 2026, 11:59 PM IST**. Deploy early. Do not leave it to the last evening.

---

## 0. What is in the folder

```
tapmi-crm/
├── app.py              The web server: every page and button is defined here
├── content.py          ALL words, prices, discount tables, form choices (edit this to change the site)
├── crm.py              The CRM: lead scoring, pipeline stages, automated follow-ups, dashboard numbers
├── ai.py               The AI feature (Gemini if you add a free key, otherwise a built-in template)
├── templates/          The HTML pages
├── static/             style.css and the chart library
├── requirements.txt    The Python packages needed
├── Procfile            Tells some hosts how to start the app (Render uses its own Start Command, see Step 5)
└── GUIDE.md            This file
```

You do **not** need to understand all the code. You need to understand *what each part does*, because you will explain it in your report and your review session. Section 9 gives you the explanations.

---

## 1. Install the tools (one time)

1. **Python 3.11 or newer**: download from python.org/downloads. On Windows, tick **"Add python.exe to PATH"** on the first installer screen. This is the most common beginner mistake.
2. **PyCharm Community Edition** (free): jetbrains.com/pycharm/download. Pick "Community".
3. **Git**: git-scm.com/downloads. Accept all default options.
4. A **GitHub account**: github.com, free.
5. A **Render account**: render.com. Choose "Sign up with GitHub" later, in Step 5.

Restart your laptop once after installing so everything is found.

---

## 2. Open the project in PyCharm and run it

1. Unzip `tapmi-crm.zip` somewhere easy, like `Documents/tapmi-crm`.
2. Open PyCharm → **Open** → choose the `tapmi-crm` folder → **Trust Project**.
3. If PyCharm offers "Create a virtual environment using requirements.txt", click **OK**. If not, do it by hand:
   - Open the **Terminal** tab at the bottom of PyCharm.
   - Windows: `python -m venv .venv` then `.venv\Scripts\activate`
   - Mac: `python3 -m venv .venv` then `source .venv/bin/activate`
   - You should now see `(.venv)` at the start of the line.
   - Then: `pip install -r requirements.txt`
4. Start the website. In the terminal type:
   - Windows: `python app.py`
   - Mac: `python3 app.py`
5. Open your browser at **http://127.0.0.1:5001**. You should see the website.
6. Team login (the CRM): bottom of the page → **Team login**, or go to **http://127.0.0.1:5001/admin/login**. Password: **`tapmi-demo`**.

To stop the server, click in the terminal and press **Ctrl + C**.

The first run creates a file called `crm.db` (the database) and fills it with 12 dummy leads so the dashboard is not empty. Delete `crm.db` any time to start fresh.

### Things to try now (this is also your testing checklist)
- Click **For organisations** and **For individuals**, then open each programme and its fees.
- Submit a test enquiry on each of the five forms (use dummy details). Watch each appear in **Leads** with a score.
- Open a lead → press **Analyse lead with AI** → edit the draft → **Approve and send**.
- Open a lead → click a different pipeline stage → look at the new tasks in **Follow-up plan**.
- On the **Dashboard** press **+7 days** to fast-forward time. Automatic follow-up emails fire; see them in **Email log**.

---

## 3. Make it yours (fill in the blanks)

Open `content.py` in PyCharm. Everything you may need to change is in this one file.

| What | Where | What to do |
|---|---|---|
| Brand name "ExecutivePathways" | `templates/base.html` (search for `brand`) | Change it if your group named the brand. Do **not** copy TAPMI's logo; the disclaimer says this is a student project |
| Your prices and discounts | `PROGRAMMES` in `content.py` | Already match Milestone 2. If your group changed something, edit it and explain the change in your report |
| Asset links (video, brochure, poster, story) | `ASSET_LINKS` at the bottom of `content.py` | Paste your Canva/YouTube/Google Drive share links between the quotes. Make sure the links are set to "anyone with the link can view" |
| Marketing spend per channel | Dashboard → **Targets and spend** (no code needed) | Replace my placeholder numbers with your Task A budget |
| Launch targets | Same place | Use your own objectives (e.g. 30 leads, 5 enrolments) |

> **Important:** the spend figures, targets and demo leads are placeholder/dummy values, not research findings. In your report, label them as "illustrative assumptions". The brief penalises invented statistics presented as real.

---

## 3b. Edit a file safely
1. Change the file in PyCharm and press **Ctrl+S** (Mac: Cmd+S).
2. Stop the server (Ctrl+C) and start it again (`python app.py`).
3. Refresh the browser.

---

## 4. Put the project on GitHub (from PyCharm)

1. In PyCharm: top menu **Git → Create Git Repository** → select the `tapmi-crm` folder.
2. PyCharm may show a list of files to add; accept. The `.gitignore` file already keeps your database, secrets and virtual environment out.
3. **Git → Commit**. Tick everything → message `First version` → **Commit**.
4. **Git → GitHub → Share Project on GitHub**.
   - First time, it asks you to log in. Click **Log in via GitHub** and approve in the browser.
   - Repository name: `tapmi-crm`. Tick **Private** (Render can still read a private repo).
   - Click **Share**.
5. Refresh your repo page on github.com. You should see all the files.

Any later change: **Git → Commit** (message describing the change) → **Commit and Push**.

Terminal alternative (if the menus confuse you):
```
git init
git add .
git commit -m "First version"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/tapmi-crm.git
git push -u origin main
```

---

## 5. Deploy on Render (free)

1. Go to render.com → **Get Started** → **Sign up with GitHub** → allow access to your `tapmi-crm` repo.
2. **New +** → **Web Service** → choose your `tapmi-crm` repo → **Connect**.
3. Fill in the form:
   - **Name:** anything, e.g. `exec-pathways-demo`. This becomes your URL.
   - **Region:** Singapore (closest to India).
   - **Branch:** `main`
   - **Runtime / Language:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app --workers 1 --threads 4 --bind 0.0.0.0:$PORT`
   - **Instance type:** Free
4. Scroll to **Environment Variables** → **Add** these (names exactly as written):

   | Name | Value |
   |---|---|
   | `SECRET_KEY` | any long random text |
   | `ADMIN_PASSWORD` | a password you choose for the CRM |
   | `SITE_USER` | `instructor` |
   | `SITE_PASSWORD` | a password you choose for the whole site |
   | `GEMINI_API_KEY` | (optional, see Step 6) |

   `SITE_PASSWORD` makes the **whole website** ask for a username and password. That satisfies the brief's "unlisted or password-protected" rule. Give these credentials to your instructor in the report.
5. Click **Create Web Service**. Wait for the log to say the service is live (3 to 6 minutes). Your link looks like `https://exec-pathways-demo.onrender.com`.
6. Open it. Log in with `instructor` and your `SITE_PASSWORD`. Then go to `/admin/login` and use your `ADMIN_PASSWORD`.

### Free-tier behaviour you must know (Render's own rules)
- **It sleeps after 15 minutes without visits.** The next visit takes about a minute to wake it. **Open the site 2 minutes before** you record, and before any review session.
- **Its storage is wiped on every restart or redeploy.** The 12 demo leads are re-created automatically, but leads you added are lost. So: **record your walkthrough in one sitting**, and enter your five test leads *during* the recording. Also include screenshots in your report as permanent evidence.
- Free web services have a monthly hour limit. One project is fine.

If the build fails, open the **Logs** tab and read the last red lines. The fixes in Section 10 cover the common ones.

---

## 6. Turn on the AI (optional but recommended)

Without a key, the AI button still works in **template mode** (a rule-based draft). That is fine for a demo, but "AI-enabled CRM" scores better with a real model.

1. Go to **aistudio.google.com** and sign in with a Google account.
2. Click **Get API key** → **Create API key**. No card is needed for the free tier.
3. In Render: your service → **Environment** → add `GEMINI_API_KEY` = your key → **Save**. The service restarts.
4. Optional: if Google has retired the default model name, set `GEMINI_MODEL` to a current Flash model name shown in AI Studio.
5. Test: open any lead → **Analyse lead with AI**. The badge says **Gemini** when it worked, **Template mode** when it fell back.

Never paste your key into a file in the project or upload it to GitHub. Only put it in Render's Environment tab. (If you test locally with a key, set it in your terminal first: Windows `set GEMINI_API_KEY=your-key`, Mac `export GEMINI_API_KEY=your-key`.)

**Disclose AI use.** The brief requires an appendix listing where AI tools were used. Include: this website's code was generated with Claude's help; the CRM uses Gemini (or template mode) to summarise leads and draft emails.

---

## 7. Record the 5-minute walkthrough (suggested script)

| Time | Show | Say |
|---|---|---|
| 0:00 | Home page | Two entry paths for the two buyer types; prices from Milestone 2 |
| 0:40 | A programme page, switch organisation and individual tabs | B2B shows volume discounts; B2C shows EMI/payment options |
| 1:20 | Submit an enquiry on **EMBA for organisations** | Fields mirror the DMU: decision role, budget, timeline |
| 2:00 | CRM → Leads → the new lead | Score breakdown (BANT), band, auto-qualified |
| 2:30 | Lead page: stage buttons, follow-up plan, email log | Automation: instant welcome, then dated tasks |
| 3:00 | Submit one lead on each of the other 4 forms (quick) | One test lead per buyer situation; show them in Leads |
| 3:40 | **Analyse lead with AI** → edit draft → Approve | AI drafts, human approves |
| 4:15 | Move a lead to **Won**, then dashboard **+90 days** | Retention and development follow-ups |
| 4:45 | Dashboard | Funnel, cost per lead by source, pipeline value; what decision each metric informs |

Use Windows **Win+Alt+R** (Xbox Game Bar), Mac **Cmd+Shift+5**, or Loom/OBS.

---

## 8. Part C checklist: where each requirement lives

| Brief requirement | Where it is |
|---|---|
| Website serves all five buyer situations with distinct pathways | Home page (two entry boards), `/for-organisations`, `/for-individuals`, `/programme/<name>` with organisation/individual tabs |
| Offerings and prices from Milestone 2 | `content.py` → shown on every programme page |
| Host or link the Task B assets | `/assets` page, fed by `ASSET_LINKS` |
| Clear calls to action and lead-capture forms | Five forms at `/enquire/<situation>` |
| Information architecture, page content, SEO choices explained | Section 9d below (for your report) |
| CRM receiving leads | Built into the app (`crm.py`), admin area `/admin` |
| Pipelines/stages for B2B and B2C; lead-source tracking; qualification fields; follow-up and nurture actions | `PIPELINE_B2B/B2C` in `content.py`; `?src=` links; form fields; `schedule_sequence()` |
| Retention and development steps | `on_stage_change()` → 90-day check-in, repeat MDP/cert progression, credit stacking, referrals |
| Test lead per buyer situation moving through the pipeline | Seeded demo leads, plus the five you submit on camera |
| AI capability + where humans stay in control | `ai.py`; lead page → AI assistant; draft needs approval |
| Marketing dashboard with purpose, frequency, decision for each metric | `/admin` → "What each metric is for" |
| "Student project, not an official TAPMI offering." on every page | Black strip at the top and footer of every page |
| Unlisted or password-protected | `SITE_PASSWORD` gate, plus `noindex` tags and `robots.txt` |
| Working link + credentials, ~5 min recording, CRM config + dashboard screenshots, design rationale | Steps 5, 7, and Section 9 |

**Track source with campaign links.** Add `?src=` to any enquiry link: `…/enquire/CERT_B2C?src=poster` (use on your poster QR), `?src=linkedin`, `?src=email`, `?src=webinar`, `?src=referral`, `?src=salesvisit`. The CRM records the source and the dashboard shows cost per lead by source.

---

## 9. The reasoning to cite in your report

Your teacher said the CRM need not be full-fledged, but the report must **cite the reasoning and logic of the CRM flow**. Use this section as the backbone, and put it in your own words.

### 9a. Why this CRM design (overall)
We built a lightweight CRM into our own website instead of using a third-party platform, so that the form fields, scoring rules, pipeline stages and dashboard all trace directly to our Milestone 1 segments and our Milestone 3 Task A lead-generation design. It demonstrates the three capabilities your teacher listed: **lead capture, lead qualification, automated follow-ups and reminders**.

### 9b. The flow and the CRM objective each step serves
| Step | What happens | CRM objective |
|---|---|---|
| Capture | Form per buyer situation, source recorded | **Acquisition** |
| Qualify | Score out of 100 → Hot / Warm / Cold | **Acquisition** |
| Nurture | Instant welcome, timed emails, reminders matched to the band | **Acquisition** → conversion |
| Convert | Pipeline stages, each creating the next task (call, proposal nudge) | **Acquisition** |
| Onboard + check in | Welcome email, 90-day check-in | **Retention** |
| Expand | Repeat MDP cohorts, certification progression, EMBA nominations (B2B); credit stacking into the EMBA (B2C) | **Development** |
| Refer | Referral request after enrolment | **Development** |

### 9c. Why these qualification rules
- **B2B uses BANT** (Budget, Authority, Need, Timeline). In Milestone 1 you mapped the Decision-Making Unit (initiator, user, influencer, decider, buyer, budget owner). The form asks for the person's DMU role, so *Authority* scores highest for deciders and budget owners, and lowest for users.
- **B2C uses fit, funding, timeline and intent.** "Fit" matches your personas: the *Aspiring General Manager* (about 6 to 12 years' experience) for the EMBA, and the *Strategic Upskiller* (about 2 to 10 years) for certifications. "Funding" reflects the cost barrier your respondents raised (EMI, deferred fee).
- **Thresholds:** 70 or more = Hot (sales-qualified, human calls within 24 hours); 40 to 69 = Warm (marketing-qualified, nurture plus a call reminder); below 40 = Cold (slow nurture, re-score at 30 days). *State clearly that these thresholds are the group's design judgement, not statistically validated; a real launch would calibrate them against actual conversion data.*
- **Lifecycle terms:** Cold = lead, Warm = marketing-qualified lead (MQL), Hot = sales-qualified lead (SQL), then customer, then advocate.
- **Why rules, not a black-box model:** with no historical conversion data, an explainable rule-based score is more defensible, and counsellors can see why a lead scored what it did ("Why this score" panel).

### 9d. Information architecture, page content and SEO choices
- **Two entry paths on the home page** (organisation vs individual) because B2B and B2C buyers search and decide differently (Milestone 1). Each path lists only the programmes sold to that buyer, so a corporate buyer never wades through personal-EMI content.
- **One programme page per programme with an organisation/individual toggle**, so prices and discounts match each buyer's logic: volume discount tables for organisations, EMI/payment plans for individuals.
- **Short forms asking only what the qualification model needs**, with different fields for B2B and B2C. A "Call me" tick gives an explicit buying signal.
- **SEO:** each page has a unique title, a meta description, a single H1 and a heading hierarchy, descriptive link text, and fast static pages. *The brief requires the site to stay unlisted, so the site deliberately sets `noindex` and `robots.txt: Disallow`; state that these on-page SEO choices are built in and would be switched on for a real launch by removing the noindex tags.* In a real launch, target keywords would come from your Task A search-intent work (e.g. "executive MBA for working professionals Bengaluru").

### 9e. Automation rules (what fires, when, why)
- **Instant** welcome email (speed-to-lead; sets expectation of a one-working-day reply).
- **Hot:** call task due in 1 day; story email day 3; reminder day 7 to send a proposal.
- **Warm:** story email day 2; reminder day 5 to book a call; check-in email day 9.
- **Cold:** story email day 7; check-in day 21; re-score reminder day 30.
- **Stage-triggered:** Qualified → book call; Proposal/Application → nudge email at day 4, call reminder at day 7; Won → welcome, 90-day check-in, B2B repeat-cohort pitch at day 120 and expansion email at day 180, B2C credit-stacking email at day 150; Won or Lost cancels the leftover nurture emails.
- **Honest limitation:** the day gaps are design assumptions; the emails are simulated and logged, not sent to real inboxes.

### 9f. AI: why it earns its place, and where humans stay in control
- **Value:** counsellors spend time on calls, not triage and typing. The AI summarises the lead, recommends the next action and drafts a personalised email.
- **Control:** AI never sends. A person edits and approves every draft. The AI sees only the programme facts and fees held in `content.py` and is instructed never to promise admission, placement, salary, rankings or accreditation, nor invent a price; it must say a counsellor will confirm anything else.
- **Humans decide:** pricing exceptions, proposals, and every money conversation.
- **Fallback:** if the AI call fails or no key is set, a rule-based draft is used, and the screen says so.

### 9g. Dashboard metrics
Already listed on the dashboard page, with purpose, review frequency and the decision each informs. Copy that table into your report.

### 9h. Tool choice
Python + Flask + SQLite: free, runs on Render's free tier, and lets us tailor the pipeline to our own five buyer situations. Trade-off to state: it is a prototype, not a commercial CRM, so there is no real email delivery, no user management, and (on the free host) the database resets on restart. The brief's minimum standard is a clickable prototype; this is a working one.

---

## 10. If something goes wrong

| Problem | Fix |
|---|---|
| `python` is not recognised (Windows) | Reinstall Python and tick "Add python.exe to PATH". Or use `py app.py` |
| `ModuleNotFoundError: No module named 'flask'` | You are not in the virtual environment. Activate it (Step 2.3), then `pip install -r requirements.txt` |
| Browser shows "refused to connect" | The server is not running. Start `python app.py` and use `http://127.0.0.1:5001` |
| Port already in use | Close the other copy (Ctrl+C), or run on another port: Windows `set PORT=5002` then `python app.py`; Mac `PORT=5002 python3 app.py` |
| Render build fails on `pip install` | Open Logs. Make sure `requirements.txt` is in the repo root. Add an environment variable `PYTHON_VERSION` = `3.12.3` and redeploy |
| Render says "Application failed to respond" | Start Command must be exactly `gunicorn app:app --workers 1 --threads 4 --bind 0.0.0.0:$PORT` |
| Site takes a minute to open | Free tier waking up. Wait, then refresh |
| My test leads disappeared on Render | Free tier wipes storage on restart. Re-enter them and re-record in one sitting. Keep screenshots as evidence |
| AI badge says "Template mode" | No key, wrong key, or model name retired. Re-check `GEMINI_API_KEY` and try a current `GEMINI_MODEL` |
| Page looks unstyled | Hard-refresh: Ctrl+Shift+R (Mac: Cmd+Shift+R) |

---

## 11. Do NOT forget (not covered by the code)

- **Usability and creative testing are "desirable".** If you do them with your earlier respondents, report real results. If a respondent could not be reached, say so. Do not invent test outcomes.
- **Screenshots** of the CRM configuration (pipelines, scoring, automation rules) and the dashboard for the report.
- **Contribution document** and **AI-use appendix** (Section 6).
- Keep the Render service and your assets accessible until grades are released.
