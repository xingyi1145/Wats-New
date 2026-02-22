import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import time

def vectorize_live_data():
    # Define file paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(base_dir) == 'src':
        project_root = os.path.dirname(base_dir)
    else:
        project_root = base_dir

    input_file = os.path.join(project_root, 'live_opportunities.json')
    output_file = os.path.join(project_root, 'live_opportunities_vectors.json')

    print(f"Loading data from {input_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            events = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {input_file}")
        return

    print(f"Loaded {len(events)} events.")

    print("Loading model 'all-MiniLM-L6-v2'...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    rich_texts = []
    print("Preparing rich text for embedding...")
    for event in events:
        title = event.get('title', '') or ''
        source = event.get('source', '') or ''
        snippet = event.get('snippet', '') or ''
        
        # Construct rich_text string
        rich_text = f"Title: {title}. Source: {source}. Description: {snippet}"
        rich_texts.append(rich_text)

    print(f"Generating embeddings for {len(rich_texts)} events...")
    start_time = time.time()
    
    # Generate embeddings
    embeddings = model.encode(rich_texts, batch_size=32, show_progress_bar=True)
    
    end_time = time.time()
    print(f"Embeddings generated in {end_time - start_time:.2f} seconds.")

    print("Attaching embeddings to event data...")
    for i, event in enumerate(events):
        # Convert numpy array to list of floats
        event['embedding'] = embeddings[i].tolist()

    print(f"Saving updated data to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=4, ensure_ascii=False)

    print("Done!")

if __name__ == "__main__":
    vectorize_live_data()
