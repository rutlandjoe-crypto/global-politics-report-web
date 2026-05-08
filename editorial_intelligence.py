from __future__ import annotations

import re
from typing import Any


AGENCIES = ["White House", "Congress", "House", "Senate", "Supreme Court", "FBI", "DOJ", "Justice Department", "State Department", "Commerce Department", "EPA", "FTC", "FCC", "committee", "court"]
POLICY = ["tax", "immigration", "foreign policy", "health care", "budget", "redistricting", "election", "campaign", "court", "security", "labor", "education", "abortion", "climate", "housing"]
JURISDICTIONS = ["U.S.", "US", "United States", "Washington", "Virginia", "Texas", "California", "Florida", "New York", "Arizona", "Georgia", "Michigan", "Pennsylvania", "Iran", "Tehran"]
MOJIBAKE = {
    "\ufeff": "", "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"', "\u2014": "-", "\u2013": "-", "\xa0": " ",
    "â€™": "'", "â€˜": "'", "â€œ": '"', "â€\x9d": '"', "â€": '"', "â€“": "-", "â€”": "-",
    "Ã¢â‚¬â„¢": "'", "Ã¢â‚¬Ëœ": "'", "Ã¢â‚¬Å“": '"', "Ã¢â‚¬Â": '"', "Ã¢â‚¬": '"',
    "Ã¢â‚¬â€œ": "-", "Ã¢â‚¬â€": "-", "Donât": "Don't", "donât": "don't", "RenÃ©e": "Renee",
    "Ã©": "e", "Ã¡": "a", "Ã³": "o", "Ãº": "u", "Ã±": "n", "Ã¼": "u",
    "ÃƒÂ©": "e", "ÃƒÂ¡": "a", "ÃƒÂ³": "o", "ÃƒÂº": "u", "ÃƒÂ±": "n", "ÃƒÂ¼": "u",
}


def clean_text(value: Any, fallback: str = "") -> str:
    text = "" if value is None else str(value)
    for old, new in MOJIBAKE.items():
        text = text.replace(old, new)
    text = re.sub(r"\s+", " ", text).strip(" -")
    return text or fallback


def _dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        item = clean_text(item).strip("'\".,")
        key = item.lower()
        if item and key not in seen:
            seen.add(key)
            out.append(item)
    return out


def _not_headline(lines: list[str], headline: str) -> list[str]:
    headline_key = re.sub(r"[^a-z0-9]+", " ", headline.lower()).strip()
    return [line for line in _dedupe(lines) if re.sub(r"[^a-z0-9]+", " ", line.lower()).strip() != headline_key]


def _entities(text: str) -> list[str]:
    names = re.findall(r"\b(?:President|Sen\.|Rep\.|Gov\.|Judge|Justice|Mayor|Secretary)?\s*[A-Z][A-Za-z.'-]*(?:\s+[A-Z][A-Za-z.'-]*){0,3}", text)
    skip = {"The", "This", "That", "Political", "Stop", "Watch", "Source", "Global Politics Report", "Politics", "Party"}
    noisy = {"Face", "Faces", "New", "Continue", "Continues", "Pressure", "Negotiations", "Budget", "Report"}
    agencies = {agency.lower() for agency in AGENCIES}
    jurisdictions = {place.lower() for place in JURISDICTIONS}
    clean: list[str] = []
    for name in _dedupe(names):
        words = set(name.replace(".", "").split())
        if "HEADLINE" in name or name in skip or name.lower() in agencies or name.lower() in jurisdictions or words & noisy or len(name) <= 2:
            continue
        clean.append(name)
    return clean[:5]


def build_key_data(item: dict[str, Any], vertical: str = "politics") -> list[str]:
    headline = clean_text(item.get("headline") or item.get("title"))
    snapshot = clean_text(item.get("snapshot") or item.get("summary"))
    text = f"{headline}. {snapshot}. {clean_text(item.get('content'))}"
    lines: list[str] = []

    people = _entities(text)
    if people:
        lines.append(f"Person / officeholder: {', '.join(people[:4])}")
    agencies = [a for a in AGENCIES if re.search(rf"\b{re.escape(a)}\b", text, re.I)]
    if agencies:
        lines.append(f"Agency / court / committee: {', '.join(_dedupe(agencies)[:3])}")

    bill_case = re.findall(r"\b(?:[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){0,3}\s+(?:Act|Bill|Case|v\.\s+[A-Z][A-Za-z]+|Election|Poll))\b", text)
    if bill_case:
        lines.append(f"Bill / case / election / poll: {', '.join(_dedupe(bill_case)[:2])}")

    jurisdiction = [j for j in JURISDICTIONS if re.search(rf"\b{re.escape(j)}\b", text)]
    if jurisdiction:
        lines.append(f"Jurisdiction: {', '.join(_dedupe(jurisdiction)[:3])}")

    figures = re.findall(r"\$[0-9][0-9,.]*(?:\s?(?:million|billion))?|[0-9]+(?:\.[0-9]+)?%|[0-9]+-[0-9]+|[0-9]+\s?(?:votes?|seats?|days?|deadline)", text, re.I)
    if figures:
        lines.append(f"Vote / poll / deadline / figure: {', '.join(_dedupe(figures)[:3])}")

    if re.search(r"\b(Democrat|Republican|GOP|Democrats|Republicans|majority|minority|control)\b", text):
        lines.append("Party / control context: partisan response or governing leverage is part of the story")

    policies = [p for p in POLICY if p in text.lower()]
    if policies:
        lines.append(f"Policy area: {', '.join(_dedupe(policies)[:3])}")

    published = clean_text(item.get("published_at") or item.get("published") or item.get("updated_at"))
    source = clean_text(item.get("source_name") or item.get("source"))
    if published:
        lines.append(f"Published: {published}")
    if source:
        lines.append(f"Source: {source}")
    return _not_headline(lines, headline)[:6]


def build_why_it_matters(item: dict[str, Any], vertical: str = "politics") -> list[str]:
    text = clean_text(f"{item.get('headline', '')} {item.get('snapshot', '')} {item.get('content', '')}").lower()
    if any(w in text for w in ["court", "lawsuit", "warrant", "probe", "investigation", "case"]):
        return ["The legal or oversight angle can set precedent, create accountability pressure and change institutional leverage."]
    if any(w in text for w in ["election", "campaign", "poll", "democrat", "republican", "gop", "voter"]):
        return ["The campaign and party context can affect voter perception, coalition strategy and control of governing power."]
    if any(w in text for w in ["bill", "budget", "taxpayer", "policy", "proposal", "agency"]):
        return ["The policy stakes matter because they can shift public spending, legislative leverage or agency action."]
    return ["This affects political power, public accountability, policy consequences or campaign strategy."]


def build_what_to_watch(item: dict[str, Any], vertical: str = "politics") -> list[str]:
    actor = (_entities(clean_text(item.get("headline") or item.get("snapshot") or "")) or ["officials"])[0]
    return [
        f"Watch for the next statement, filing, vote, hearing or agency action involving {actor}.",
        "Track responses from lawmakers, courts, campaigns, affected voters and official records.",
    ]


def normalize_card(item: dict[str, Any], vertical: str = "politics") -> dict[str, Any]:
    card = dict(item)
    for key in ["headline", "title", "snapshot", "summary", "source", "source_name", "published", "published_at", "updated_at", "url", "content"]:
        if key in card:
            card[key] = clean_text(card.get(key))
    headline = clean_text(card.get("headline") or card.get("title"))
    key_data = build_key_data(card, vertical)
    if not key_data:
        key_data = [f"Source: {clean_text(card.get('source_name') or card.get('source'), 'Politics source')}"]
    card["key_data"] = _not_headline(key_data, headline)[:6]
    card["why_it_matters"] = _dedupe(build_why_it_matters(card, vertical))[:4]
    card["what_to_watch"] = _dedupe(build_what_to_watch(card, vertical))[:4]
    return card


def normalize_payload(payload: dict[str, Any], vertical: str = "politics") -> dict[str, Any]:
    payload = dict(payload)
    for key in ["title", "headline", "snapshot", "site", "site_name", "vertical", "updated_at", "generated_at", "published_at"]:
        if key in payload:
            payload[key] = clean_text(payload.get(key))
    for key in ["live_newsroom", "editor_signals", "homepage_cards"]:
        if isinstance(payload.get(key), list):
            payload[key] = [normalize_card(x, vertical) if isinstance(x, dict) else x for x in payload[key]]
            payload[key] = [x for x in payload[key] if not isinstance(x, dict) or clean_text(x.get("headline") or x.get("title"))]
    if isinstance(payload.get("sections"), dict):
        payload["sections"] = {k: normalize_card(v, vertical) if isinstance(v, dict) else v for k, v in payload["sections"].items()}
        payload["sections"] = {k: v for k, v in payload["sections"].items() if not isinstance(v, dict) or clean_text(v.get("headline") or v.get("title"))}
    elif isinstance(payload.get("sections"), list):
        payload["sections"] = [normalize_card(x, vertical) if isinstance(x, dict) else x for x in payload["sections"]]
        payload["sections"] = [x for x in payload["sections"] if not isinstance(x, dict) or clean_text(x.get("headline") or x.get("title"))]
    return payload
