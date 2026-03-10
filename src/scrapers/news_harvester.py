import json
import os
from datetime import datetime
from ddgs import DDGS
import time

# Layer 1: The Bouncer (Explicitly block junk domains)
BLACKLIST_DOMAINS = [
    'wikipedia.org', 'knowyourmeme.com', 'cbc.ca', 'globalnews.ca', 
    'ctvnews.ca', 'reddit.com', 'quora.com', 'medium.com', 'facebook.com',
    'instagram.com', 'tiktok.com', 'therecord.com', 'thestar.com'
]

# Layer 2: The Keyword Requirement (Must prove it's actually UWaterloo)
REQUIRED_KEYWORDS = ['waterloo', 'uw', 'wusa']
ACTION_KEYWORDS = ['apply', 'register', 'deadline', 'join', 'hackathon', 'event', 'ticket']

def is_valid_opportunity(link, title, snippet):
    link_lower = link.lower()
    text_to_check = (title + " " + snippet).lower()

    # 1. Reject blacklisted domains
    for domain in BLACKLIST_DOMAINS:
        if domain in link_lower:
            return False
            
    # 2. Reject if it doesn't mention Waterloo explicitly
    if not any(kw in text_to_check for kw in REQUIRED_KEYWORDS):
        return False
        
    # 3. Reject if it doesn't sound like an actionable opportunity
    if not any(kw in text_to_check for kw in ACTION_KEYWORDS):
        return False
        
    return True

def harvest_news():
    print("Initializing News Harvester for UW Nexus (Strict Mode)...")
    
    # Layer 3: Targeted Search Dorks
    queries = [
        'site:devpost.com "University of Waterloo" hackathon',
        'site:lu.ma "Waterloo" tech event OR hackathon',
        'site:ticketfi.com "University of Waterloo" event',
        'site:uwaterloo.ca/news "apply" OR "register" undergraduate',
        'site:wusa.ca/events "register" OR "tickets"'
    ]

    ddgs = DDGS()
    all_results = []
    seen_links = set()
    current_date = datetime.now().strftime("%Y-%m-%d")

    print(f"Processing {len(queries)} strict search queries...")

    for query in queries:
        print(f"\nSearching for: {query}")
        try:
            results = ddgs.text(query, region='wt-wt', safesearch='moderate', max_results=10)
            
            count = 0
            if results:
                for result in results:
                    link = result.get('href', '')
                    title = result.get('title', '')
                    snippet = result.get('body', '')
                    
                    if link and link not in seen_links:
                        # Pass through our strict algorithmic filter
                        if is_valid_opportunity(link, title, snippet):
                            seen_links.add(link)
                            entry = {
                                "title": title,
                                "link": link,
                                "snippet": snippet,
                                "source": "web_harvester",
                                "date_fetched": current_date
                            }
                            all_results.append(entry)
                            count += 1
            
            print(f"  -> Found {count} valid, actionable results.")
            time.sleep(2)
            
        except Exception as e:
            print(f"  -> Error searching for '{query}': {str(e)}")

    # Save results
    current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
while os.path.basename(project_root) in ['src', 'scrapers', 'tests']:
    project_root = os.path.dirname(project_root)
    data_dir = os.path.join(project_root, 'data')
    os.makedirs(data_dir, exist_ok=True)
    output_file = os.path.join(data_dir, "live_opportunities.json")
    
    # Because we want a clean slate, we will NOT append to the old garbage data today.
    # We will overwrite it entirely.
    print(f"\nSaving {len(all_results)} highly-targeted opportunities to {output_file}...")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=4, ensure_ascii=False)
        print("Harvest complete!")
    except Exception as e:
        print(f"Error saving file: {e}")

if __name__ == "__main__":
    harvest_news()