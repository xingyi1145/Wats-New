# WAT'S NEW: Phase 2 Vision & Roadmap

## 1. The MVP Conclusion (Where We Are)
We successfully built a **Semantic Search Application**. 
* **Data:** Aggregated 200+ WUSA clubs and live local UWaterloo events.
* **Brain:** Implemented local vectorization using `sentence-transformers` (`all-MiniLM-L6-v2`).
* **Stack:** FastAPI backend connected to a Next.js/Tailwind frontend.
* **The Verdict:** The MVP proved that vector math can successfully map student "vibes" to concrete opportunities. However, it fails to fully "break the bubble" because it relies on local-only data and requires the user to proactively search. 

## 2. The Strategic Pivot (The "Why")
To truly break the information gap for undergraduate students, the system must evolve across three pillars:
1. **Scope (Local $\rightarrow$ Global):** Students don't just want local clubs; they want world-class opportunities (Jane Street, GSoC, Microsoft Explore). The engine must bridge global tech opportunities with local student profiles.
2. **UX (Search $\rightarrow$ Discovery):** A search bar assumes the user knows what they want. To show users what they *don't* know, the UI must shift to a "Discovery Feed" (swipe/card based) that pushes opportunities to them.
3. **Intelligence (Semantic Match $\rightarrow$ Recommendation System):** The backend must become stateful. It needs to track user interactions (swipes, clicks, saves) and mathematically adjust their user-vector in real-time, moving towards a Collaborative Filtering or Two-Tower neural network model.

## 3. The Execution Roadmap (Phase 2)

### Step 1: The Global Harvester [CURRENT]
* **Goal:** Expand the vector database beyond UWaterloo.
* **Action:** Build a targeted scraper to ingest Tier-1 global undergraduate programs, open-source fellowships, and tech internships. 

### Step 2: The Stateful Backend
* **Goal:** Give the engine a memory.
* **Action:** Update FastAPI to support basic User Sessions (UUIDs). Create endpoints to log "Likes" and "Dislikes" for specific opportunity cards.

### Step 3: The Discovery UI
* **Goal:** Remove the search bar. 
* **Action:** Redesign the Next.js frontend into a "Card Stack" feed. The user reads a card, swipes right (save) or left (skip), triggering the backend to fetch the next best match based on that interaction.

### Step 4: The ML Recommendation Upgrade
* **Goal:** Learn from behavior, not just text.
* **Action:** Implement a dynamic user-vector that recalculates its coordinates based on the vectors of the items the user "Likes".