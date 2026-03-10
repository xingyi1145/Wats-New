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

### Step 1: The Global Harvester [COMPLETE]
* **Goal:** Expand the vector database beyond UWaterloo.
* **Action:** Built targeted snipers (`src/scrapers/` to ingest structured global undergraduate programs, RSS feeds, Devpost Hackathons, and URA opportunities. Organized via `compile_database.py`.

### Step 2: The Stateful Backend [COMPLETE]
* **Goal:** Give the engine a memory.
* **Action:** Updated FastAPI to support basic User Sessions (UUIDs). Created endpoints and SQLite databases to securely log explicit "Likes" and "Skips" for specific opportunity cards.

### Step 3: The Discovery UI [COMPLETE]
* **Goal:** Remove the search bar. 
* **Action:** Redesigned the Next.js frontend into a "Card Stack" feed applying deferred UI state limits. The user interacts through specific explicit buttons to trigger background recommendation fetch loops.

### Step 4: ML Telemetry Integration [COMPLETE]
* **Goal:** Learn from behavior, not just text. Track both Utility (useful/saved) and Novelty (discovered/ignoring what they already know).
* **Action:** Implemented a background continuous telemetry endpoint (`/api/telemetry`) to capture `[novelty, utility]` binary vectors implicitly based on interaction delays and state tracking, appending straight to `data/telemetry.jsonl`. Appended manual "Flag" loops (`/api/flag`) to clean databases via user-reporting. 

### Step 5: Architecture Scaling [COMPLETE]
* **Goal:** Prep for seamless public web deployment.
* **Action:** Reorganized data layers locally out to `/data` while migrating scripts to `/scrapers`. Refactored Fastapi routing via `0.0.0.0`, Environment variables handling on the frontend `process.env.NEXT_PUBLIC_API_URL`, dynamic pathing, and prepped the platform for continuous Vercel and Cloud VM deployments. 
