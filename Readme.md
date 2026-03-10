# Wats-New (UW Nexus)

An AI-powered recommendation engine and semantic search platform initially designed for University of Waterloo students. Wats-New breaks the information bubble, connecting students with relevant cross-disciplinary opportunities, including student clubs, open-source fellowships, global hackathons, and undergraduate research (URAs), based purely on natural language interests.

## Features

- **Semantic Match Engine**: Uses `sentence-transformers` (`all-MiniLM-L6-v2`) to map the context of student interests ("vibes") mathematically against thousands of opportunities.
- **Discovery UX**: A card-stack Next.js web application that feeds opportunities iteratively, instead of relying on a standard search bar.
- **Live Opportunity "Snipers"**: Distinct scraping pipelines (`sniper_ura`, `sniper_rss`, `sniper_devpost`) that execute independently to securely scrape diverse data schemas into isolated targets.
- **Machine Learning Telemetry**: The UI silently logs implicit user vectors for $[novelty, utility]$ directly to `telemetry.jsonl` through a Deferred State cycle, securely routing for offline ML model training.
- **REST API**: A fast, asynchronous backend powered by FastAPI orchestrating real-time SQLite interaction states.

## Tech Stack

- **Backend**: Python 3.12+, FastAPI, Uvicorn, SQLite
- **AI/ML**: `sentence-transformers`, PyTorch, NumPy, DuckDuckGo Search
- **Data Harvesting Pipelines**: BeautifulSoup4, Feedparser, Cron
- **Frontend**: Node.js 20+, Next.js (App Router), React, Tailwind CSS

## Prerequisites

- Python 3.12 or higher
- Node.js 20.9.0+ (using `nvm` to manage Node versions)

## Installation & Setup

### 1. Database & Inference Setup

Navigate to the project root and set up the Python virtual environment:

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Data Pipeline

Before running the API, you must provision the data files and render the vector embeddings for the local search engine:

```bash
# Vectorize static foundational data
python src/generate_embeddings.py

# Run the complete orchestrated daily pipeline (Snipers -> Database Compiler -> Vectorizer)
python src/pipeline_daily.py
```

*Note: Data files like `telemetry.jsonl` and mapped sqlite `.db` states are kept isolated inside the `/data` directory automatically.*

### 3. Start the Backend API

Start the FastAPI server (Supports Vercel cloud integrations locally via ENV ports):

```bash
python src/api.py
```

The API will be available at `http://0.0.0.0:8000`. You can view interactive endpoints at `/docs`.

### 4. Frontend Setup

Open a new terminal, ensure you are using Node.js 20+, and start the Next.js development server:

```bash
# Switch to Node 20
nvm use 20

# Navigate to the frontend directory
cd frontend

# Install dependencies and Boot Server
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`.

## Project Structure

- `src/`: Backend logic, AI routing, and API core.
  - `api.py`: FastAPI server handling recommendations and telemetry.
  - `pipeline_daily.py`: Aggregation script executing scheduled data fetching.
  - `compile_database.py`: Deduplicates snipers and organizes the master matrix.
  - `clean_data.py` & `vectorize_live_data.py`: AI/ML processing queues.
  - `scrapers/`: Isolated targeted "Sniper" scripts (URA, RSS, Devpost).
- `frontend/`: Standalone Next.js 14+ UI with Tailwind CSS.
- `doc/`: Strategic architectural charters and historical phases.
- `data/`: Dynamic local data layer containing SQlite databases, `.jsonl` telemetry logs, and NumPy vectors.

## License

MIT
