import json
import numpy as np
from sentence_transformers import SentenceTransformer, util

print("Loading AI Model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

print("Loading Vector Database...")
try:
    with open('wusa_clubs_vectors.json', 'r', encoding='utf-8') as f:
        clubs = json.load(f)
except FileNotFoundError:
    print("Error: Could not find wusa_clubs_vectors.json")
    exit()

# Filter out any clubs that failed to get an embedding, just in case
valid_clubs = [c for c in clubs if 'embedding' in c]
# Convert the lists of floats back into a math-friendly numpy array
club_embeddings = np.array([c['embedding'] for c in valid_clubs]).astype('float32')

print("\n✅ Brain Loaded. Let's test it.")
print("-" * 40)

while True:
    # 1. Take User Input
    query = input("\nEnter a student interest (or type 'exit'): ")
    if query.lower() == 'exit':
        break
        
    # 2. Convert text to Vector
    query_vector = model.encode(query)
    
    # 3. Calculate Cosine Similarity (The "Distance" between vectors)
    similarities = util.cos_sim(query_vector, club_embeddings)[0]
    
    # 4. Get the Top 3 Matches
    # argsort sorts lowest to highest, so we take the last 3 and reverse the order
    # explicitly convert to numpy to avoid tensor slicing issues
    top_indices = np.argsort(similarities.numpy())[-3:][::-1] 
    
    print("\n🏆 Top 3 Recommendations:")
    for rank, idx in enumerate(top_indices, 1):
        club = valid_clubs[idx]
        score = similarities[idx].item()
        
        # We multiply score by 100 to make it look like a "Match Percentage"
        print(f"{rank}. [{score * 100:.1f}% Match] {club.get('club_name')} ({club.get('category')})")