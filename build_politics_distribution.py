from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from editorial_intelligence import clean_text, normalize_payload

ET = ZoneInfo("America/New_York")
BASE_DIR = Path(__file__).resolve().parent

REPORT_FILE = BASE_DIR / "politics_report.txt"

OUTPUT_JSON = BASE_DIR / "latest_report.json"
OUTPUT_TXT = BASE_DIR / "latest_report.txt"

WEB_DIR = Path(r"C:\Users\joeru\OneDrive\Desktop\global-politics-report-web")
WEB_PUBLIC = WEB_DIR / "public"

WEB_JSON = WEB_PUBLIC / "latest_report.json"
WEB_TXT = WEB_PUBLIC / "latest_report.txt"


def now_et():
    return datetime.now(ET)


def stamp():
    return now_et().strftime("%Y-%m-%d %I:%M:%S %p ET")


def read_report():
    if not REPORT_FILE.exists():
        return ""
    raw = REPORT_FILE.read_text(encoding="utf-8")
    return "\n".join(clean_text(line) for line in raw.splitlines()).strip()


def first_real_line(text: str):
    for line in text.splitlines():
        line = clean_text(line)
        if len(line) > 40 and line.upper() not in {"HEADLINE", "SNAPSHOT", "KEY STORYLINES"}:
            return line
    return "Political developments are unfolding across key areas."


def section_value(text: str, heading: str) -> str:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        if line.strip().upper() != heading:
            continue
        for value in lines[index + 1:]:
            value = clean_text(value.lstrip("- "))
            if not value:
                continue
            if value.upper() in {"HEADLINE", "SNAPSHOT", "KEY STORYLINES", "WHY IT MATTERS", "WHAT TO WATCH"}:
                return ""
            return value
    return ""


def build_payload(text: str):
    headline = section_value(text, "HEADLINE") or first_real_line(text)
    snapshot = section_value(text, "SNAPSHOT") or headline

    return normalize_payload({
        "title": "Global Politics Report",
        "site": "Global Politics Report",
        "vertical": "Politics",
        "headline": headline,
        "snapshot": snapshot,
        "updated_at": stamp(),
        "generated_at": stamp(),
        "sections": {
            "politics": {
                "title": "Politics",
                "headline": headline,
                "snapshot": snapshot,
                "content": text,
                "updated_at": stamp(),
                "source_name": "Politics Report",
            }
        }
    })


def write_files(payload, text):
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    OUTPUT_TXT.write_text(text, encoding="utf-8")

    WEB_PUBLIC.mkdir(parents=True, exist_ok=True)

    WEB_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    WEB_TXT.write_text(text, encoding="utf-8")


def main():
    print(f"[{stamp()}] POLITICS BUILD STARTED")

    text = read_report()

    if not text:
        print("No politics report found.")
        return

    payload = build_payload(text)
    write_files(payload, text)

    print(f"[{stamp()}] POLITICS BUILD COMPLETE")


if __name__ == "__main__":
    main()
