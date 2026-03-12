"""
Scrape UWaterloo Sedra Student Design Centre Directory

Extracts team names, descriptions, and website links from the
accordion-style directory page and saves to data/design_teams.json.
"""

import json
import os
import re

import requests
from bs4 import BeautifulSoup

# ============================================================================
# Configuration
# ============================================================================

TARGET_URL = "https://uwaterloo.ca/sedra-student-design-centre/directory-teams"
FALLBACK_LINK = TARGET_URL

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
while os.path.basename(project_root) in ['src', 'scrapers', 'tests']:
    project_root = os.path.dirname(project_root)
data_dir = os.path.join(project_root, "data")
os.makedirs(data_dir, exist_ok=True)
OUTPUT_FILE = os.path.join(data_dir, "design_teams.json")


# ============================================================================
# Helpers
# ============================================================================

def first_sentences(text: str, n: int = 3) -> str:
    """Return the first n sentences of a string."""
    if not text:
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return " ".join(sentences[:n]).strip()


def find_website_link(block) -> str:
    """
    Extract the team website URL from a content block.
    Prefers <a> tags whose href is an external http link.
    Skips mailto: links.
    """
    for a_tag in block.find_all("a", href=True):
        href = a_tag["href"].strip()
        if href.startswith("mailto:"):
            continue
        if href.startswith("http"):
            return href
    return ""


# ============================================================================
# Scraper
# ============================================================================

def scrape_design_teams() -> list[dict]:
    print(f"Fetching: {TARGET_URL}")
    resp = requests.get(TARGET_URL, timeout=15, headers={
        "User-Agent": "Mozilla/5.0 (compatible; WatsNew-Spider/1.0)"
    })
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    main = soup.find("main") or soup

    details_blocks = main.find_all("details")
    print(f"Found {len(details_blocks)} team accordion blocks.\n")

    teams: list[dict] = []

    for block in details_blocks:
        # --- Title ---
        summary = block.find("summary")
        if not summary:
            continue
        title = summary.get_text(strip=True)
        if not title:
            continue

        # --- Content div ---
        content = block.find("div", class_="details__content")
        if not content:
            content = block

        # --- Description ---
        paragraphs = content.find_all("p")
        if paragraphs:
            full_text = " ".join(p.get_text(strip=True) for p in paragraphs)
        else:
            full_text = content.get_text(strip=True)
        snippet = first_sentences(full_text, n=3)

        # --- Link ---
        link = find_website_link(content) or FALLBACK_LINK

        teams.append({
            "title": title,
            "link": link,
            "snippet": snippet,
            "source": "sedra_design_centre",
        })

        print(f"  ✓ {title}")
        print(f"    Link: {link[:80]}")
        print(f"    Snippet: {snippet[:100]}...")

    return teams


# ============================================================================
# Entry point
# ============================================================================

def main():
    print("=" * 60)
    print("  Sedra Design Centre – Team Directory Scraper")
    print("=" * 60)

    teams = scrape_design_teams()

    if not teams:
        print("\nNo teams extracted.")
        return

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(teams, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"  Scraped {len(teams)} design teams.")
    print(f"  Saved to {OUTPUT_FILE}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
    print(f"Saved seeds to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape_design_teams()
