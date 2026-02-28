import json
import os
import sqlite3
from contextlib import asynccontextmanager
from typing import Optional

import numpy as np
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer, util


# Global state to hold loaded data
class AppState:
    model: SentenceTransformer = None
    all_items: list = []
    all_embeddings: np.ndarray = None
    db_path: str = None


state = AppState()


# ============================================================================
# SQLite Database Functions
# ============================================================================

def get_db_connection():
    """Get a new database connection."""
    conn = sqlite3.connect(state.db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize the SQLite database and create tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            seen_links TEXT DEFAULT '[]',
            liked_links TEXT DEFAULT '[]',
            user_vector TEXT DEFAULT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("  -> SQLite database initialized.")


def get_user_from_db(user_id: str) -> dict:
    """
    Get user state from database.
    Returns dict with seen_links (set), liked_links (set), vector (np.ndarray or None).
    Creates new user row if not exists.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    
    if row is None:
        # Create new user with empty state
        cursor.execute(
            'INSERT INTO users (user_id, seen_links, liked_links, user_vector) VALUES (?, ?, ?, ?)',
            (user_id, '[]', '[]', None)
        )
        conn.commit()
        conn.close()
        return {
            "seen_links": set(),
            "liked_links": set(),
            "vector": None
        }
    
    conn.close()
    
    # Parse JSON strings back to Python objects
    try:
        seen_links = set(json.loads(row['seen_links'])) if row['seen_links'] else set()
    except (json.JSONDecodeError, TypeError):
        seen_links = set()
    
    try:
        liked_links = set(json.loads(row['liked_links'])) if row['liked_links'] else set()
    except (json.JSONDecodeError, TypeError):
        liked_links = set()
    
    try:
        if row['user_vector']:
            vector = np.array(json.loads(row['user_vector']), dtype='float32')
        else:
            vector = None
    except (json.JSONDecodeError, TypeError):
        vector = None
    
    return {
        "seen_links": seen_links,
        "liked_links": liked_links,
        "vector": vector
    }


def save_user_to_db(user_id: str, seen_links: set, liked_links: set, user_vector: Optional[np.ndarray]):
    """
    Save user state to database.
    Converts sets to JSON lists and numpy array to JSON list.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Convert Python objects to JSON strings
    seen_links_json = json.dumps(list(seen_links))
    liked_links_json = json.dumps(list(liked_links))
    
    # Convert numpy array to JSON string (or None)
    if user_vector is not None:
        vector_json = json.dumps(user_vector.tolist())
    else:
        vector_json = None
    
    cursor.execute('''
        UPDATE users 
        SET seen_links = ?, liked_links = ?, user_vector = ?
        WHERE user_id = ?
    ''', (seen_links_json, liked_links_json, vector_json, user_id))
    
    conn.commit()
    conn.close()


def get_item_vector_by_link(link: str) -> Optional[np.ndarray]:
    """
    Find an item's embedding vector by its link.
    Returns None if not found.
    """
    for i, item in enumerate(state.all_items):
        if item.get('link') == link:
            # Return a copy to avoid modifying the base embeddings
            return state.all_embeddings[i].copy()
    return None


def normalize_vector(vec: np.ndarray) -> np.ndarray:
    """Normalize a vector for cosine similarity."""
    norm = np.linalg.norm(vec)
    if norm > 0:
        return vec / norm
    return vec


# Request/Response Models
class RecommendRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    user_id: str


class InteractRequest(BaseModel):
    user_id: str
    link: str
    action: str  # "like" or "skip"


class RecommendationItem(BaseModel):
    title: str
    link: str
    source: str
    match_score: float
    item_type: str


class RecommendResponse(BaseModel):
    query: str
    results: list[RecommendationItem]


def load_data():
    """Load the vector databases from JSON files."""
    # Determine project root
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(base_dir) == 'src':
        project_root = os.path.dirname(base_dir)
    else:
        project_root = base_dir

    all_items = []

    # Load clubs data
    clubs_path = os.path.join(project_root, 'wusa_clubs_vectors.json')
    try:
        with open(clubs_path, 'r', encoding='utf-8') as f:
            clubs = json.load(f)
        valid_clubs = [c for c in clubs if 'embedding' in c]
        for c in valid_clubs:
            c['_type'] = 'club'
        all_items.extend(valid_clubs)
        print(f"  -> Loaded {len(valid_clubs)} clubs.")
    except FileNotFoundError:
        print(f"  -> Warning: {clubs_path} not found.")

    # Load live opportunities data
    events_path = os.path.join(project_root, 'live_opportunities_vectors.json')
    try:
        with open(events_path, 'r', encoding='utf-8') as f:
            events = json.load(f)
        valid_events = [e for e in events if 'embedding' in e]
        for e in valid_events:
            e['_type'] = 'event'
        all_items.extend(valid_events)
        print(f"  -> Loaded {len(valid_events)} live events.")
    except FileNotFoundError:
        print(f"  -> Warning: {events_path} not found.")

    # Load global opportunities data
    global_path = os.path.join(project_root, 'global_opportunities_vectors.json')
    try:
        with open(global_path, 'r', encoding='utf-8') as f:
            global_opps = json.load(f)
        valid_global = [g for g in global_opps if 'embedding' in g]
        for g in valid_global:
            g['_type'] = 'global_opportunity'
        all_items.extend(valid_global)
        print(f"  -> Loaded {len(valid_global)} global opportunities.")
    except FileNotFoundError:
        print(f"  -> Warning: {global_path} not found.")

    return all_items


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to load resources on startup."""
    print("Starting up Wat's New API...")

    # Initialize SQLite database
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.basename(base_dir) == 'src':
        project_root = os.path.dirname(base_dir)
    else:
        project_root = base_dir
    state.db_path = os.path.join(project_root, 'users.db')
    print(f"Initializing SQLite database at {state.db_path}...")
    init_database()

    # Load AI Model
    print("Loading AI Model 'all-MiniLM-L6-v2'...")
    state.model = SentenceTransformer('all-MiniLM-L6-v2')

    # Load Vector Databases
    print("Loading Vector Databases...")
    state.all_items = load_data()

    if not state.all_items:
        print("Warning: No data loaded!")
    else:
        # Convert all embeddings into a single numpy array
        state.all_embeddings = np.array(
            [item['embedding'] for item in state.all_items]
        ).astype('float32')
        print(f"✅ Brain Loaded with {len(state.all_items)} total items.")

    yield  # App is running

    # Cleanup (if needed)
    print("Shutting down Wat's New API...")


# Initialize FastAPI app with lifespan
app = FastAPI(
    title="Wat's New API",
    description="Semantic search API for UWaterloo student clubs and events",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",  # Vite default port
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "message": "Wat's New API is running",
        "total_items": len(state.all_items)
    }


@app.post("/api/recommend", response_model=RecommendResponse)
async def recommend(request: RecommendRequest):
    """
    Get semantic recommendations using Dynamic Vector Shifting.

    - **query**: Initial interest text (only used if no stored vector exists)
    - **top_k**: Number of results to return (default: 5)
    - **user_id**: User identifier for tracking seen/liked items and preference vector
    
    The user's preference vector evolves based on their likes, providing
    increasingly personalized recommendations over time.
    """
    query = request.query
    user_id = request.user_id
    top_k = request.top_k

    if state.model is None or state.all_embeddings is None:
        return RecommendResponse(query=query, results=[])

    # Get user state from database
    user_state = get_user_from_db(user_id)
    seen_links = user_state["seen_links"]
    user_vector = user_state["vector"]

    # Dynamic Vector Shifting: use stored vector or encode query
    if user_vector is not None:
        # User has an evolved preference vector - use it
        search_vector = user_vector
    else:
        # First time user - encode query and store as initial vector
        search_vector = state.model.encode(query).astype('float32')
        # Save the initial vector to database
        save_user_to_db(user_id, seen_links, user_state["liked_links"], search_vector)

    # Calculate cosine similarities using the user's preference vector
    similarities = util.cos_sim(search_vector, state.all_embeddings)[0]

    # Get all indices sorted by similarity (highest first)
    all_indices = np.argsort(similarities.numpy())[::-1]

    # Filter out seen items and collect top_k unseen results
    results = []
    for idx in all_indices:
        if len(results) >= top_k:
            break
            
        item = state.all_items[idx]
        link = item.get('link', '')
        
        # Skip if user has already seen this link
        if link in seen_links:
            continue
        
        score = similarities[idx].item()
        item_type = item.get('_type', 'unknown')

        # Determine title and source based on type
        if item_type == 'club':
            title = item.get('club_name', 'Unknown Club')
            source = item.get('category', 'N/A')
        else:
            title = item.get('title', 'Unknown Event')
            source = item.get('source', 'N/A')

        results.append(RecommendationItem(
            title=title,
            link=link,
            source=source,
            match_score=round(score * 100, 2),
            item_type=item_type
        ))

    return RecommendResponse(query=query, results=results)


@app.post("/api/interact")
async def interact(request: InteractRequest):
    """
    Record user interaction and apply Dynamic Vector Shifting on likes.

    - **user_id**: User identifier
    - **link**: URL of the opportunity
    - **action**: Either "like" or "skip"
    
    When action is "like", the user's preference vector shifts toward
    the liked item's vector using: new_vector = (old * 0.8) + (liked * 0.2)
    """
    user_id = request.user_id
    link = request.link
    action = request.action.lower()

    # Validate action
    if action not in ["like", "skip"]:
        return {"error": "Action must be 'like' or 'skip'", "success": False}

    # Get user state from database
    user_state = get_user_from_db(user_id)
    seen_links = user_state["seen_links"]
    liked_links = user_state["liked_links"]
    user_vector = user_state["vector"]

    # Always add to seen_links
    seen_links.add(link)

    vector_shifted = False
    
    # If liked, apply vector shifting
    if action == "like":
        liked_links.add(link)
        
        # Apply Dynamic Vector Shifting if user has a vector
        if user_vector is not None:
            liked_item_vector = get_item_vector_by_link(link)
            
            if liked_item_vector is not None:
                # Ensure shapes match
                if user_vector.shape == liked_item_vector.shape:
                    # Apply vector shift formula: 80% user preference + 20% liked item
                    new_vector = (user_vector * 0.8) + (liked_item_vector * 0.2)
                    
                    # Re-normalize for optimal cosine similarity performance
                    user_vector = normalize_vector(new_vector)
                    vector_shifted = True

    # Save updated state to database
    save_user_to_db(user_id, seen_links, liked_links, user_vector)

    return {
        "success": True,
        "user_id": user_id,
        "action": action,
        "total_seen": len(seen_links),
        "total_liked": len(liked_links),
        "vector_shifted": vector_shifted
    }


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
