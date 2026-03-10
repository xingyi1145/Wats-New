# Project Charter: UW Nexus (Wat's New)

| Project Name | **UW Nexus** (Working Title: Wat's New) |
| :--- | :--- |
| **Project Manager** | Yi Xing |
| **Start Date** | Feb 2026 |
| **Target MVP** | April 2026 |
| **Status** | Phase 2 Complete (Deployed Beta) |

---

### 1. Problem Statement
**The "Why":** UWaterloo students currently face two information problems:
1.  **Fragmentation:** Opportunities (research, hackathons, clubs) are scattered across 5+ disconnected platforms (WaterlooWorks, WUSA, Portal, Reddit).
2.  **The Filter Bubble:** Students only see opportunities directly related to their declared major. A CS student rarely sees a Fine Arts digital media project, and an International student often wastes time applying to "Citizens Only" grants.

### 2. Project Goal
**The "What":** Build a web-based "Opportunity Engine" that aggregates scattered campus data and uses semantic search (AI) to recommend relevant, cross-disciplinary opportunities based on a user’s profile and natural language interests. It has transitioned into a "Discovery Feed" to push opportunities directly to users and learn from their interactions.

### 3. Objectives & Success Metrics (SMART)
* **Objective 1 (Base Data):** Successfully scrape the WUSA Clubs Directory and extract full descriptions (including "Show More" content). *Status: Complete.*
* **Objective 2 (Live Intel):** Implement targeted "Snipers" (e.g., URA, RSS, Devpost, Wat2Do) that fetch structured specific fresh opportunities. *Status: Complete.*
* **Objective 3 (Intelligence):** Implement a Vector Search algorithm (`sentence-transformers`) that connects user interests to opportunities semantically. Introduce continuous telemetry gathering (utility/novelty metrics) to train personalized models. *Status: Complete.*
* **Objective 4 (User Value):** Achieve a Click-Through Rate where users click on at least 1 recommended item *outside* their home faculty. *Status: Monitoring.*

### 4. Scope Definition

| **In Scope (What we WILL do)** | **Out of Scope (What we will NOT do yet)** |
| :--- | :--- |
| **User Profile:** Basic inputs / text string + background ML tracked preferences. | **Social Features:** Chatting, friends lists, or forums. |
| **Data Source A (Static):** WUSA Clubs Registry (JSON). | **Full Integration:** Real-time sync with WaterlooWorks (Requires official API). |
| **Data Source B (Dynamic):** "Sniper" engines targeting URAs, Hubs, RSS feeds, and Hackathons. | **User Accounts:** Complex authentication (Currently utilizing local storage UUIDs). |
| **The "Engine":** Semantic matching (Vector embeddings) & Telemetry Logging (JSONL). | **Mobile App:** Native iOS/Android app (Web app is prioritized). |
| **Implicit Tracking:** Novelty vs Utility background logging for ranking. | |

### 5. Technical Stack
* **Frontend:** Next.js (App Router) & Tailwind CSS (Cloud-ready on Vercel).
* **Backend:** Python (FastAPI) – Handles ML logic, background tasks, and API serving.
* **Database:** 
    * *Local State:* SQLite for tracking explicit saves/skips per UUID.
    * *Vector Store:* JSON matrix files mapped via `numpy` locally.
    * *Telemetry:* Streaming `.jsonl` appends for analytics and future model training.
* **Data Engineering:** `duckduckgo-search`, `BeautifulSoup`, `feedparser` inside targeted `.py` scraper pipelines running on daily/monthly schedules.
* **AI/ML:** `sentence-transformers/all-MiniLM-L6-v2` (Embeddings).

### 6. Key Risks & Mitigation
| Risk | Probability | Mitigation Strategy |
| :--- | :--- | :--- |
| **Scrapers Break** | High | Modularize scrapers. Moved away from wide web harvesting to specific "Snipers" (RSS, Tables) with failsafes ensuring corrupted data doesn't wipe existing databases. |
| **"Garbage" Search Results** | Low | Hardened parsers utilizing whitelist/blacklist filtering (e.g., RSS scopes) to remove irrelevant items before vectorization. |
| **Cold Start** | Medium | Handled via "Vibe Analysis" text input that sets initial vector anchor points. |

### 7. Timeline
* **Phase 1 (Data Layer):** [DONE]
    * Scrape WUSA Clubs. Clean "Show More" text data.
* **Phase 2 (The Brain):** [DONE]
    * Build targeted scrapers (`src/scrapers/`).
    * Implement orchestrator pipelines (`pipeline_daily.py`).
* **Phase 3 (The API):** [DONE]
    * Create FastAPI endpoints serving recommendations, tracking profiles (SQLite).
    * Add Telemetry and Flagging endpoints.
* **Phase 4 (The UI & Cloud):** [DONE]
    * Build React/Next.js UI.
    * Path resolution scaling and folder restructure.
    * Deployable configuration to Vercel.
