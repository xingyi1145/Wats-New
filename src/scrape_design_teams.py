"""
Scrapes the UWaterloo Sedra Student Design Centre directory to generate seed URLs.
"""

import json
import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# ============================================================================
# Configuration
# ============================================================================

TARGET_URL = "https://uwaterloo.ca/sedra-student-design-centre/directory-teams"

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = (
    os.path.dirname(current_dir)
    if os.path.basename(current_dir) == "src"
    else current_dir
)
data_dir = os.path.join(project_root, "data")
os.makedirs(data_dir, exist_ok=True)
OUTPUT_FILE = os.path.join(data_dir, "design_team_seeds.json")


def clean_url(url: str) -> str:
    """Sanitize URL: ensure it starts with http and has no trailing punctuation."""
    url = url.strip()
    if not url.startswith("http"):
        return ""
    # Remove trailing punctuation
    url = re.sub(r"[.,;'\"\(\)\[\]\|]+$", "", url)
    return url


def scrape_design_teams():
    print(f"Fetching: {TARGET_URL}")
    try:
        response = requests.get(TARGET_URL, timeout=15, headers={
            "User-Agent": "Mozilla/5.0 (compatible; WatsNew-Spider/1.0)"
        })
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch {TARGET_URL}: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Try to scope to main content area to avoid nav/footer noise
    main_content = soup.find("main") or soup.find("div", class_="region-content") or soup
    
    raw_links = set()

    # Strategy 1: Look for "Website: http..." in text
    text_nodes = main_content.find_all(string=re.compile(r"Website:\s*http", re.IGNORECASE))
    for node in text_nodes:
        # Extract the URL from the string
        match = re.search(r"Website:\s*(https?://[^\s]+)", node, re.IGNORECASE)
        if match:
            raw_links.add(match.group(1))

    # Strategy 2: Extract all external hrefs that might be team websites
    # Teams are often listed as links. We want external ones, mostly avoiding common social/spam domains.
    blocked_domains = [
        "uwaterloo.ca", "facebook.com", "twitter.com", "instagram.com", 
        "linkedin.com", "youtube.com", "tiktok.com", "github.com"
    ]
    
    for a_tag in main_content.find_all("a", href=True):
        href = a_tag["href"].strip()
        if not href.startswith("http"):
            continue
            
        parsed = urlparse(href)
        domain = parsed.netloc.lower()
        
        # Check if domain is blocked
        if any(block in domain for block in blocked_domains):
            continue
            
        raw_links.add(href)

    # Sanitize and deduplicate
    clean_links = set()
    for link in raw_links:
        cleaned = clean_url(link)
        if cleaned:
            clean_links.add(cleaned)

    # Sort for consistent output
    final_links = sorted(list(clean_links))
    
    print(f"Extracted {len(final_links)} design team seed URLs.")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_links, f, indent=2, ensure_ascii=False)
        
    print(f"Saved seeds to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape_design_teams()
