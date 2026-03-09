import json
import os

def compile_database():
    print("Initializing Database Compiler...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir) if os.path.basename(current_dir) == 'src' else current_dir
    data_dir = os.path.join(project_root, 'data')
    
    # The individual files written by your snipers
    source_files = [
        "raw_devpost.json",
        "raw_rss.json",
        "raw_ura.json"
    ]
    
    master_database = []
    
    for filename in source_files:
        filepath = os.path.join(data_dir, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    master_database.extend(data)
                    print(f"  -> Merged {len(data)} records from {filename}")
                except json.JSONDecodeError:
                    print(f"  -> Error reading {filename}, skipping.")
        else:
            print(f"  -> Warning: {filename} not found. Skipping.")
            
    output_file = os.path.join(data_dir, 'live_opportunities.json')
    
    print(f"\nCompiling {len(master_database)} total live opportunities to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(master_database, f, indent=4, ensure_ascii=False)
        
    print("Database Compilation Complete!")

if __name__ == "__main__":
    compile_database()