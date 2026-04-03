#!/usr/bin/env bash
# End-to-end pipeline: download → clean → load into SQLite
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Netflix Content Analytics Pipeline ==="
echo ""

# Step 1 — Download raw data (if not already present)
RAW_CSV="$ROOT/data/raw/netflix_titles.csv"
if [ ! -f "$RAW_CSV" ]; then
    echo "[1/3] Downloading dataset from Kaggle..."
    mkdir -p "$ROOT/data/raw"
    kaggle datasets download -d shivamb/netflix-shows -p "$ROOT/data/raw" --unzip
else
    echo "[1/3] Raw data already present — skipping download."
fi

# Step 2 — ETL & Cleaning
echo "[2/3] Running ETL & cleaning..."
python "$ROOT/scripts/etl_clean.py"

# Step 3 — Load into SQLite
echo "[3/3] Loading into SQLite..."
python "$ROOT/scripts/load_sqlite.py"

echo ""
echo "=== Pipeline complete ==="
echo "  Raw data:    $ROOT/data/raw/netflix_titles.csv"
echo "  Clean data:  $ROOT/data/clean/netflix_titles_clean.csv"
echo "  Database:    $ROOT/data/netflix.db"
