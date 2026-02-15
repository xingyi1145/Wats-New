import time
import json
import logging
import random
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from tqdm import tqdm

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

BASE_URL = "https://clubs.wusa.ca"
START_URL = "https://clubs.wusa.ca/club_listings"
OUTPUT_FILE = "wusa_clubs.json"

def get_club_urls(page) -> List[str]:
    """
    Extracts all club urls from the current listing page.
    """
    club_links = []
    # The "Learn More" buttons seem to be the reliable way to get to the detail page
    # We look for anchor tags that contain "Learn More"
    try:
        # Wait for the list to load
        page.wait_for_selector("a:has-text('Learn More')", timeout=10000)
        
        links = page.locator("a:has-text('Learn More')").all()
        for link in links:
            href = link.get_attribute("href")
            if href:
                full_url = href if href.startswith("http") else f"{BASE_URL}{href}"
                club_links.append(full_url)
    except Exception as e:
        logger.error(f"Error extracting links from listing page: {e}")
    
    return club_links

def scrape_club_details(page, url: str) -> Optional[Dict]:
    """
    Visits a club detail page and extracts: name, category, description.
    """
    try:
        page.goto(url, wait_until="domcontentloaded")
        # specific sleep to be polite and simulate human behavior
        time.sleep(random.uniform(1.0, 2.0)) 
        
        data = {
            "link": url,
            "club_name": None,
            "category": "Uncategorized", # Default if not found
            "description": ""
        }

        # Extract Name - Based on fetch, it's likely a header
        # Strategy: Look for the biggest header or specific class
        # Attempt 1: H1 or H2
        if page.locator("h1").count() > 0:
            data["club_name"] = page.locator("h1").first.inner_text().strip()
        elif page.locator("h2").count() > 0: # Some sites use h2 for title
             data["club_name"] = page.locator("h2").first.inner_text().strip()
        
        # Fallback: look for the breadcrumb last item
        if not data["club_name"]:
            breadcrumb = page.locator(".breadcrumb li:last-child") # Common pattern
            if breadcrumb.count() > 0:
                 data["club_name"] = breadcrumb.inner_text().strip()

        # Extract Category
        # Often found in specific metadata sections or badges
        # We will search for common indicators
        # Note: WUSA site variable. We'll look for common text.
        # If strict category isn't found, we can try to infer or leave as Uncategorized.
        
        # Extract Description
        # Look for "Who we are" section as seen in fetch logs
        # We can try to get the text after "Who we are" header
        who_we_are_header = page.locator("text='Who we are'")
        if who_we_are_header.count() > 0:
            # Get the parent's text or the next sibling
            # Often extracting the full main content container is safer
            # Let's try to get the container that holds the description
            # This is a heuristic.
            
            # Option A: Get the text of the parent container of "Who we are"
            container = who_we_are_header.locator("..") # Parent
            data["description"] = container.inner_text().strip()
        else:
            # Fallback: Grab all paragraph text from the main body
            # This might be noisy, but better than nothing
            paragraphs = page.locator("div.club-content p, div.description p").all_inner_texts()
            data["description"] = "\n".join(paragraphs).strip()
            
            if not data["description"]:
                 # Last resort: body text, but that's too much.
                 # Let's try looking for the main content div if standard class exists
                 content = page.locator(".content, #content, main").first
                 if content.count() > 0:
                     data["description"] = content.inner_text().strip()

        # Clean description (remove "Who we are" header text from the description if captured)
        if data["description"]:
            data["description"] = data["description"].replace("Who we are", "").strip()

        return data

    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")
        return None

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = context.new_page()

        all_club_links = []
        current_page_num = 1
        
        logger.info("Starting scrape of club list...")

        # 1. Collect all Links
        # We know there is pagination. We will loop until we can't find a "Next" button or it's disabled.
        # Or simply construct urls: ?page=1, ?page=2
        
        while True:
            url = f"{START_URL}?page={current_page_num}"
            logger.info(f"Visiting Listing Page: {url}")
            try:
                page.goto(url, wait_until="domcontentloaded")
                time.sleep(1) # Polite wait
                
                urls = get_club_urls(page)
                if not urls:
                    logger.info("No URLs found on this page. Stopping pagination.")
                    break
                
                new_links = [u for u in urls if u not in all_club_links]
                if not new_links:
                    logger.info("No new links found (duplicates). Stopping.")
                    break
                    
                all_club_links.extend(new_links)
                logger.info(f"Found {len(new_links)} clubs on page {current_page_num}. Total: {len(all_club_links)}")
                
                # Check for Next button
                # The fetch log showed "Next >"
                next_button = page.locator("a:has-text('Next ›')")
                if next_button.count() == 0 or not next_button.is_visible():
                    logger.info("Next button not found. Last page reached.")
                    break
                
                current_page_num += 1
                
            except Exception as e:
                logger.error(f"Error on listing page {url}: {e}")
                break

        logger.info(f"Collected {len(all_club_links)} unique club links.")
        
        # 2. Visit Each Club
        results = []
        # Use tqdm for progress bar
        for link in tqdm(all_club_links, desc="Scraping Clubs"):
            details = scrape_club_details(page, link)
            if details:
                results.append(details)
            
            # Rate limiting
            time.sleep(random.uniform(0.5, 1.5))

        # 3. Save
        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Scraping complete. Saved {len(results)} clubs to {OUTPUT_FILE}")
        browser.close()

if __name__ == "__main__":
    main()
