from __future__ import annotations

import html
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import requests


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(os.environ.get("GPR_OUTPUT_DIR", ROOT / "public"))
CURRENT_REPORT = ROOT / "public" / "latest_report.json"
ET_ZONE = ZoneInfo("America/New_York")

LIVE_HOURS = 12
EDITOR_HOURS = 36
FALLBACK_HOURS = 72

FEEDS = [
    ("The Hill", "https://thehill.com/feed/", False),
    ("NPR Politics", "https://feeds.npr.org/1014/rss.xml", False),
    ("The New York Times", "https://rss.nytimes.com/services/xml/rss/nyt/Politics.xml", False),
    ("BBC News", "https://feeds.bbci.co.uk/news/world/us_and_canada/rss.xml", False),
    ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml", True),
]

POLITICS_TERMS = re.compile(
    r"\b(president|trump|white house|congress|senate|senator|house|lawmakers?|"
    r"election|campaign|primary|candidate|voters?|ballot|governor|mayor|court|judge|"
    r"justice|law|policy|government|minister|parliament|military|war|sanctions?|"
    r"diplomacy|diplomatic|iran|israel|gaza|ukraine|russia|china|nato|eu|united nations)\b",
    re.IGNORECASE,
)

CATEGORY_PATTERNS = {
    "Elections": re.compile(
        r"\b(elections?|campaigns?|primar(?:y|ies)|candidates?|voters?|ballots?|polls?)\b",
        re.I,
    ),
    "Congress": re.compile(r"\b(congress|senate|senator|house|lawmakers?|committee|bill|vote)\b", re.I),
    "Courts": re.compile(r"\b(court|judge|justice|lawsuit|ruling|legal|prosecutor)\b", re.I),
    "Foreign Policy": re.compile(
        r"\b(war|military|sanctions?|diplomacy|iran|israel|gaza|ukraine|russia|china|nato|united nations)\b",
        re.I,
    ),
    "Government": re.compile(
        r"\b(president|white house|administration|governor|mayor|minister|parliament|government|policy)\b",
        re.I,
    ),
}


def clean_text(value: Any) -> str:
    text = html.unescape(str(value or ""))
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def child_text(item: ET.Element, names: tuple[str, ...]) -> str:
    for child in item:
        if child.tag.rsplit("}", 1)[-1] in names and child.text:
            return clean_text(child.text)
    return ""


def parse_date(value: str) -> datetime | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def category_for(text: str) -> str:
    for category, pattern in CATEGORY_PATTERNS.items():
        if pattern.search(text):
            return category
    return "Policy"


def fetch_feed(source_name: str, feed_url: str, topical_filter: bool) -> list[dict[str, Any]]:
    response = requests.get(
        feed_url,
        timeout=25,
        headers={"User-Agent": "GlobalPoliticsReport/1.0 (+https://www.globalpoliticsreport.com)"},
    )
    response.raise_for_status()
    root = ET.fromstring(response.content)
    now = datetime.now(timezone.utc)
    stories: list[dict[str, Any]] = []

    for item in root.findall(".//item"):
        headline = child_text(item, ("title",))
        url = child_text(item, ("link",))
        summary = child_text(item, ("description", "summary", "content"))
        published_raw = child_text(item, ("pubDate", "published", "updated", "date"))
        published_at = parse_date(published_raw)

        if not headline or not url.startswith(("http://", "https://")) or not published_at:
            continue

        combined = f"{headline} {summary}"
        if topical_filter and not POLITICS_TERMS.search(combined):
            continue

        age_hours = max(0.0, (now - published_at).total_seconds() / 3600)
        if age_hours > FALLBACK_HOURS:
            continue

        stories.append(
            {
                "headline": headline,
                "url": url,
                "summary": summary or headline,
                "published_at": published_at,
                "published": published_raw,
                "age_hours": age_hours,
                "source_name": source_name,
                "source_feed": feed_url,
                "category": category_for(combined),
            }
        )

    return stories


def dedupe(stories: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()

    for story in sorted(stories, key=lambda item: item["published_at"], reverse=True):
        title_key = re.sub(r"[^a-z0-9]+", " ", story["headline"].lower()).strip()
        url_key = story["url"].split("?", 1)[0].rstrip("/")
        if not title_key or title_key in seen_titles or url_key in seen_urls:
            continue
        seen_titles.add(title_key)
        seen_urls.add(url_key)
        result.append(story)

    return result


def select_diverse(stories: list[dict[str, Any]], count: int) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    source_counts: dict[str, int] = {}

    for source_limit in (1, 2, count):
        for story in stories:
            if story in selected:
                continue
            source = story["source_name"]
            if source_counts.get(source, 0) >= source_limit:
                continue
            selected.append(story)
            source_counts[source] = source_counts.get(source, 0) + 1
            if len(selected) == count:
                return selected

    return selected


def story_card(story: dict[str, Any]) -> dict[str, Any]:
    age = story["age_hours"]
    freshness = "fresh" if age <= LIVE_HOURS else "editor_fresh" if age <= EDITOR_HOURS else "public_fallback"
    category = story["category"]
    category_label = {"Elections": "Election", "Courts": "Court"}.get(category, category)
    why = {
        "Elections": "This development may affect voter attention, campaign strategy or party positioning.",
        "Congress": "This development may affect legislative leverage, negotiations or the timing of government action.",
        "Courts": "This development may affect legal authority, enforcement or the balance of institutional power.",
        "Foreign Policy": "This development may affect alliances, security commitments or diplomatic leverage.",
        "Government": "This development may affect executive authority, public policy or government accountability.",
        "Policy": "This development may affect public policy, political strategy or institutional decision-making.",
    }[category]

    return {
        "headline": story["headline"],
        "url": story["url"],
        "snapshot": story["summary"],
        "key_data": [
            f"Source: {story['source_name']}",
            f"Politics desk: {category_label}",
            f"Published: {story['published_at'].astimezone(ET_ZONE).strftime('%b. %d, %Y at %I:%M %p ET')}",
        ],
        "why_it_matters": [
            why,
            "The practical test is whether official decisions follow the public statements and political reaction.",
        ],
        "what_to_watch": [
            "Watch for official documents, votes, rulings or agency actions.",
            "Track responses from elected officials, courts, campaigns and affected institutions.",
        ],
        "editor_note": f"Developing {category.lower()} story; prioritize verified official action and source reporting.",
        "source_feed": story["source_feed"],
        "source_name": story["source_name"],
        "published": story["published"],
        "age_hours": f"{age:.2f}",
        "freshness_status": freshness,
        "editorial_score": str(max(1, round(100 - age))),
        "urgency": "DEVELOPING" if age <= 3 else "",
    }


def build_report(stories: list[dict[str, Any]], checked: int) -> dict[str, Any]:
    if not CURRENT_REPORT.exists():
        raise RuntimeError("The existing public report is required to preserve its data contract.")

    report = json.loads(CURRENT_REPORT.read_text(encoding="utf-8"))
    live_pool = [story for story in stories if story["age_hours"] <= LIVE_HOURS]
    editor_pool = [story for story in stories if story["age_hours"] <= EDITOR_HOURS]
    live = select_diverse(live_pool, 5)

    if len(live) < 5:
        raise RuntimeError(f"Only {len(live)} Politics stories are within {LIVE_HOURS} hours; refusing stale publish.")

    editor = select_diverse([story for story in editor_pool if story not in live], 5)
    sections = select_diverse(stories, 6)
    public_sources = {story["source_name"] for story in live + editor + sections}
    if len(editor) < 3 or len(sections) < 6 or len(public_sources) < 3:
        raise RuntimeError("Current Politics mix failed minimum story or source-diversity requirements.")

    stamp = datetime.now(ET_ZONE).strftime("%Y-%m-%d %I:%M:%S %p ET")
    live_cards = [story_card(story) for story in live]
    editor_cards = [story_card(story) for story in editor]
    section_cards = [story_card(story) for story in sections]
    report.update(
        {
            "headline": live_cards[0]["headline"],
            "snapshot": live_cards[0]["snapshot"],
            "updated_at": stamp,
            "generated_at": stamp,
            "freshness": {
                "max_live_story_age_hours": LIVE_HOURS,
                "max_editor_story_age_hours": EDITOR_HOURS,
                "max_public_fallback_age_hours": FALLBACK_HOURS,
                "total_items_checked": checked,
                "live_fresh_items": len(live_pool),
                "editor_fresh_items": len(editor_pool),
                "public_fallback_items": len(stories),
                "stale_or_blocked_items": max(0, checked - len(live_pool)),
                "unknown_date_items": 0,
                "last_checked": stamp,
            },
            "live_newsroom": live_cards,
            "editor_signals": editor_cards,
            "key_storylines": [card["headline"] for card in live_cards[:3]],
            "sections": section_cards,
        }
    )
    return report


def main() -> int:
    fetched: list[dict[str, Any]] = []
    successful_feeds = 0
    for source_name, feed_url, topical_filter in FEEDS:
        try:
            items = fetch_feed(source_name, feed_url, topical_filter)
            fetched.extend(items)
            successful_feeds += 1
            print(f"{source_name}: {len(items)} current Politics items")
        except (requests.RequestException, ET.ParseError) as exc:
            print(f"WARNING: {source_name} feed failed: {exc}", file=sys.stderr)

    if successful_feeds < 3:
        print("POLITICS UPDATE FAIL: Fewer than three feeds were available.", file=sys.stderr)
        return 1

    stories = dedupe(fetched)
    try:
        report = build_report(stories, len(fetched))
    except (json.JSONDecodeError, OSError, RuntimeError) as exc:
        print(f"POLITICS UPDATE FAIL: {exc}", file=sys.stderr)
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "latest_report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    storylines = "\n".join(report["key_storylines"])
    (OUTPUT_DIR / "latest_report.txt").write_text(
        f"HEADLINE\n{report['headline']}\n\nSNAPSHOT\n{report['snapshot']}\n\n"
        f"KEY STORYLINES\n{storylines}\n",
        encoding="utf-8",
    )
    print(f"POLITICS UPDATE PASS: wrote {len(report['live_newsroom'])} live stories to {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
