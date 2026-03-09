import feedparser
import json
import os
import re
from datetime import datetime

def scrape_rss_feeds():
    print("Initializing RSS Sniper (UWaterloo Drupal Events)...")
    
    target_feeds = [
        "https://cs.uwaterloo.ca/events/events.xml",
        "https://uwaterloo.ca/artificial-intelligence-institute/events/events.xml",
        "https://uwaterloo.ca/cybersecurity-privacy-institute/events/events.xml"
    ]
    
    whitelist_keywords = [
        'ai', 'machine learning', 'neural', 'software', 'thesis', 'seminar', 
        'colloquium', 'hci', 'human-computer', 'devops', 'systems', 
        'cybersecurity', 'data science', 'research'
    ]
    
    blacklist_keywords = [
        'pizza', 'yoga', 'social', 'coffee', 'mixer', 'movie', 'party'
    ]
    
    all_opportunities = []
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    for url in target_feeds:
        print(f"Deploying RSS crawler to: {url}")
        try:
            feed = feedparser.parse(url)
            projects_found = 0
            
            for entry in feed.entries:
                title = entry.get('title', '')
                link = entry.get('link', '')
                raw_description = entry.get('summary', '')
                
                # Strip raw HTML tags
                description = re.sub(r'<[^>]+>', '', raw_description).strip()
                
                # Combine title and description for keyword matching
                combined_text = f"{title} {description}".lower()
                
                # Check blacklist
                if any(black_kw in combined_text for black_kw in blacklist_keywords):
                    continue
                    
                # Check whitelist
                if any(white_kw in combined_text for white_kw in whitelist_keywords):
                    snippet = f"Academic Event: {title}. {description[:300]}..."
                    if len(description) > 300:
                        snippet += "..."
                        
                    all_opportunities.append({
                        "title": title,
                        "link": link,
                        "snippet": snippet,
                        "source": "rss_sniper",
                        "date_fetched": current_date
                    })
                    projects_found += 1
                    
            print(f"  -> Extracted {projects_found} high-signal academic events.")
            
        except Exception as e:
            print(f"  -> Critical error parsing RSS feed: {e}")

    # Save to live_opportunities.json
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir) if os.path.basename(current_dir) == 'src' else current_dir
    data_dir = os.path.join(project_root, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    output_file = os.path.join(data_dir, "live_opportunities.json")
    
    existing_data = []
    if os.path.exists(output_file):
        with open(output_file, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                pass

    existing_data.extend(all_opportunities)
    
    print(f"\nWriting {len(all_opportunities)} RSS academic events to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)
        
    print("RSS Sniping Complete!")

if __name__ == "__main__":
    scrape_rss_feeds()
