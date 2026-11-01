
"""
ai.py - AI capability inside the CRM.

Features:
1. Summarises each lead.
2. Assigns High / Medium / Low priority.
3. Recommends the next action for the counsellor.
4. Drafts a personalised follow-up email.

Human approval is always required before an email is sent.

Modes:
- gemini: Uses Google Gemini API when an API key is available.
- template: Uses a rule-based fallback when no API key is available
  or when the Gemini request fails.
"""

import json
import os

import requests
import content as C


GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")


def facts_for(programme):
    """Return only the approved facts for a programme."""

    p = C.PROGRAMMES[programme]

    lines = [
        f"Programme: {p['name']}. {p['summary']}"
    ]

    lines += [
        f"{key}: {value}"
        for key, value in p["facts"]
    ]

    if p["price_headline_b2b"]:
        lines.append(f"Price (B2B): {p['price_headline_b2b']}")

    if p["price_headline_b2c"]:
        lines.append(f"Price (B2C): {p['price_headline_b2c']}")

    return "\n".join(lines)


def build_prompt(lead):
    """Build the prompt sent to Gemini."""

    sit = C.SITUATIONS[lead["situation"]]

    return f"""
You are an assistant for the admissions and corporate relations team
of a business school executive-education unit.

This is a student project, not an official offering.

LEAD DETAILS

Buyer situation: {sit['label']} ({lead['kind']})
Name: {lead['name']}
Title: {lead['job_title']}
Organisation: {lead['org'] or 'n/a (individual)'}
Decision-making role: {lead['role'] or 'n/a'}
Budget: {lead['budget'] or 'n/a'}
Timeline: {lead['timeline']}
Participants: {lead['seats']}
Years of experience: {lead['years_exp']}
Funding: {lead['funding'] or 'n/a'}
Source: {lead['source']}
Message: {lead['message'] or '(none)'}

Rule-based score: {lead['score']}/100 ({lead['band']})

FACTS YOU MAY USE (nothing else):

{facts_for(lead['programme'])}

RULES:

- Never promise admission, placement, salary, rankings or accreditation.
- Never quote a price that is not listed above.
- If asked about anything not listed, say a counsellor will confirm.
- Keep the email under 130 words.
- Make the email warm and specific.
- Include one clear call to action.
- Sign off as "Admissions and Corporate Relations Team".
- Never send the email yourself.

Reply with valid JSON only, containing exactly these keys:

{{
    "priority": "High, Medium or Low",
    "summary": "Maximum 2 sentences",
    "reasons": ["Reason 1", "Reason 2"],
    "next_action": "One sentence for the human counsellor",
    "draft_subject": "Email subject",
    "draft_body": "Email body"
}}
"""


def template_analysis(lead):
    """
    Rule-based fallback.
    Works without an internet connection or Gemini API key.
    """

    priority = {
        "Hot": "High",
        "Warm": "Medium",
        "Cold": "Low"
    }.get(lead["band"], "Low")

    first = lead["name"].split()[0]

    programme = C.PROGRAMMES[lead["programme"]]["name"]

    if lead["kind"] == "B2B":

        summary = (
            f"{lead['name']} "
            f"({lead['job_title'] or 'role not given'}) "
            f"at {lead['org'] or 'an organisation'} "
            f"is enquiring about the {programme} "
            f"for {lead['seats']} participant(s)."
        )

        if priority == "High":
            action = (
                "Call within 24 hours to confirm budget and cohort size, "
                "then share a tailored proposal."
            )
        else:
            action = (
                "Send the customer story and offer a discovery call."
            )

        body = (
            f"Hi {first},\n\n"
            f"Thank you for your interest in the {programme}. "
            f"Based on what you shared about {lead['seats']} participant(s), "
            "I'd like to set up a short call to understand your goals "
            "and timeline, and then outline how the programme could run "
            "for your teams.\n\n"
            "Would a 20-minute call this week work?\n\n"
            "Admissions and Corporate Relations Team"
        )

    else:

        summary = (
            f"{lead['name']} "
            f"({lead['job_title'] or 'role not given'}) "
            f"has about {lead['years_exp']} years of experience "
            f"and is considering the {programme}."
        )

        if priority == "High":
            action = (
                "Offer a counselling call within 24 hours "
                "and explain payment options."
            )
        else:
            action = (
                "Send the weekly-schedule overview and invite "
                "them to a counselling call."
            )

        body = (
            f"Hi {first},\n\n"
            f"Thank you for your interest in the {programme}. "
            "Many professionals ask how it fits around a full-time job "
            "and how fees can be managed, so I'd be glad to walk you "
            "through both on a short call.\n\n"
            "Would a 20-minute call this week suit you?\n\n"
            "Admissions and Corporate Relations Team"
        )

    try:
        score_details = json.loads(lead["score_detail"])
    except (TypeError, ValueError, KeyError):
        score_details = []

    reasons = [
        f"{d['factor']}: {d['points']}/{d['max']}"
        for d in score_details
        if d["points"] >= d["max"] * 0.6
    ][:3]

    if not reasons:
        reasons = ["Limited buying signals so far"]

    return {
        "priority": priority,
        "summary": summary,
        "reasons": reasons,
        "next_action": action,
        "draft_subject": f"Your enquiry about the {programme}",
        "draft_body": body,
        "mode": "template"
    }


def analyse(lead):
    """
    Analyse a lead.

    Accepts a SQLite Row or dictionary.
    Always attempts to return a valid analysis dictionary.
    """

    # No API key: use the template immediately.
    if not GEMINI_KEY:
        return template_analysis(lead)

    try:

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{GEMINI_MODEL}:generateContent"
        )

        response = requests.post(
            url,
            headers={
                "x-goog-api-key": GEMINI_KEY,
                "Content-Type": "application/json"
            },
            json={
                "contents": [
                    {
                        "parts": [
                            {
                                "text": build_prompt(lead)
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "responseMimeType": "application/json",
                    "temperature": 0.4
                }
            },
            timeout=25
        )

        response.raise_for_status()

        result_text = (
            response.json()["candidates"][0]
            ["content"]["parts"][0]["text"]
        )

        data = json.loads(result_text)

        required_keys = [
            "priority",
            "summary",
            "reasons",
            "next_action",
            "draft_subject",
            "draft_body"
        ]

        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key: {key}")

        if data["priority"] not in ("High", "Medium", "Low"):
            raise ValueError("Invalid priority returned by Gemini")

        if isinstance(data["reasons"], str):
            data["reasons"] = [data["reasons"]]

        data["mode"] = "gemini"

        return data

    except Exception as exc:

        # If Gemini fails, the CRM still works using the template.
        output = template_analysis(lead)

        output["note"] = (
            f"Gemini call failed ({type(exc).__name__}); "
            "template used instead."
        )

        return output
