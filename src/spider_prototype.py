"""
Agentic Web Spider - LLM Extraction Prototype

Fetches a public tech opportunities page, extracts visible text,
and uses Gemini to produce structured JSON opportunity data.
"""

import json
import os
import re
import time

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors

# ============================================================================
# Configuration
# ============================================================================

TARGET_URL = (
    "https://raw.githubusercontent.com/pittcsc/Summer2025-Internships/dev/README.md"
)
OUTPUT_FILE = "spider_test.json"

# ============================================================================
# Step 1: Fetch and extract visible text
# ============================================================================

def fetch_page_text(url: str) -> str:
    """
    Download a URL and return only the visible text content.
    Strips all HTML tags, scripts, styles, and excessive whitespace.
    """
    print(f"Fetching: {url}")
    response = requests.get(url, timeout=30, headers={
        "User-Agent": "Mozilla/5.0 (compatible; WatsNew-Spider/1.0)"
    })
    response.raise_for_status()

    content_type = response.headers.get("Content-Type", "")

    # If the content is already plain text / markdown, use it directly
    if "text/plain" in content_type or url.endswith(".md"):
        text = response.text
    else:
        # Parse HTML and extract visible text
        soup = BeautifulSoup(response.text, "html.parser")

        # Remove non-visible elements
        for tag in soup(["script", "style", "noscript", "meta", "link", "head"]):
            tag.decompose()

        text = soup.get_text(separator="\n")

    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text).strip()

    print(f"Extracted {len(text)} characters of visible text.")
    return text


# ============================================================================
# Step 2: LLM extraction via Gemini
# ============================================================================

SYSTEM_PROMPT = """\
You are a structured-data extraction agent for a university opportunity engine.

INPUT: Raw text scraped from a webpage listing tech internships or programs.

TASK: Extract every distinct opportunity you can find and return a JSON array.

OUTPUT FORMAT (strict – no markdown fences, no commentary, ONLY the JSON array):
[
  {
    "title": "<company or program name and role>",
    "link": "<application URL if present, otherwise empty string>",
    "snippet": "<Exactly two sentences summarizing the opportunity, including location and any deadline info.>",
    "source": "spider_agent"
  }
]

RULES:
1. Output MUST be a valid JSON array and nothing else.
2. Do NOT wrap the output in markdown code fences or add any text before/after.
3. Every object MUST have exactly the four keys: title, link, snippet, source.
4. "source" is always the literal string "spider_agent".
5. If no opportunities are found, return an empty array: []
6. Limit output to the top 20 most distinct, well-described opportunities.
7. De-duplicate: if the same company+role appears multiple times, keep only one.
"""


def extract_opportunities_with_llm(page_text: str) -> list[dict]:
    """
    Send extracted text to Gemini and parse the structured JSON response.
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY not found. Add it to your .env file."
        )

    # Strip whitespace from the key in case .env has spaces around '='
    api_key = api_key.strip()

    client = genai.Client(api_key=api_key)

    # Truncate input if extremely long (Gemini context window safety)
    max_chars = 80_000
    if len(page_text) > max_chars:
        page_text = page_text[:max_chars]
        print(f"  (Truncated input to {max_chars} characters)")

    print("Sending text to Gemini for structured extraction...")

    # Retry with exponential backoff for rate limits
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f"{SYSTEM_PROMPT}\n\n--- BEGIN SCRAPED TEXT ---\n{page_text}\n--- END SCRAPED TEXT ---",
            )
            break  # Success
        except genai_errors.ClientError as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                wait = 10 * attempt
                print(f"  Rate limited (attempt {attempt}/{max_retries}). Retrying in {wait}s...")
                time.sleep(wait)
                if attempt == max_retries:
                    print("Error: Gemini API quota exhausted after all retries.")
                    print("Check your plan at https://ai.google.dev/gemini-api/docs/rate-limits")
                    return []
            else:
                raise

    raw_output = response.text.strip()

    # Clean potential markdown fences the LLM may produce despite instructions
    if raw_output.startswith("```"):
        # Remove opening fence (```json or ```)
        raw_output = re.sub(r"^```(?:json)?\s*\n?", "", raw_output)
        # Remove closing fence
        raw_output = re.sub(r"\n?```\s*$", "", raw_output)

    # Parse JSON
    try:
        opportunities = json.loads(raw_output)
    except json.JSONDecodeError as e:
        print(f"Error: LLM output was not valid JSON: {e}")
        print(f"Raw output (first 500 chars):\n{raw_output[:500]}")
        return []

    if not isinstance(opportunities, list):
        print("Error: LLM output was not a JSON array.")
        return []

    # Validate and sanitize each entry
    valid = []
    for item in opportunities:
        if not isinstance(item, dict):
            continue
        valid.append({
            "title": str(item.get("title", "")).strip(),
            "link": str(item.get("link", "")).strip(),
            "snippet": str(item.get("snippet", "")).strip(),
            "source": "spider_agent",
        })

    print(f"LLM returned {len(valid)} structured opportunities.")
    return valid


# ============================================================================
# Step 3: Main entrypoint
# ============================================================================

def main():
    print("=" * 60)
    print("  Agentic Web Spider - LLM Extraction Prototype")
    print("=" * 60)

    # Fetch
    text = fetch_page_text(TARGET_URL)

    # Extract
    opportunities = extract_opportunities_with_llm(text)

    if not opportunities:
        print("\nNo opportunities extracted. Exiting.")
        return

    # Print to terminal
    print("\n" + "=" * 60)
    print(f"  RESULTS: {len(opportunities)} opportunities extracted")
    print("=" * 60)
    print(json.dumps(opportunities, indent=2, ensure_ascii=False))

    # Save to file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(opportunities, f, indent=2, ensure_ascii=False)

    print(f"\nSaved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
