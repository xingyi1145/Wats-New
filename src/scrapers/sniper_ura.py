import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

def snipe_uras():
    print("Initializing UWaterloo URA Sniper (Tier 1 Academic Data)...")
    
    # Standard UWaterloo CMS URL patterns for URAs
    targets = [
        {
            "faculty": "Math",
            "url": "https://cs.uwaterloo.ca/current-undergraduate-students/research-opportunities/ura"
        },
        {
            "faculty": "Engineering",
            "url": "https://uwaterloo.ca/engineering/undergraduate-students/degree-enhancement/research-opportunities/ura-supervisor-list-and-usra-placement-list"
        }
    ]
    
    all_opportunities = []
    current_date = datetime.now().strftime("%Y-%m-%d")

    for target in targets:
        print(f"\nDeploying spider to {target['faculty']} Faculty URAs...")
        try:
            # UWaterloo's firewall requires a real-looking User-Agent
            response = requests.get(target['url'], headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            
            if response.status_code != 200:
                print(f"  -> Failed to bypass firewall/fetch page. Status: {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # The UW Drupal CMS typically wraps the main text inside a 'main' tag or content div
            content_area = soup.find('main') or soup.find('div', class_='uw-content')
            
            if not content_area:
                print("  -> Could not locate the main HTML content area.")
                continue
                
            projects_found = 0
            
            # Find all tables on the page
            tables = content_area.find_all('table')
            
            if tables:
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) >= 7:
                            # Strict Engineering 7-column schema
                            department = cells[0].get_text(separator=' ', strip=True).replace('\xa0', ' ')
                            last_name = cells[1].get_text(separator=' ', strip=True).replace('\xa0', ' ')
                            first_name = cells[2].get_text(separator=' ', strip=True).replace('\xa0', ' ')
                            
                            # Snippet in 7th cell (index 6)
                            description = cells[6].get_text(separator=' ', strip=True).replace('\xa0', ' ')
                            
                            # Skip header rows or empty rows
                            if "Department" in department or "Last Name" in last_name:
                                continue
                                
                            if len(description) > 50:
                                title = f"URA: {first_name} {last_name} - {department}"
                                snippet = f"Faculty: {target['faculty']}. {description}"
                                
                                all_opportunities.append({
                                    "title": title,
                                    "link": target['url'],
                                    "snippet": snippet,
                                    "source": "ura_sniper",
                                    "date_fetched": current_date
                                })
                                projects_found += 1
                        else:
                            # Fallback for tables with fewer columns (e.g. Math faculty)
                            # Could be a 2 or 3 column table
                            row_text = " - ".join([c.get_text(separator=' ', strip=True).replace('\xa0', ' ') for c in cells])
                            if len(row_text) > 50 and "Supervisor" not in row_text:
                                snippet = f"Faculty: {target['faculty']}. {row_text}"
                                title = f"URA: {target['faculty']} Research Project"
                                
                                all_opportunities.append({
                                    "title": title,
                                    "link": target['url'],
                                    "snippet": snippet,
                                    "source": "ura_sniper",
                                    "date_fetched": current_date
                                })
                                projects_found += 1
                                
            # Fallback if no tables found, use header heuristic
            if not tables or projects_found == 0:
                # The Heuristic: Look for headers, then grab the paragraph text beneath them
                for heading in content_area.find_all(['h2', 'h3', 'strong']):
                    title = heading.get_text(strip=True)
                    
                    # Filter out generic website navigation headers
                    if len(title) < 10 or "contact" in title.lower() or "faq" in title.lower() or "deadline" in title.lower():
                        continue
                        
                    # Collect all text sibling elements until the next header
                    description_parts = []
                    for sibling in heading.find_next_siblings():
                        if sibling.name in ['h2', 'h3', 'strong']:
                            break
                        if sibling.name in ['p', 'ul', 'li']:
                            description_parts.append(sibling.get_text(separator=' ', strip=True).replace('\xa0', ' '))
                            
                    description = " ".join(description_parts)
                    
                    # If we captured a meaty description, it is likely a valid research posting
                    if len(description) > 50:
                        snippet = f"Faculty: {target['faculty']}. {description}"
                        
                        all_opportunities.append({
                            "title": f"URA: {title}",
                            "link": target['url'],
                            "snippet": snippet,
                            "source": "ura_sniper",
                            "date_fetched": current_date
                        })
                        projects_found += 1
                    
            print(f"  -> Extracted {projects_found} potential research projects.")
            
        except Exception as e:
            print(f"  -> Critical error parsing URA page: {e}")

    # Save the aggregated data
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = current_dir
    while os.path.basename(project_root) in ['src', 'scrapers', 'tests']:
        project_root = os.path.dirname(project_root)
    data_dir = os.path.join(project_root, 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    # We save to independent raw file
    output_file = os.path.join(data_dir, "raw_ura.json")

    if len(all_opportunities) > 0:
        print(f"\nWriting {len(all_opportunities)} high-signal Academic URAs to {output_file}...")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_opportunities, f, indent=4, ensure_ascii=False)
    else:
        print("Failsafe triggered: 0 items found. Aborting overwrite to protect existing data.")

    print("URA Sniping Complete!")

if __name__ == "__main__":
    snipe_uras()