import json
import os
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


state = AppState()


# Request/Response Models
class RecommendRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5


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

    return all_items


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager to load resources on startup."""
    print("Starting up Wat's New API...")

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
    Get semantic recommendations based on a query.

    - **query**: The student interest text to search for
    - **top_k**: Number of results to return (default: 5)
    """
    query = request.query
    top_k = min(request.top_k, len(state.all_items))  # Cap at max items

    if state.model is None or state.all_embeddings is None:
        return RecommendResponse(query=query, results=[])

    # Encode the query
    query_vector = state.model.encode(query)

    # Calculate cosine similarities
    similarities = util.cos_sim(query_vector, state.all_embeddings)[0]

    # Get top k indices
    top_indices = np.argsort(similarities.numpy())[-top_k:][::-1]

    # Build response
    results = []
    for idx in top_indices:
        item = state.all_items[idx]
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
            link=item.get('link', ''),
            source=source,
            match_score=round(score * 100, 2),
            item_type=item_type
        ))

    return RecommendResponse(query=query, results=results)


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
