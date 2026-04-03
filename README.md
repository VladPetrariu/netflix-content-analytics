# Netflix Content Analytics

COSC 301 course project at UBCO, analyzing Netflix's catalog of movies and TV shows using Python, SQLite, and Tableau.

## Dataset

- **Source**: [Netflix Movies and TV Shows](https://www.kaggle.com/datasets/shivamb/netflix-shows) on Kaggle
- **License**: CC0 — Public Domain
- **Size**: ~6,200 titles with metadata (type, director, cast, country, date added, rating, duration, genre, description)

## Project Structure

```
netflix-content-analytics/
├── data/
│   ├── raw/                  # Original CSV from Kaggle (not modified)
│   ├── clean/                # Cleaned CSV after ETL
│   └── netflix.db            # SQLite database
├── scripts/
│   ├── etl_clean.py          # ETL: load, clean, and export
│   ├── load_sqlite.py        # Load cleaned data into SQLite
│   └── run_pipeline.sh       # One-command pipeline runner
├── notebooks/                # Jupyter notebooks for EDA
├── visuals/                  # Charts and dashboard exports
├── report/                   # Final report (PDF)
├── data_dictionary.md        # Column descriptions & transformations
├── requirements.txt          # Python dependencies
└── README.md
```

## Reproducing the Pipeline

### Prerequisites

- Python 3.10+
- [Kaggle CLI](https://github.com/Kaggle/kaggle-api) configured with API credentials (only needed if `data/raw/netflix_titles.csv` is not already present)

### Setup

```bash
git clone https://github.com/VladPetrariu/netflix-content-analytics.git
cd netflix-content-analytics

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run the full pipeline

```bash
bash scripts/run_pipeline.sh
```

This will:
1. **Download** the raw CSV from Kaggle (skipped if file exists)
2. **Clean** the data — handle missing values, parse dates, split duration, extract primary country/genre
3. **Load** the cleaned data into a SQLite database with indexes and run demo queries

### Run steps individually

```bash
# Clean raw data
python scripts/etl_clean.py

# Load into SQLite (with demo queries)
python scripts/load_sqlite.py
```

## Data Cleaning Decisions

| Issue | Decision | Justification |
|-------|----------|---------------|
| Missing director (1,969 rows) | Fill with "Unknown" | Too many to drop; director is useful metadata but not critical for most analyses |
| Missing cast (570 rows) | Fill with "Unknown" | Same reasoning as director |
| Missing country (476 rows) | Fill with "Unknown" | Preserves rows for non-geographic analyses |
| Missing date_added (11 rows) | Drop | Cannot analyze addition trends without this field |
| Missing rating (10 rows) | Drop | Cannot classify content without rating |
| Duplicate rows | Remove | None found, but checked defensively |
| date_added format | Parse "Month Day, Year" → ISO datetime | Enables time-series analysis |
| duration | Split into value (int) + unit (text) | Allows numeric comparisons for movies (minutes) and shows (seasons) separately |

See [`data_dictionary.md`](data_dictionary.md) for full column reference.

## SQLite Queries

Once the database is built, you can query it directly:

```bash
sqlite3 data/netflix.db
```

```sql
-- Titles added per year
SELECT year_added, COUNT(*) FROM titles GROUP BY year_added ORDER BY year_added;

-- Top genres
SELECT primary_genre, COUNT(*) as n FROM titles GROUP BY primary_genre ORDER BY n DESC LIMIT 10;

-- Average movie length by rating
SELECT rating, ROUND(AVG(duration_value),1) as avg_min
FROM titles WHERE type='Movie'
GROUP BY rating ORDER BY avg_min DESC;
```

## Use of Generative AI

This project used **Claude** (Anthropic) via **Claude Code** (CLI tool) to assist with:

- Writing the ETL cleaning script (`scripts/etl_clean.py`)
- Writing the SQLite loading script (`scripts/load_sqlite.py`)
- Writing the pipeline runner (`scripts/run_pipeline.sh`)
- Drafting the data dictionary and this README

All AI-generated content was reviewed, tested, and validated by the project authors. Students remain fully accountable for the submitted work, per the COSC 301 syllabus policy on generative AI use.
