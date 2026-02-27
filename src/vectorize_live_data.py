import json
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import time

def vectorize_data_file(input_file, output_file, model):
    """
    Generic function to vectorize a JSON data file.
    
    Args:
        input_file: Path to input JSON file
        output_file: Path to output JSON file with embeddings
        model: SentenceTransformer model instance
    """
    print(f"\nLoading data from {input_file}...")
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            events = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at {input_file}")
        return False

    print(f"Loaded {len(events)} events.")

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

    print(f"Successfully vectorized {len(events)} events!")
    return True

def vectorize_live_data():
    """Vectorize local university opportunities."""
    # Define file paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(base_dir) == 'src':
        project_root = os.path.dirname(base_dir)
    else:
        project_root = base_dir

    input_file = os.path.join(project_root, 'live_opportunities.json')
    output_file = os.path.join(project_root, 'live_opportunities_vectors.json')

    print("Loading model 'all-MiniLM-L6-v2'...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    vectorize_data_file(input_file, output_file, model)
    print("Done!")

def vectorize_global_opportunities():
    """Vectorize global tech opportunities."""
    # Define file paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(base_dir) == 'src':
        project_root = os.path.dirname(base_dir)
    else:
        project_root = base_dir

    input_file = os.path.join(project_root, 'global_opportunities.json')
    output_file = os.path.join(project_root, 'global_opportunities_vectors.json')

    print("Loading model 'all-MiniLM-L6-v2'...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    vectorize_data_file(input_file, output_file, model)
    print("Done!")

def vectorize_all():
    """Vectorize both local and global opportunities."""
    print("=" * 60)
    print("VECTORIZING ALL OPPORTUNITY DATA")
    print("=" * 60)
    
    # Define file paths
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(base_dir) == 'src':
        project_root = os.path.dirname(base_dir)
    else:
        project_root = base_dir

    # Load model once for efficiency
    print("\nLoading model 'all-MiniLM-L6-v2'...")
    model = SentenceTransformer('all-MiniLM-L6-v2')

    # Vectorize local opportunities
    print("\n" + "=" * 60)
    print("1. VECTORIZING LOCAL OPPORTUNITIES")
    print("=" * 60)
    local_input = os.path.join(project_root, 'live_opportunities.json')
    local_output = os.path.join(project_root, 'live_opportunities_vectors.json')
    vectorize_data_file(local_input, local_output, model)

    # Vectorize global opportunities
    print("\n" + "=" * 60)
    print("2. VECTORIZING GLOBAL OPPORTUNITIES")
    print("=" * 60)
    global_input = os.path.join(project_root, 'global_opportunities.json')
    global_output = os.path.join(project_root, 'global_opportunities_vectors.json')
    vectorize_data_file(global_input, global_output, model)

    print("\n" + "=" * 60)
    print("ALL VECTORIZATION COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    vectorize_live_data()
