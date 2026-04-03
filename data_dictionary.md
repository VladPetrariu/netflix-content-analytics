# Data Dictionary — Netflix Titles

## Source

- **Dataset**: Netflix Movies and TV Shows (Kaggle — shivamb/netflix-shows)
- **Raw file**: `data/raw/netflix_titles.csv` (6,234 rows)
- **Cleaned file**: `data/clean/netflix_titles_clean.csv` (6,214 rows after cleaning)
- **License**: CC0 — Public Domain

## Cleaning Summary

| Step | Action | Rows Affected |
|------|--------|---------------|
| Missing director/cast/country | Filled with "Unknown" | 1,969 / 570 / 476 |
| Missing date_added or rating | Dropped rows | 20 |
| Duplicate rows | Removed | 0 |
| date_added | Parsed from "Month Day, Year" to ISO datetime | All |
| duration | Split into `duration_value` (int) + `duration_unit` (text) | All |
| Whitespace | Stripped from all text columns | All |

## Column Reference (Cleaned Dataset)

| Column | Type | Description | Transformation |
|--------|------|-------------|----------------|
| `show_id` | TEXT | Unique identifier for each title | Cast from int to string (it is an ID, not a number) |
| `type` | TEXT | "Movie" or "TV Show" | None — original values preserved |
| `title` | TEXT | Title of the movie or show | Whitespace stripped |
| `director` | TEXT | Director name(s), comma-separated if multiple | Missing values filled with "Unknown"; whitespace stripped |
| `cast` | TEXT | Actor names, comma-separated | Missing values filled with "Unknown"; whitespace stripped |
| `country` | TEXT | Production country/countries, comma-separated | Missing values filled with "Unknown"; whitespace stripped |
| `date_added` | DATE | Date the title was added to Netflix | Parsed from "Month Day, Year" string to ISO date (YYYY-MM-DD) |
| `release_year` | INTEGER | Original release year of the title | None — original values preserved |
| `rating` | TEXT | Content maturity rating (e.g. TV-MA, PG-13, R) | Rows with missing rating dropped |
| `duration` | TEXT | Original duration string ("90 min" or "2 Seasons") | Kept as-is; see derived columns below |
| `listed_in` | TEXT | Genre(s), comma-separated (e.g. "Dramas, International Movies") | Whitespace stripped |
| `description` | TEXT | Synopsis of the title | Whitespace stripped |
| `year_added` | INTEGER | **Derived** — Year extracted from `date_added` | New column added during cleaning |
| `month_added` | INTEGER | **Derived** — Month (1–12) extracted from `date_added` | New column added during cleaning |
| `duration_value` | INTEGER | **Derived** — Numeric part of `duration` (e.g. 90, 2) | Extracted via regex from `duration` |
| `duration_unit` | TEXT | **Derived** — Unit part of `duration` ("min" or "season") | Extracted via regex; "seasons" normalized to "season" |
| `primary_country` | TEXT | **Derived** — First country listed in `country` | Split on comma, take first entry |
| `primary_genre` | TEXT | **Derived** — First genre listed in `listed_in` | Split on comma, take first entry |

## SQLite Table

The cleaned data is stored in `data/netflix.db`, table `titles`. The column `cast` is renamed to `cast_members` in SQLite to avoid the SQL reserved word. Indexes exist on: `type`, `release_year`, `year_added`, `rating`, `primary_country`, `primary_genre`.
