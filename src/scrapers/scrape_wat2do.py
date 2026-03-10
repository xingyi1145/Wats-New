"""
Wat2Do Event Harvester

Fetches live student events from the wat2do.ca backend API,
filters expired events, and merges them into data/live_opportunities.json.
"""

import json
import os
import re
from datetime import datetime, timezone, timedelta

import requests

# ============================================================================
# Configuration
# ============================================================================

API_URL = "https://api.wat2do.ca/api/events/"
REQUEST_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; WatsNew-Spider/1.0)"}

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
while os.path.basename(project_root) in ['src', 'scrapers', 'tests']:
    project_root = os.path.dirname(project_root)
data_dir = os.path.join(project_root, "data")
os.makedirs(data_dir, exist_ok=True)

OUTPUT_FILE = os.path.join(data_dir, "live_opportunities.json")


# ============================================================================
# Helpers
# ============================================================================

def first_two_sentences(text: str) -> str:
    """Return the first two sentences of a string."""
    if not text:
        return ""
    # Split on sentence-ending punctuation followed by whitespace
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return " ".join(sentences[:2]).strip()


def parse_utc(dt_string: str) -> datetime | None:
    """Parse an ISO 8601 UTC datetime string."""
    if not dt_string:
        return None
    try:
        # Handle both "Z" suffix and "+00:00" offset
        dt_string = dt_string.replace("Z", "+00:00")
        return datetime.fromisoformat(dt_string)
    except (ValueError, TypeError):
        return None


def is_expired(event: dict) -> bool:
    """Return True if the event has already ended."""
    now = datetime.now(timezone.utc)

    end = parse_utc(event.get("dtend_utc"))
    if end:
        return end < now

    # Fallback: dtstart_utc + 2 hours
    start = parse_utc(event.get("dtstart_utc"))
    if start:
        return (start + timedelta(hours=2)) < now

    # No date info at all — keep the event
    return False


# ============================================================================
# Fetch all pages
# ============================================================================

def fetch_all_events() -> list[dict]:
    """Paginate through the wat2do API and return all raw event dicts."""
    all_events: list[dict] = []
    url = API_URL
    page = 1
    max_pages = 200  # Safety limit
    last_cursor = None

    while page <= max_pages:
        print(f"  Fetching page {page}: {url}")
        try:
            resp = requests.get(url, timeout=15, headers=REQUEST_HEADERS)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"  ✗ Request failed: {e}")
            break

        data = resp.json()
        results = data.get("results", [])
        all_events.extend(results)
        print(f"    → Got {len(results)} events (running total: {len(all_events)})")

        if not data.get("hasMore", False):
            break

        cursor = data.get("nextCursor")
        if not cursor or cursor == last_cursor:
            print("  ⚠ Cursor not advancing. Stopping pagination.")
            break

        last_cursor = cursor
        url = f"{API_URL}?cursor={cursor}"
        page += 1

    if page > max_pages:
        print(f"  ⚠ Reached max page limit ({max_pages}). Stopping.")

    return all_events


# ============================================================================
# Map to our schema
# ============================================================================

def map_event(event: dict) -> dict:
    """Convert a wat2do event dict to our opportunity schema."""
    title = (event.get("title") or "").strip()
    link = event.get("source_url") or ""
    if not link:
        link = f"https://wat2do.ca/events/{event.get('id', '')}"

    snippet = first_two_sentences(event.get("description", ""))

    return {
        "title": title,
        "link": link,
        "snippet": snippet,
        "source": "wat2do_aggregator",
    }


# ============================================================================
# Integration
# ============================================================================

def merge_and_save(new_items: list[dict]):
    """Load existing live_opportunities.json, append new items, deduplicate, save."""
    existing: list[dict] = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
            if not isinstance(existing, list):
                existing = []
        except (json.JSONDecodeError, IOError):
            existing = []

    existing_titles = {item.get("title", "").strip().lower() for item in existing}

    added = 0
    for item in new_items:
        norm_title = item["title"].strip().lower()
        if norm_title and norm_title not in existing_titles:
            existing.append(item)
            existing_titles.add(norm_title)
            added += 1

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    print(f"\n  Added {added} new events (total on disk: {len(existing)}).")
    print(f"  Output: {OUTPUT_FILE}")


# ============================================================================
# Entry point
# ============================================================================

def main():
    print("=" * 60)
    print("  Wat2Do Event Harvester")
    print("=" * 60)

    # Step 1: Fetch all pages
    raw_events = fetch_all_events()
    print(f"\n  Fetched {len(raw_events)} total events from API.")

    # Step 2: TTL filter — drop expired events
    live_events = [e for e in raw_events if not is_expired(e)]
    expired_count = len(raw_events) - len(live_events)
    print(f"  Dropped {expired_count} expired events, {len(live_events)} are still live.")

    # Step 3: Map to our schema
    mapped = [map_event(e) for e in live_events]

    if not mapped:
        print("\n  No live events to add.")
        return

    # Step 4: Merge and save
    merge_and_save(mapped)

    print(f"\n{'='*60}")
    print("  HARVEST COMPLETE")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
