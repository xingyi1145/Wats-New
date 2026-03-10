"""
Daily Pipeline – High Velocity Data

Runs scrapers for fast-expiring data (events, news, global opportunities),
then cleans and vectorizes the results.

Schedule: once per day via cron or task scheduler.
"""

import logging
import os
import subprocess
import sys
import time

# ============================================================================
# Logging setup
# ============================================================================

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
while os.path.basename(project_root) in ['src', 'scrapers', 'tests']:
    project_root = os.path.dirname(project_root)
data_dir = os.path.join(project_root, "data")
os.makedirs(data_dir, exist_ok=True)

log_file = os.path.join(data_dir, "pipeline.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger("pipeline_daily")

# ============================================================================
# Pipeline steps
# ============================================================================

PYTHON = sys.executable  # Use the same interpreter running this script

STEPS = [
    ("News Harvester",       os.path.join(current_dir, "scrapers", "news_harvester.py")),
    ("Wat2Do Scraper",       os.path.join(current_dir, "scrapers", "scrape_wat2do.py")),
    ("Agentic Spider",       os.path.join(current_dir, "scrapers", "agentic_spider.py")),
    ("Data Cleaner",         os.path.join(current_dir, "clean_data.py")),
    ("Vectorizer",           os.path.join(current_dir, "vectorize_live_data.py")),
]


def run_step(name: str, script_path: str) -> bool:
    """Run a single pipeline step. Returns True on success."""
    logger.info(f"▶ Starting: {name} ({os.path.basename(script_path)})")
    start = time.time()
    try:
        result = subprocess.run(
            [PYTHON, script_path],
            cwd=project_root,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout per step
        )
        elapsed = time.time() - start

        if result.returncode == 0:
            logger.info(f"✓ Completed: {name} in {elapsed:.1f}s")
        else:
            logger.warning(
                f"✗ Failed: {name} (exit code {result.returncode}) after {elapsed:.1f}s\n"
                f"  stderr: {result.stderr[:500]}"
            )
            return False

    except subprocess.TimeoutExpired:
        logger.warning(f"✗ Timeout: {name} exceeded 600s limit")
        return False
    except Exception as e:
        logger.warning(f"✗ Error running {name}: {e}")
        return False

    return True


# ============================================================================
# Entry point
# ============================================================================

def main():
    logger.info("=" * 60)
    logger.info("  DAILY PIPELINE – High Velocity Data")
    logger.info("=" * 60)

    total = len(STEPS)
    passed = 0
    failed = 0

    for name, script in STEPS:
        success = run_step(name, script)
        if success:
            passed += 1
        else:
            failed += 1

    logger.info("=" * 60)
    logger.info(f"  DAILY PIPELINE COMPLETE: {passed}/{total} succeeded, {failed} failed.")
    logger.info("=" * 60)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
