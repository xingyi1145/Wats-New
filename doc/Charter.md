# Project Charter: UW Nexus (Wat's New)

| Project Name | **UW Nexus** (Working Title: Wat's New) |
| :--- | :--- |
| **Project Manager** | Yi Xing |
| **Start Date** | Feb 2026 |
| **Target MVP** | April 2026 |
| **Status** | In Progress (Phase 1 Complete) |

---

### 1. Problem Statement
**The "Why":** UWaterloo students currently face two information problems:
1.  **Fragmentation:** Opportunities (research, hackathons, clubs) are scattered across 5+ disconnected platforms (WaterlooWorks, WUSA, Portal, Reddit).
2.  **The Filter Bubble:** Students only see opportunities directly related to their declared major. A CS student rarely sees a Fine Arts digital media project, and an International student often wastes time applying to "Citizens Only" grants.

### 2. Project Goal
**The "What":** Build a web-based "Opportunity Engine" that aggregates scattered campus data and uses semantic search (AI) to recommend relevant, cross-disciplinary opportunities based on a user’s profile and natural language interests.

### 3. Objectives & Success Metrics (SMART)
* **[COMPLETED] Objective 1 (Base Data):** Successfully scrape the WUSA Clubs Directory and extract full descriptions (including "Show More" content). *Status: 199 Clubs Scraped & Cleaned.*
* **Objective 2 (Live Intel):** Implement a "News Harvester" pipeline that searches the web (DuckDuckGo) for fresh events (Hackathons, Guest Lectures) every 24 hours.
* **Objective 3 (Intelligence):** Implement a Vector Search algorithm (`sentence-transformers`) that connects user interests to opportunities semantically (e.g., "Music" input $\rightarrow$ "Audio Research" output).
* **Objective 4 (User Value):** Achieve a Click-Through Rate where users click on at least 1 recommended item *outside* their home faculty.

### 4. Scope Definition

| **In Scope (What we WILL do)** | **Out of Scope (What we will NOT do yet)** |
| :--- | :--- |
| **User Profile:** Basic inputs (Program, Year, Visa Status) + Open-ended "Interests" bio. | **Social Features:** Chatting, friends lists, or forums. |
| **Data Source A (Static):** WUSA Clubs Registry (JSON). | **Full Integration:** Real-time sync with WaterlooWorks (Requires official API). |
| **Data Source B (Dynamic):** "Live Harvester" using DuckDuckGo to find Hackathons/Events. | **User Accounts:** Complex authentication (Start with local storage or simple auth). |
| **The "Engine":** Semantic matching (Vector embeddings) via `sentence-transformers`. | **Mobile App:** Native iOS/Android app (Web app is prioritized). |
| **International Filter:** Toggle to hide "Citizens Only" requirements. | |

### 5. Technical Stack
* **Frontend:** React / Next.js (Responsive Web App).
* **Backend:** Python (FastAPI) – Handles the ML logic and Search API.
* **Database:** * *Static:* JSON files (for MVP simplicity).
    * *Vector:* `pgvector` or local FAISS index for similarity search.
* **Data Engineering:** * `Playwright` (Scraping Static Sites).
    * `duckduckgo-search` (Harvester for Live Events).
* **AI/ML:** `sentence-transformers/all-MiniLM-L6-v2` (Embeddings).

### 6. Key Risks & Mitigation
| Risk | Probability | Mitigation Strategy |
| :--- | :--- | :--- |
| **Scrapers Break** | High | Modularize scrapers. If WUSA changes, only `scrape_clubs.py` needs fixing. Use the "Live Harvester" as a backup data source. |
| **"Garbage" Search Results** | Medium | The Live Harvester might fetch spam. **Fix:** Implement an LLM filtering step (Gemini/GPT) to "grade" search results before saving them. |
| **Cold Start** | Medium | New users have no data. **Fix:** "Onboarding Tags" (force user to pick 3 interests at signup). |

### 7. Timeline
* **Phase 1 (Data Layer):** [DONE]
    * Scrape WUSA Clubs.
    * Clean "Show More" text data.
* **Phase 2 (The Brain):** [CURRENT FOCUS]
    * Build `generate_embeddings.py` to vectorize club data.
    * Build `harvest_news.py` for live web search.
* **Phase 3 (The API):**
    * Create FastAPI endpoints to serve recommendations.
* **Phase 4 (The UI):**
    * Build React Frontend.

---
*Last Updated: Feb 15, 2026*