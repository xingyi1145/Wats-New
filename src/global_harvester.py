import json
from datetime import datetime
from ddgs import DDGS
import time

def harvest_global_opportunities():
    """
    Harvest top-tier global tech opportunities for undergraduates.
    Targets programs like Google Summer of Code, Microsoft Explore, Jane Street, etc.
    """
    print("Initializing Global Tech Opportunities Harvester...")
    
    # Define high-value global opportunity queries
    queries = [
        '"Google Summer of Code" 2026 application',
        '"Microsoft Explore" program undergraduate',
        'Jane Street first year trading program',
        'undergraduate open source fellowship tech',
        'MLH fellowship application'
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
            # Fetch results (max 5 high-quality results per query)
            results = ddgs.text(query, region='wt-wt', safesearch='moderate', max_results=5)
            
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
                            "source": "global_opportunity",
                            "date_fetched": current_date
                        }
                        all_results.append(entry)
                        count += 1
            
            print(f"  -> Found {count} new unique results.")
            
            # Be polite to the search engine - 2 second delay between queries
            time.sleep(2)
            
        except Exception as e:
            print(f"  -> Error searching for '{query}': {str(e)}")

    # Save results
    output_file = "global_opportunities.json"
    print(f"\nSaving {len(all_results)} total unique opportunities to {output_file}...")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=4, ensure_ascii=False)
        print("Global harvest complete!")
        print(f"Total unique opportunities harvested: {len(all_results)}")
    except Exception as e:
        print(f"Error saving file: {e}")

if __name__ == "__main__":
    harvest_global_opportunities()
