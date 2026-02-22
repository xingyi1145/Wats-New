import json
from datetime import datetime
from ddgs import DDGS
import time

def harvest_news():
    print("Initializing News Harvester for UW Nexus (Updated)...")
    
    # Define relaxed search queries
    queries = [
        'University of Waterloo student hackathon',
        'site:uwaterloo.ca undergraduate research application',
        'site:uwaterloo.ca guest lecture seminar',
        'Waterloo student tech events'
    ]

    # Initialize DDGS
    ddgs = DDGS()
    
    # Storage for results
    all_results = []
    seen_links = set()
    
    current_date = datetime.now().strftime("%Y-%m-%d")

    print(f"Processing {len(queries)} search queries...")

    for query in queries:
        print(f"\nSearching for: {query}")
        try:
            # Fetch results (max 10, no time limit for broader results)
            # Using arguments as requested: using mapped names for clarity
            # Note: region='wt-wt' and safesearch='moderate' as requested
            results = ddgs.text(query, region='wt-wt', safesearch='moderate', max_results=10)
            
            count = 0
            if results:
                for result in results:
                    link = result.get('href')
                    
                    # Deduplication check
                    if link and link not in seen_links:
                        seen_links.add(link)
                        
                        entry = {
                            "title": result.get('title'),
                            "link": link,
                            "snippet": result.get('body'),
                            "source": "web_harvester",
                            "date_fetched": current_date
                        }
                        all_results.append(entry)
                        count += 1
            
            print(f"  -> Found {count} new unique results.")
            
            # Be polite to the search engine
            time.sleep(2)
            
        except Exception as e:
            print(f"  -> Error searching for '{query}': {str(e)}")

    # Save results
    output_file = "live_opportunities.json"
    print(f"\nSaving {len(all_results)} total unique opportunities to {output_file}...")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=4, ensure_ascii=False)
        print("Harvest complete!")
    except Exception as e:
        print(f"Error saving file: {e}")

if __name__ == "__main__":
    harvest_news()
