"""
Agentic Web Spider – Targeted Crawler + LLM Extraction

Crawls seed URLs up to MAX_DEPTH, follows only links that match an
opportunity-related heuristic, extracts page text, and feeds each
page to the Gemini LLM extractor from spider_prototype.py.

Results are de-duplicated and saved to data/spider_opportunities.json.
"""

import json
import os
import re
import time
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from spider_prototype import fetch_page_text, extract_opportunities_with_llm

# ============================================================================
# Path setup
# ============================================================================

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = (
    os.path.dirname(current_dir)
    if os.path.basename(current_dir) == "src"
    else current_dir
)
data_dir = os.path.join(project_root, "data")
os.makedirs(data_dir, exist_ok=True)

OUTPUT_FILE = os.path.join(data_dir, "spider_opportunities.json")

# ============================================================================
# Crawl configuration
# ============================================================================

SEED_URLS = [
    # GitHub awesome-lists of internships / fellowships
    "https://github.com/pittcsc/Summer2025-Internships",
    "https://github.com/SimplifyJobs/Summer2025-Internships",
    # MLH fellowships overview
    "https://fellowship.mlh.io/",
    # Google Summer of Code
    "https://summerofcode.withgoogle.com/",
]

MAX_DEPTH = 1  # 0 = seeds only, 1 = seeds + one hop

REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; WatsNew-Spider/1.0)"
}

POLITENESS_DELAY = 3  # seconds between requests

# ============================================================================
# Heuristic bouncer – decide which links are worth crawling
# ============================================================================

# Keywords that indicate an opportunity-related page
ALLOW_KEYWORDS = re.compile(
    r"internship|fellowship|apply|jobs|opportunity|career|program|hiring|recruit|"
    r"open.?source|gsoc|summer.?of.?code|mlh|open.?position|undergrad",
    re.IGNORECASE,
)

# Domains / patterns to always reject
BLOCK_PATTERNS = re.compile(
    r"(facebook\.com|twitter\.com|x\.com|instagram\.com|linkedin\.com/in/|"
    r"tiktok\.com|youtube\.com/watch|login|signin|sign.?up|logout|#|"
    r"mailto:|javascript:|\.pdf$|\.png$|\.jpg$|\.gif$|\.svg$|\.zip$|\.exe$|"
    r"github\.com/[^/]+/[^/]+/(stargazers|forks|branches|tags|activity|"
    r"issues|pulls?|actions|projects|wiki|security|network|graphs?|commits?|"
    r"blob/|tree/|compare|settings|archive|releases))",
    re.IGNORECASE,
)


def is_worth_crawling(url: str) -> bool:
    """
    Return True if the URL looks like it leads to an opportunity page.
    Rejects social media, auth pages, media files, and generic homepages.
    """
    # Reject blocked patterns first
    if BLOCK_PATTERNS.search(url):
        return False

    # Reject bare homepages (path is / or empty)
    parsed = urlparse(url)
    if parsed.path in ("", "/") and not parsed.query:
        return False

    # Accept if the URL itself contains opportunity-related keywords
    if ALLOW_KEYWORDS.search(url):
        return True

    return False


# ============================================================================
# Link extraction
# ============================================================================

def extract_links(html: str, base_url: str) -> list[str]:
    """
    Parse HTML and return a list of absolute URLs found in <a href="…"> tags.
    """
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for tag in soup.find_all("a", href=True):
        href = tag["href"].strip()
        if not href or href.startswith("#"):
            continue
        absolute = urljoin(base_url, href)
        # Only keep http(s) links
        if absolute.startswith(("http://", "https://")):
            links.append(absolute)
    return links


def fetch_html(url: str) -> str | None:
    """Download raw HTML. Returns None on failure."""
    try:
        resp = requests.get(url, timeout=30, headers=REQUEST_HEADERS)
        resp.raise_for_status()
        return resp.text
    except requests.RequestException as e:
        print(f"  ✗ Failed to fetch {url}: {e}")
        return None


# ============================================================================
# Main crawl loop
# ============================================================================

def crawl(seed_urls: list[str], max_depth: int) -> list[dict]:
    """
    BFS-style crawl starting from seed_urls up to max_depth hops.
    Each reachable page is fed to the LLM extractor.
    Returns a de-duplicated list of opportunity dicts.
    """
    seen_urls: set[str] = set()
    all_opportunities: list[dict] = []
    seen_links: set[str] = set()  # de-dup by opportunity link

    # Queue entries: (url, current_depth)
    queue: list[tuple[str, int]] = [(url, 0) for url in seed_urls]

    while queue:
        url, depth = queue.pop(0)

        # Normalise and skip duplicates
        url = url.split("#")[0].rstrip("/")
        if url in seen_urls:
            continue
        seen_urls.add(url)

        print(f"\n{'='*60}")
        print(f"  [{depth}/{max_depth}] Crawling: {url}")
        print(f"{'='*60}")

        # ----- Fetch raw HTML -----
        html = fetch_html(url)
        if html is None:
            continue

        # ----- Discover child links (if we haven't reached max depth) -----
        if depth < max_depth:
            child_links = extract_links(html, url)
            kept = 0
            for link in child_links:
                normalised = link.split("#")[0].rstrip("/")
                if normalised not in seen_urls and is_worth_crawling(normalised):
                    queue.append((normalised, depth + 1))
                    kept += 1
            print(f"  → Discovered {len(child_links)} links, {kept} passed the heuristic bouncer.")

        # ----- Extract visible text and run LLM -----
        try:
            page_text = fetch_page_text(url)
        except Exception as e:
            print(f"  ✗ Text extraction failed: {e}")
            time.sleep(POLITENESS_DELAY)
            continue

        if len(page_text) < 100:
            print("  ⏭ Page too short, skipping LLM call.")
            time.sleep(POLITENESS_DELAY)
            continue

        opportunities = extract_opportunities_with_llm(page_text)

        # De-duplicate by link (or title if link is empty)
        for opp in opportunities:
            key = opp.get("link") or opp.get("title", "")
            if key and key not in seen_links:
                seen_links.add(key)
                all_opportunities.append(opp)

        print(f"  ✓ Running total: {len(all_opportunities)} unique opportunities")

        # Save incrementally
        save_opportunities(all_opportunities)

        # Be polite
        time.sleep(POLITENESS_DELAY)

    return all_opportunities


# ============================================================================
# Persistence
# ============================================================================

def save_opportunities(opportunities: list[dict]):
    """
    Append new opportunities to the output file.
    Merges with any existing data and de-duplicates by link.
    """
    existing: list[dict] = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
            if not isinstance(existing, list):
                existing = []
        except (json.JSONDecodeError, IOError):
            existing = []

    existing_links = {item.get("link") for item in existing if item.get("link")}

    new_count = 0
    for opp in opportunities:
        link = opp.get("link", "")
        if link and link not in existing_links:
            existing.append(opp)
            existing_links.add(link)
            new_count += 1
        elif not link:
            # No link – append if title is unique
            existing_titles = {item.get("title") for item in existing}
            if opp.get("title") not in existing_titles:
                existing.append(opp)
                new_count += 1

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2, ensure_ascii=False)

    print(f"\nSaved {new_count} new opportunities (total on disk: {len(existing)}).")
    print(f"Output: {OUTPUT_FILE}")


# ============================================================================
# Entry point
# ============================================================================

def main():
    print("=" * 60)
    print("  Agentic Web Spider – Targeted Crawler")
    print(f"  Seeds: {len(SEED_URLS)} | Max depth: {MAX_DEPTH}")
    print("=" * 60)

    opportunities = crawl(SEED_URLS, MAX_DEPTH)

    if not opportunities:
        print("\nNo opportunities extracted across all pages.")
        return

    print(f"\n{'='*60}")
    print(f"  CRAWL COMPLETE: {len(opportunities)} unique opportunities extracted")
    print(f"{'='*60}")

    save_opportunities(opportunities)


if __name__ == "__main__":
    main()
