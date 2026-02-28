# Wat's New API - Discovery Feed Endpoints

## Overview
The API now supports stateful user tracking with personalized recommendations that filter out previously seen content.

## Data Loaded
- **199** WUSA clubs
- **40** local opportunities (live_opportunities)
- **24** global opportunities (global_opportunities)  
- **Total: 263 items**

## Endpoints

### GET /
Health check endpoint
```bash
curl http://localhost:8000/
```

### POST /api/recommend
Get personalized recommendations filtered by user's seen history.

**Request:**
```json
{
  "query": "machine learning and AI projects",
  "top_k": 5,
  "user_id": "user_123"
}
```

**Response:**
```json
{
  "query": "machine learning and AI projects",
  "results": [
    {
      "title": "MLH Fellowship",
      "link": "https://fellowship.mlh.io/",
      "source": "global_opportunity",
      "match_score": 38.39,
      "item_type": "global_opportunity"
    }
  ]
}
```

### POST /api/interact
Record user interaction (like/skip) with an opportunity.

**Request:**
```json
{
  "user_id": "user_123",
  "link": "https://fellowship.mlh.io/",
  "action": "like"
}
```
*Actions: "like" or "skip"*

**Response:**
```json
{
  "success": true,
  "user_id": "user_123",
  "action": "like",
  "total_seen": 1,
  "total_liked": 1
}
```

## User State Management

### In-Memory Structure
```python
USER_STATE = {
  "user_123": {
    "seen_links": {"link1", "link2", ...},
    "liked_links": {"link1", ...}
  }
}
```

### Behavior
- **All interactions** add links to `seen_links`
- **Like actions** also add to `liked_links`
- **Recommendations** automatically filter out items in `seen_links`
- **User isolation**: Each user_id maintains separate history

## Testing Commands

```bash
# Get recommendations
curl -X POST http://localhost:8000/api/recommend \
  -H "Content-Type: application/json" \
  -d '{"query": "tech hackathons", "top_k": 3, "user_id": "student_1"}'

# Mark as liked
curl -X POST http://localhost:8000/api/interact \
  -H "Content-Type: application/json" \
  -d '{"user_id": "student_1", "link": "https://example.com", "action": "like"}'

# Mark as skipped
curl -X POST http://localhost:8000/api/interact \
  -H "Content-Type: application/json" \
  -d '{"user_id": "student_1", "link": "https://example.com", "action": "skip"}'
```

## Running the Server

```bash
# Development mode (auto-reload)
cd /home/xingy/Projects/Wats-New
.venv/bin/python src/api.py

# The server runs on http://0.0.0.0:8000
```
