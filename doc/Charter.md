Project Charter: The UW Opportunity Engine
Project Name: Wat's New (Working Title)
Project Manager: Yi Xing
Start Date: Feb 2026
Target Completion (MVP): April 2026 (End of Term)
1. Problem Statement
The "Why": UWaterloo students currently face two information problems:
Fragmentation: Opportunities (research, hackathons, clubs) are scattered across 5+ disconnected platforms (WaterlooWorks, WUSA, Department sites, Discord, Reddit).
The Filter Bubble: Students only see opportunities directly related to their declared major. A CS student rarely sees a Fine Arts digital media project, and an International student often wastes time applying to "Citizens Only" grants.
2. Project Goal
The "What": Build a web-based "Opportunity Engine" that aggregates scattered campus data and uses semantic search (AI) to recommend relevant, cross-disciplinary opportunities based on a user’s profile and natural language interests.
3. Objectives & Success Metrics (SMART)
Objective 1 (Aggregation): Successfully build automated scrapers for 2 primary data sources (e.g., WUSA Clubs & UW Events Calendar) by [Date].
Objective 2 (Intelligence): Implement a Vector Search algorithm that creates valid recommendations connecting two seemingly unrelated keywords (e.g., "Music" input $\rightarrow$ "Audio Processing Research" output).
Objective 3 (User Value): Achieve a "Click-Through Rate" where users click on at least 1 recommended item that is outside their home faculty.
4. Scope Definition (The Guardrails)
This is the most critical section. As your sparring partner, I have aggressively cut features to ensure you actually finish.
In Scope (What we WILL do)
Out of Scope (What we will NOT do yet)
User Profile: Basic inputs (Program, Year, Visa Status) + Open-ended "Interests" text box.
Social Features: Chatting with other users, forums, or "friending" people.
Data Sources: Scraping WUSA Clubs list and one Faculty research page.
Full Integration: Real-time sync with WaterlooWorks (impossible without official API access).
The "Engine": Semantic matching (Vector embeddings) to find related topics.
Complex Admin: A portal for club leaders to manually upload events (solves the wrong problem).
International Filter: A toggle to hide "Citizens Only" requirements.
Mobile App: Native iOS/Android app (Web app is sufficient and faster to build).

5. Technical Stack
Frontend: React / Next.js (Responsive Web App).
Backend: Python (FastAPI or Flask) – Best for handling the ML logic.
Database: PostgreSQL (with pgvector extension) or Pinecone – To store vector embeddings.
Scraping: BeautifulSoup / Selenium.
6. Key Risks & Mitigation Strategy
Risk: Scrapers break frequently. If UWaterloo changes their website layout, your app breaks.
Mitigation: Build the scrapers as modular "plugins" so fixing one doesn't break the whole app. Cache data so the app works even if the scraper fails for a day.
Risk: The "Cold Start" problem. New users have no data to base recommendations on.
Mitigation: Use "Onboarding Tags." Force the user to pick 3 tags (e.g., "AI", "Music", "Finance") during sign-up to seed the algorithm immediately.
7. Timeline (Tentative)
Phase 1 (Weeks 1-2): Infrastructure. Set up the repo, build the basic Scraper for WUSA.
Phase 2 (Weeks 3-4): The Brain. Implement the Vector Search (embedding user text and matching it to club text).
Phase 3 (Weeks 5-6): The Face. Build the React Frontend and connect it to the backend.
Phase 4 (Week 7): Testing. Give it to 5 friends. Fix bugs.

Intellectual Critique (Sparring Mode)
Now, look at this charter. As your sparring partner, I see one major assumption you need to test immediately:
The Assumption: You assume students want to break their bubble.
The Counterpoint: Most students are stressed and time-poor. They might just want the easiest path to a resume boost (confirmation bias).
The Adjustment: Your UI cannot just be "Here are random cool things." It must pitch the value of the bubble-breaking recommendation.
Bad UI: "You might like the Knitting Club."
Good UI: "You like Coding. Joining the Knitting Club could help you build a project around Textile Patterns & Algorithms (unique portfolio piece)."