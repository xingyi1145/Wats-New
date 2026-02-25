# Wats-New

An AI-powered recommendation engine and semantic search platform designed for University of Waterloo students. Wats-New connects students with relevant extracurricular opportunities, including student clubs, hackathons, undergraduate research, and guest lectures, based on natural language queries.

## Features

- **Semantic Search**: Uses `sentence-transformers` (`all-MiniLM-L6-v2`) to understand the context of student interests rather than relying on exact keyword matches.
- **Live Opportunity Harvesting**: Automatically fetches recent, relevant events and opportunities from the web using DuckDuckGo search.
- **Unified Vector Database**: Combines static club data and live event data into a single, queryable vector space.
- **REST API**: A fast, asynchronous backend built with FastAPI.
- **Modern Frontend**: A responsive user interface built with Next.js 16, React, and Tailwind CSS.

## Tech Stack

- **Backend**: Python 3.12+, FastAPI, Uvicorn, Pydantic
- **AI/ML**: `sentence-transformers`, PyTorch, NumPy
- **Data Harvesting**: `duckduckgo-search`
- **Frontend**: Node.js 20+, Next.js (App Router), React, Tailwind CSS

## Prerequisites

- Python 3.12 or higher
- Node.js 20.9.0 or higher (use `nvm` to manage Node versions)

## Installation & Setup

### 1. Backend Setup

Navigate to the project root and set up the Python virtual environment:

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Data Pipeline

Before running the API, you need to generate the vector embeddings for the search engine:

```bash
# 1. Vectorize static club data
python src/generate_embeddings.py

# 2. Harvest live opportunities from the web
python src/news_harvester.py

# 3. Vectorize the newly harvested live data
python src/vectorize_live_data.py
```

### 3. Start the Backend API

Start the FastAPI server:

```bash
cd src
python api.py
```

The API will be available at `http://localhost:8000`. You can view the interactive API documentation at `http://localhost:8000/docs`.

### 4. Frontend Setup

Open a new terminal, ensure you are using Node.js 20+, and start the Next.js development server:

```bash
# Switch to Node 20 (if using nvm)
nvm use 20

# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:3000`.

## Project Structure

- `src/`: Backend source code, API, and data processing scripts.
  - `api.py`: FastAPI application entry point.
  - `generate_embeddings.py`: Script to vectorize static club data.
  - `news_harvester.py`: Script to scrape live events and opportunities.
  - `vectorize_live_data.py`: Script to vectorize live event data.
  - `tests/test_search.py`: CLI tool to test the semantic search engine.
- `frontend/`: Next.js frontend application.
- `doc/`: Project documentation and charters.
- `*.json`: Local data storage for raw and vectorized data.

## License

MIT
