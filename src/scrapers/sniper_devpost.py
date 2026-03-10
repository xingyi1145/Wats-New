import requests
import json
import os
from datetime import datetime

def snipe_devpost():
    print("Initializing Devpost JSON Sniper (Tier 2 Data)...")
    
    # We broaden the search slightly to catch major Toronto/Canada hackathons 
    # that Waterloo students frequently commute to.
    search_queries = ["Waterloo", "Toronto", "Canada"]
    
    all_opportunities = []
    seen_urls = set()
    current_date = datetime.now().strftime("%Y-%m-%d")

    for query in search_queries:
        # We query the hidden API, filtering only for upcoming/open hackathons
        url = f"https://devpost.com/api/hackathons?q={query}&status[]=upcoming&status[]=open"
        
        try:
            # Devpost requires a standard User-Agent or they will block the request
            response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            
            if response.status_code == 200:
                data = response.json()
                hackathons = data.get('hackathons', [])
                
                for h in hackathons:
                    hack_url = h.get('url')
                    if hack_url not in seen_urls:
                        seen_urls.add(hack_url)
                        
                        # Extract the exact fields we need
                        title = h.get('title', 'Unknown Hackathon')
                        dates = h.get('submission_period_dates', 'Unknown dates')
                        themes = ", ".join([t.get('name', '') for t in h.get('themes', [])])
                        location = h.get('displayed_location', 'Online/Unknown')
                        prize = h.get('prize_amount', 'No prizes listed')
                        
                        # We construct a dense, highly informative snippet for your ML vectorizer
                        snippet = f"Location: {location}. Dates: {dates}. Themes: {themes}. Prizes: {prize}."
                        
                        all_opportunities.append({
                            "title": title,
                            "link": hack_url,
                            "snippet": snippet,
                            "source": "devpost_sniper",
                            "date_fetched": current_date
                        })
                print(f"  -> Sniped {len(hackathons)} results for '{query}'")
            else:
                print(f"  -> API rejected request for '{query}' with status {response.status_code}")
                
        except Exception as e:
            print(f"  -> Error connecting to Devpost API: {e}")

    # Save the pure data
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = current_dir
    while os.path.basename(project_root) in ['src', 'scrapers', 'tests']:
        project_root = os.path.dirname(project_root)
    data_dir = os.path.join(project_root, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    output_file = os.path.join(data_dir, "raw_devpost.json")

    if len(all_opportunities) > 0:
        print(f"\nWriting {len(all_opportunities)} high-signal Builder opportunities to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_opportunities, f, indent=4, ensure_ascii=False)
    else:
        print("Failsafe triggered: 0 items found. Aborting overwrite to protect existing data.")
        
    print("Devpost Sniping Complete!")

if __name__ == "__main__":
    snipe_devpost()