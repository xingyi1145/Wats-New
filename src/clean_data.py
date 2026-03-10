"""
Data Cleaning & Entity Resolution

Deduplicates and sanitizes opportunity JSON files before vectorization.
Uses URL normalization and title normalization to identify duplicates.
"""

import json
import os
import re
from urllib.parse import urlparse, urlunparse

import numpy as np
from sentence_transformers import SentenceTransformer, util


# ============================================================================
# Path setup
# ============================================================================

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
while os.path.basename(project_root) in ['src', 'scrapers', 'tests']:
    project_root = os.path.dirname(project_root)
data_dir = os.path.join(project_root, "data")

# ============================================================================
# Model loading (once)
# ============================================================================

print("Loading sentence-transformers model...")
MODEL = SentenceTransformer("all-MiniLM-L6-v2")
SEMANTIC_THRESHOLD = 0.78

DOMAIN_BLACKLIST = [
    "tiktok.com",
    "youtube.com",
    "facebook.com",
    "instagram.com",
    "coursejoiner.com",
    "makeoverarena.com"
]


# ============================================================================
# Normalization helpers
# ============================================================================

def normalize_url(url: str) -> str:
    """
    Normalize a URL for deduplication:
    - Force lowercase
    - Strip query parameters and fragments
    - Remove trailing slashes from the path
    """
    if not url:
        return ""
    parsed = urlparse(url.strip().lower())
    clean_path = parsed.path.rstrip("/")
    normalized = urlunparse((
        parsed.scheme,
        parsed.netloc,
        clean_path,
        "",   # params
        "",   # query  (stripped)
        "",   # fragment (stripped)
    ))
    return normalized


def normalize_title(title: str) -> str:
    """
    Normalize a title for deduplication:
    - Lowercase
    - Strip all punctuation
    - Collapse extra whitespace
    """
    if not title:
        return ""
    title = title.lower()
    title = re.sub(r"[^\w\s]", "", title)   # remove punctuation
    title = re.sub(r"\s+", " ", title).strip()
    return title


# ============================================================================
# Cleaning engine
# ============================================================================

def clean_file(filepath: str) -> int:
    """
    Load a JSON array file, deduplicate by normalized URL and title,
    overwrite the file with the cleaned list, and return the number
    of duplicates removed.
    """
    print(f"\n{'='*60}")
    print(f"  Cleaning: {os.path.basename(filepath)}")
    print(f"{'='*60}")

    if not os.path.exists(filepath):
        print(f"  ⚠ File not found: {filepath}")
        return 0

    with open(filepath, "r", encoding="utf-8") as f:
        items = json.load(f)

    if not isinstance(items, list):
        print("  ⚠ File does not contain a JSON array. Skipping.")
        return 0

    original_count = len(items)
    print(f"  Loaded {original_count} items.")

    seen_urls: set[str] = set()
    seen_titles: set[str] = set()
    cleaned: list[dict] = []
    removed = 0

    for item in items:
        norm_url = normalize_url(item.get("link", ""))
        norm_title = normalize_title(item.get("title", ""))

        # Check domain blacklist
        if norm_url and any(domain in norm_url for domain in DOMAIN_BLACKLIST):
            print(f"  ✗ Spam domain removed: {norm_url}")
            removed += 1
            continue

        # Check for duplicate URL (skip empty URLs)
        if norm_url and norm_url in seen_urls:
            print(f"  ✗ Duplicate URL removed: {item.get('title', '?')[:60]}")
            removed += 1
            continue

        # Check for duplicate title (skip empty titles)
        if norm_title and norm_title in seen_titles:
            print(f"  ✗ Duplicate title removed: {item.get('title', '?')[:60]}")
            removed += 1
            continue

        # Mark as seen
        if norm_url:
            seen_urls.add(norm_url)
        if norm_title:
            seen_titles.add(norm_title)

        cleaned.append(item)

    exact_removed = removed
    print(f"  Pass 1 (exact match): removed {exact_removed} duplicates, {len(cleaned)} remain.")

    # ------------------------------------------------------------------
    # Pass 2: Semantic deduplication via cosine similarity
    # ------------------------------------------------------------------
    if len(cleaned) > 1:
        print("  Running semantic deduplication...")

        comparison_texts = [
            (item.get("title", "") + " " + item.get("snippet", "")).strip()
            for item in cleaned
        ]

        embeddings = MODEL.encode(comparison_texts, convert_to_tensor=True,
                                  show_progress_bar=False)
        sim_matrix = util.cos_sim(embeddings, embeddings).cpu().numpy()

        # Flag indices to drop (keep earlier item, drop later one)
        semantic_dupes: set[int] = set()
        for i in range(len(cleaned)):
            if i in semantic_dupes:
                continue
            for j in range(i + 1, len(cleaned)):
                if j in semantic_dupes:
                    continue
                if sim_matrix[i][j] > SEMANTIC_THRESHOLD:
                    print(
                        f"  ✗ Semantic duplicate (sim={sim_matrix[i][j]:.3f}): "
                        f"\"{cleaned[j].get('title', '?')[:50]}\" "
                        f"≈ \"{cleaned[i].get('title', '?')[:50]}\""
                    )
                    semantic_dupes.add(j)

        semantic_removed = len(semantic_dupes)
        if semantic_dupes:
            cleaned = [item for idx, item in enumerate(cleaned)
                       if idx not in semantic_dupes]
        print(f"  Pass 2 (semantic): removed {semantic_removed} duplicates, {len(cleaned)} remain.")
        removed += semantic_removed

    # Overwrite the original file
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=2, ensure_ascii=False)

    print(f"  ✓ Kept {len(cleaned)} / {original_count} items ({removed} total duplicates removed).")
    return removed


# ============================================================================
# Entry point
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  Data Cleaning & Entity Resolution")
    print("=" * 60)

    files_to_clean = [
        os.path.join(data_dir, "global_opportunities.json"),
        os.path.join(data_dir, "spider_opportunities.json"),
        os.path.join(data_dir, "live_opportunities.json"), # Add this line!
    ]

    total_removed = 0
    for filepath in files_to_clean:
        total_removed += clean_file(filepath)

    print(f"\n{'='*60}")
    print(f"  CLEANING COMPLETE: {total_removed} total duplicates removed.")
    print(f"{'='*60}")
