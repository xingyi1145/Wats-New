import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import time

def generate_embeddings():
    # Define file paths
    # Assuming script is run from project root or src, try to locate file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Check if we are in src
    if os.path.basename(base_dir) == 'src':
        project_root = os.path.dirname(base_dir)
    else:
        project_root = base_dir

    input_file = os.path.join(project_root, 'wusa_clubs_fixed.json')
    output_file = os.path.join(project_root, 'wusa_clubs_vectors.json')

    print(f"Loading data from {input_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            clubs = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {input_file}")
        return

    print("Loading model 'all-MiniLM-L6-v2'...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    rich_texts = []
    print("Preparing rich text for embedding...")
    for club in clubs:
        name = club.get('club_name', '') or ''
        category = club.get('category', '') or ''
        description = club.get('description', '') or ''
        
        # Construct rich_text string
        rich_text = f"Name: {name}. Category: {category}. Description: {description}"
        rich_texts.append(rich_text)

    print(f"Generating embeddings for {len(rich_texts)} clubs...")
    start_time = time.time()
    
    # Generate embeddings
    embeddings = model.encode(rich_texts, batch_size=32, show_progress_bar=True)
    
    end_time = time.time()
    print(f"Embeddings generated in {end_time - start_time:.2f} seconds.")

    print("Attaching embeddings to club data...")
    for i, club in enumerate(clubs):
        # Convert numpy array to list of floats
        club['embedding'] = embeddings[i].tolist()

    print(f"Saving updated data to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(clubs, f, indent=4)

    print("Done!")

if __name__ == "__main__":
    generate_embeddings()
