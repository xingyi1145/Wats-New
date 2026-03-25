# Project Charter: Autonomous Information Foraging System (Wats-New v2.0)

## 1. Executive Summary
The current Wats-New pipeline relies on passive, deterministic data collection (e.g., RSS feeds, specific scraper scripts). This approach suffers from high latency (discovering opportunities only after they are widely publicized) and low adaptability. This project proposes an active, multi-agent Information Foraging Swarm. By shifting to a probabilistic model, the system will autonomously hypothesize, search, extract, and ruthlessly filter high-value, niche opportunities across the web.

## 2. Problem Statement
Passive scraping yields low-signal, high-noise data. To provide true value, the system must act as an intelligent researcher that can:
1. Deduce what to search for based on temporal context and specific student personas.
2. Navigate the web efficiently without prohibitive compute/API costs.
3. Filter out generic, expired, or irrelevant garbage before it reaches the vector database.
4. Learn from its successes and failures to optimize future searches.

## 3. System Architecture: The 4-Agent Swarm

### Agent 1: The Strategist (Query Generator)
* **Role:** Generates hyper-specific, context-aware search queries.
* **Mechanism:** An LLM prompted with the current date, academic calendar, and distinct student profiles. 
* **Hardening (The Fix):** Instead of generic "student" prompts, it is injected with strict technical constraints. For example, it will generate queries specifically hunting for "software engineering summer 2026," "undergraduate research machine learning," or "neural network visualization projects" while explicitly appending operators to bypass standard job boards (e.g., `site:notion.site OR site:github.com "internship"`).

### Agent 2: The Explorer (Hybrid Web Navigator)
* **Role:** Executes queries and extracts raw text.
* **Mechanism:** A cost-optimized, two-tier navigation system.
    * **Tier 1 (Breadth):** Uses a SERP API (e.g., Tavily or Exa) to execute The Strategist's queries. It evaluates the resulting metadata snippets for an initial "Information Scent Score."
    * **Tier 2 (Depth):** Only if a link scores above a high scent threshold does the system deploy a headless browser (Playwright) driven by a Vision-Language Model to navigate complex DOMs, click "Apply", and extract the buried text.
* **Hardening (The Fix):** This hybrid approach prevents the VLM from getting trapped in infinite scrolls or burning tokens on low-value pages.

### Agent 3: The Ruthless Evaluator (Anti-Garbage Filter)
* **Role:** Acts as the gatekeeper to the vector database.
* **Mechanism:** A two-pass evaluation pipeline.
    * **Pass 1 (Binary Filters):** Hard algorithmic checks. Is the deadline passed? Does it explicitly require U.S. Citizenship? Is it restricted to SWPP-eligible applicants? If yes, immediately discard.
    * **Pass 2 (Cynical Rubric):** An LLM prompted to act as a highly critical, ambitious undergraduate. It scores the extracted text from 1-10 on actual utility, penalizing generic PR speak, pay-to-play events, and low-quality spam.
* **Hardening (The Fix):** Separating objective constraints (Pass 1) from subjective scoring (Pass 2) ensures zero hallucinations regarding strict eligibility requirements.

### Agent 4: The Memory Engine (Domain Reputation)
* **Role:** Optimizes the system's foraging efficiency over time.
* **Mechanism:** A Multi-Armed Bandit algorithm tracking domain yield.
* **Hardening (The Fix):** Instead of a heavy Knowledge Graph, this is a lightweight JSON weight table. If The Evaluator scores a `github.io` blog post highly, the domain's weight increases. If it rejects five `eventbrite.com` links in a row, the weight drops. This table is fed back to The Strategist daily to inform search operators (e.g., `-site:eventbrite.com`).

## 4. Implementation Phases

* **Phase 1: The Gatekeeper (Evaluator).** Build the two-pass filter first. Feed it manual, raw text to ensure it correctly identifies garbage and accurately flags strict constraints (like citizenship or funding eligibility).
* **Phase 2: The Scout (Strategist + SERP).** Implement the context-aware query generation and the Tier 1 SERP API extraction. Connect this directly to the Evaluator.
* **Phase 3: The Deep Diver (VLM Explorer).** Implement Playwright/VLM for the edge cases where high-scent opportunities are hidden behind complex UI interactions.
* **Phase 4: The Loop (Memory Engine).** Implement the JSON weight table to close the feedback loop between the Evaluator and the Strategist.

## 5. Success Metrics
1.  **Precision (Quality):** >85% of items hitting the vector database are rated "highly relevant" by end-users.
2.  **Cost Efficiency:** Foraging compute costs remain under $2.00 per 100 high-quality opportunities discovered.
3.  **Novelty:** >50% of discovered opportunities are not easily found on the first page of a standard Google search for the same topic.