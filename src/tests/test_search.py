import json
import numpy as np
from sentence_transformers import SentenceTransformer, util

print("Loading AI Model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

print("Loading Vector Databases...")

# Load clubs data
all_items = []
try:
    with open('wusa_clubs_vectors.json', 'r', encoding='utf-8') as f:
        clubs = json.load(f)
    valid_clubs = [c for c in clubs if 'embedding' in c]
    for c in valid_clubs:
        c['_type'] = 'club'  # Tag the type for display
    all_items.extend(valid_clubs)
    print(f"  -> Loaded {len(valid_clubs)} clubs.")
except FileNotFoundError:
    print("  -> Warning: wusa_clubs_vectors.json not found.")

# Load live opportunities data
try:
    with open('live_opportunities_vectors.json', 'r', encoding='utf-8') as f:
        events = json.load(f)
    valid_events = [e for e in events if 'embedding' in e]
    for e in valid_events:
        e['_type'] = 'event'  # Tag the type for display
    all_items.extend(valid_events)
    print(f"  -> Loaded {len(valid_events)} live events.")
except FileNotFoundError:
    print("  -> Warning: live_opportunities_vectors.json not found.")

if not all_items:
    print("Error: No data loaded. Exiting.")
    exit()

# Convert all embeddings into a single numpy array
all_embeddings = np.array([item['embedding'] for item in all_items]).astype('float32')

print(f"\n✅ Brain Loaded with {len(all_items)} total items. Let's test it.")
print("-" * 40)

while True:
    # 1. Take User Input
    query = input("\nEnter a student interest (or type 'exit'): ")
    if query.lower() == 'exit':
        break
        
    # 2. Convert text to Vector
    query_vector = model.encode(query)
    
    # 3. Calculate Cosine Similarity (The "Distance" between vectors)
    similarities = util.cos_sim(query_vector, all_embeddings)[0]
    
    # 4. Get the Top 5 Matches (expanded to show variety across data sources)
    # argsort sorts lowest to highest, so we take the last 5 and reverse the order
    # explicitly convert to numpy to avoid tensor slicing issues
    top_indices = np.argsort(similarities.numpy())[-5:][::-1] 
    
    print("\n🏆 Top 5 Recommendations:")
    for rank, idx in enumerate(top_indices, 1):
        item = all_items[idx]
        score = similarities[idx].item()
        item_type = item.get('_type', 'unknown')
        
        # Display differently based on type
        if item_type == 'club':
            name = item.get('club_name', 'Unknown Club')
            category = item.get('category', 'N/A')
            print(f"{rank}. [{score * 100:.1f}% Match] [CLUB] {name} ({category})")
        else:
            title = item.get('title', 'Unknown Event')
            print(f"{rank}. [{score * 100:.1f}% Match] [EVENT] {title}")