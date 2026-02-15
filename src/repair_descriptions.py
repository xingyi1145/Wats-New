import json
import time
import os
import random
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

# 1. Path Setup
# Determine paths relative to this script so it runs from anywhere
current_dir = os.path.dirname(os.path.abspath(__file__))
# Assuming structure: Projects/Wat's-New/src/repair_descriptions.py
# Data is in: Projects/Wat's-New/wusa_clubs.json
project_root = os.path.dirname(current_dir)
input_filename = os.path.join(project_root, 'wusa_clubs.json')
output_filename = os.path.join(project_root, 'wusa_clubs_fixed.json')

print(f"Reading from: {input_filename}")
print(f"Saving to: {output_filename}")

# Load data
try:
    with open(input_filename, 'r', encoding='utf-8') as f:
        clubs = json.load(f)
    print(f"Loaded {len(clubs)} clubs to process.")
except FileNotFoundError:
    print(f"Error: Could not find {input_filename}")
    exit(1)

def scrape_full_description(page, url):
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        
        # Polite wait
        time.sleep(0.5)

        # 2. HANDLE 'SHOW MORE' / EXPANSION
        # Check for multiple possible text variations for the button
        # Using a broad locator to find buttons or links with "Show More"
        show_more = page.locator('button:has-text("Show More"), a:has-text("Show More"), span:has-text("Show More")').first
        
        if show_more.is_visible():
            # print("  -> Clicking Show More...")
            try:
                show_more.click(timeout=2000)
                page.wait_for_timeout(500) # Wait for expansion
            except:
                pass # Sometimes it's visible but not clickable or already expanded
            
        # 3. EXTRACT DESCRIPTION
        # Strategy: Look for "Who we are" header, which seems standard for WUSA
        description_text = ""
        
        who_we_are_headers = page.locator("text='Who we are'")
        if who_we_are_headers.count() > 0:
            # Get the parent container
            container = who_we_are_headers.first.locator("..")
            description_text = container.inner_text()
        else:
            # Fallback 1: Generic description classes
            desc_locator = page.locator('.description, .club-description, div[class*="Description"], .content').first
            if desc_locator.count() > 0:
                description_text = desc_locator.inner_text()
            else:
                # Fallback 2: Paragraphs in main area
                paragraphs = page.locator("main p").all_inner_texts()
                description_text = "\n".join(paragraphs)

        source_text = description_text.strip()
        
        # 4. CLEANUP
        # Remove "WHO WE ARE" header if captured
        clean_text = source_text.replace("WHO WE ARE", "").replace("Who we are", "")
        # Remove "Show More" text if captured (case insensitive handling via simple replaces)
        clean_text = clean_text.replace("Show More", "").replace("Show Less", "").replace("show more", "")
        
        # Normalize whitespace
        clean_text = " ".join(clean_text.split())
        
        return clean_text

    except Exception as e:
        print(f"  -> Failed to scrape {url}: {e}")
        return None

def main():
    with sync_playwright() as p:
        # headless=True for speed, change to False to debug
        browser = p.chromium.launch(headless=True)
        # Create context with user agent to avoid blocking
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = context.new_page()
        
        # Statistics
        fixed_count = 0
        skipped_count = 0

        # Iterate through clubs
        total = len(clubs)
        
        print("Starting repair process...")
        for i, club in enumerate(clubs):
            url = club.get('link')
            current_desc = club.get('description', '')
            
            # Optimization: Only visit if description looks truncated or contains "Show More"
            # Or if it's explicitly short strings ending in "..."
            needs_fix = "Show More" in current_desc or len(current_desc) < 100 or current_desc.endswith("...")
            
            if not needs_fix:
                skipped_count += 1
                continue

            print(f"[{i+1}/{total}] Fixing: {club.get('club_name', 'Unknown')}")
            
            if not url:
                continue

            new_desc = scrape_full_description(page, url)
            
            if new_desc:
                club['description'] = new_desc
                fixed_count += 1
                # print(f"  -> Updated ({len(new_desc)} chars)")
            else:
                # If scraping failed, try to clean the existing text locally at least
                clean_existing = current_desc.replace("Show More", "").replace("WHO WE ARE", "")
                club['description'] = " ".join(clean_existing.split())

            # Save incrementally every 20 records
            if fixed_count > 0 and fixed_count % 20 == 0:
                print("  -> Saving progress...")
                with open(output_filename, 'w', encoding='utf-8') as f:
                    json.dump(clubs, f, indent=2, ensure_ascii=False)
            
            # Rate limiting
            time.sleep(random.uniform(0.5, 1.0))

        browser.close()

    # Final Save
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(clubs, f, indent=2, ensure_ascii=False)

    print(f"Done! Processed {total} clubs.")
    print(f"Fixed/Updated: {fixed_count}")
    print(f"Skipped (Already good): {skipped_count}")
    print(f"Saved to {output_filename}")

if __name__ == "__main__":
    main()
