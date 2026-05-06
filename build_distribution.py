from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
BASE_DIR = Path(__file__).resolve().parent

REPORT_FILE = BASE_DIR / "politics_report.txt"

OUTPUT_JSON = BASE_DIR / "latest_report.json"
OUTPUT_TXT = BASE_DIR / "latest_report.txt"

WEB_DIR = Path(r"C:\Users\joeru\OneDrive\Desktop\global-politics-report-web")
WEB_PUBLIC = WEB_DIR / "public"

WEB_JSON = WEB_PUBLIC / "latest_report.json"
WEB_TXT = WEB_PUBLIC / "latest_report.txt"

RUN_STARTED_AT_DT = datetime.now(ET)
RUN_STARTED_AT = RUN_STARTED_AT_DT.strftime("%Y-%m-%d %I:%M:%S %p ET")
RUN_ID = RUN_STARTED_AT_DT.strftime("gpr-politics-%Y%m%d-%H%M%S-et")
RUN_ISO = RUN_STARTED_AT_DT.isoformat()


def now_et():
    return datetime.now(ET)


def stamp():
    return now_et().strftime("%Y-%m-%d %I:%M:%S %p ET")


def read_report():
    if not REPORT_FILE.exists():
        return ""
    return REPORT_FILE.read_text(encoding="utf-8").strip()


def first_real_line(text: str):
    for line in text.splitlines():
        line = line.strip()
        if len(line) > 40:
            return line
    return "Political developments are unfolding across key areas."


def add_heartbeat_to_text(text: str) -> str:
    heartbeat = f"HEARTBEAT\nGlobal Politics Report checked by GSR Network at {RUN_STARTED_AT}."

    if not text.strip():
        return heartbeat

    return f"{text.strip()}\n\n{heartbeat}"


def build_payload(text: str):
    headline = first_real_line(text)
    heartbeat_text = add_heartbeat_to_text(text)

    return {
        "title": "Global Politics Report",
        "site_name": "Global Politics Report",
        "tagline": "Built for journalists, by a journalist.",
        "headline": headline,
        "snapshot": headline,
        "updated_at": RUN_STARTED_AT,
        "generated_at": RUN_STARTED_AT,
        "published_at": RUN_STARTED_AT,
        "last_checked": RUN_STARTED_AT,
        "last_pipeline_run": RUN_STARTED_AT,
        "run_id": RUN_ID,
        "run_iso": RUN_ISO,
        "system_heartbeat": {
            "status": "live",
            "vertical": "politics",
            "run_id": RUN_ID,
            "checked_at": RUN_STARTED_AT,
            "checked_at_iso": RUN_ISO,
            "last_pipeline_run": RUN_STARTED_AT,
            "forced_freshness": True,
            "message": f"GSR Network politics pipeline completed a live heartbeat at {RUN_STARTED_AT}.",
        },
        "sections": {
            "politics": {
                "title": "Politics",
                "headline": headline,
                "snapshot": headline,
                "content": heartbeat_text,
                "updated_at": RUN_STARTED_AT,
                "generated_at": RUN_STARTED_AT,
                "published_at": RUN_STARTED_AT,
                "last_checked": RUN_STARTED_AT,
                "last_pipeline_run": RUN_STARTED_AT,
                "source_file": "politics_report.txt",
                "freshness_status": "checked",
                "heartbeat": {
                    "status": "checked",
                    "run_id": RUN_ID,
                    "checked_at": RUN_STARTED_AT,
                    "checked_at_iso": RUN_ISO,
                    "message": f"Politics checked by GSR Network at {RUN_STARTED_AT}.",
                },
            }
        },
        "freshness": {
            "status": "active",
            "forced_freshness": True,
            "last_checked": RUN_STARTED_AT,
            "last_pipeline_run": RUN_STARTED_AT,
            "run_id": RUN_ID,
            "inputs": [
                {
                    "source": "politics_report.txt",
                    "status": "present" if text else "missing",
                    "last_checked": RUN_STARTED_AT,
                    "run_id": RUN_ID,
                }
            ],
        },
        "editorial_brain": {
            "status": "active",
            "heartbeat": "active",
            "forced_freshness": "active",
            "vertical": "politics",
            "focus": [
                "Political news signals",
                "Current affairs monitoring",
                "Orderly one-line card data",
                "Heartbeat on every successful run",
                "Forced freshness fields on top-level payload and section cards",
            ],
            "version": "2026-05-02-politics-heartbeat-forced-freshness",
        },
    }


def write_files(payload, text):
    heartbeat_text = add_heartbeat_to_text(text)

    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    OUTPUT_TXT.write_text(heartbeat_text, encoding="utf-8")

    WEB_PUBLIC.mkdir(parents=True, exist_ok=True)

    WEB_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    WEB_TXT.write_text(heartbeat_text, encoding="utf-8")

    print(f"[OK] Wrote {OUTPUT_JSON}")
    print(f"[OK] Wrote {OUTPUT_TXT}")
    print(f"[OK] Wrote {WEB_JSON}")
    print(f"[OK] Wrote {WEB_TXT}")


def main():
    print(f"[{RUN_STARTED_AT}] POLITICS BUILD STARTED")
    print(f"[HEARTBEAT] Run ID: {RUN_ID}")

    text = read_report()

    if not text:
        print("No politics report found.")
        print("[WARN] No output written because source report is missing or empty.")
        return

    payload = build_payload(text)
    write_files(payload, text)

    print("[DONE] Politics heartbeat active")
    print("[DONE] Politics forced freshness active")
    print(f"[{RUN_STARTED_AT}] POLITICS BUILD COMPLETE")


if __name__ == "__main__":
    main()