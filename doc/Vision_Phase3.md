# Wats-New: Development Roadmap

## Phase 1: Deployment & The "Cold Start" Solution
*Status: Immediate Next Steps*

We have successfully engineered a fully autonomous, self-cleaning data pipeline and a semantic vector recommendation engine. Before adding complex features, we must deploy the MVP to real users to solve the Machine Learning "Cold Start Problem."

### 1. Cloud Infrastructure Setup
* **Frontend (Next.js):** Deploy to **Vercel** for free, zero-config hosting.
* **Backend API (FastAPI):** Deploy the python recommendation engine to a service like **Render**, **Railway**, or **Heroku**.
* **Vector Database:** Currently using local JSON/Numpy. For cloud deployment, migrate `ALL_EMBEDDINGS` to a free-tier vector database like **Pinecone** or **Supabase (pgvector)** so the backend doesn't run out of memory.

### 2. Pipeline Automation (Cron Jobs)
* **The Problem:** Our orchestrators (`pipeline_daily.py` and `pipeline_monthly.py`) are currently run manually on a local machine.
* **The Solution:** Spin up a cheap $5/month Linux VPS (DigitalOcean/Linode) or use GitHub Actions.
* **Action:** Schedule cron jobs so the daily pipeline runs automatically at 3:00 AM EST, ensuring the frontend always serves fresh UWaterloo events and global hackathons.

### 3. Data Collection (Beta Launch)
* Deploy the link to a cohort of 50 UWaterloo students.
* Add a silent analytics tracker (like PostHog) to monitor exactly which "Vibes" students type in, and which cards they click. This initial user behavior data is mathematically required for Phase 2.

---

## Phase 2: The Intelligent Engine 
*Status: Future Scaling (Post-Launch)*

Once we have a baseline of real user data, we transition from a pure semantic search engine to a true Machine Learning Recommendation App.

### Feature A: The ML Recommender (RLHF)
* **Goal:** Move beyond "text similarity" to predict "usefulness."
* **Execution:** Add binary rating buttons to the UI cards (e.g., 🔥 "Useful" / ♻️ "Already Knew This" / 👎 "Irrelevant"). 
* **The Math:** Train a lightweight classifier (like XGBoost or a small neural net) on this feedback data to rerank the vector similarity scores before they are sent to the frontend.

### Feature B: User Authentication & Context Injection
* **Goal:** Provide hyper-personalized recommendations without requiring users to type a massive prompt every time.
* **Execution:** * Integrate standard OAuth (Google/GitHub login).
    * Build a profile onboarding flow where users can upload a PDF Resume or a `user.md` file.
    * **Architecture:** Vectorize the user's resume. When they log in, automatically merge their "Resume Vector" with their live "Search Vector" so the engine inherently knows their skills without them asking.

### Feature C: Hybrid Search Interface
* **Goal:** Accommodate both exploratory discovery and exact retrieval.
* **Execution:** Update the UI to feature a toggle.
    * *Mode 1 (Discovery):* The current "Vibe" text window for open-ended serendipity based on user profiles.
    * *Mode 2 (Search):* A traditional, Instagram-style strict search bar for when a user specifically wants to look up "Baja SAE" or "Google Summer of Code" without the AI trying to be clever.