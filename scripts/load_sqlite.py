"""
Load cleaned Netflix data into a SQLite database with proper schema and indexes.
Demonstrates queryability with sample analytical queries.
"""

import argparse
import sqlite3
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
CLEAN_PATH = ROOT / "data" / "clean" / "netflix_titles_clean.csv"
DB_PATH = ROOT / "data" / "netflix.db"


def create_schema(conn: sqlite3.Connection):
    conn.execute("DROP TABLE IF EXISTS titles")
    conn.execute("""
        CREATE TABLE titles (
            show_id        TEXT PRIMARY KEY,
            type           TEXT NOT NULL,
            title          TEXT NOT NULL,
            director       TEXT,
            cast_members   TEXT,
            country        TEXT,
            date_added     TEXT,
            release_year   INTEGER,
            rating         TEXT,
            duration       TEXT,
            listed_in      TEXT,
            description    TEXT,
            year_added     INTEGER,
            month_added    INTEGER,
            duration_value INTEGER,
            duration_unit  TEXT,
            primary_country TEXT,
            primary_genre  TEXT
        )
    """)
    conn.execute("CREATE INDEX idx_type ON titles(type)")
    conn.execute("CREATE INDEX idx_release_year ON titles(release_year)")
    conn.execute("CREATE INDEX idx_year_added ON titles(year_added)")
    conn.execute("CREATE INDEX idx_rating ON titles(rating)")
    conn.execute("CREATE INDEX idx_primary_country ON titles(primary_country)")
    conn.execute("CREATE INDEX idx_primary_genre ON titles(primary_genre)")
    conn.commit()


def load_data(conn: sqlite3.Connection, csv_path: Path):
    df = pd.read_csv(csv_path)
    # Rename 'cast' to 'cast_members' to avoid SQL reserved word
    df = df.rename(columns={"cast": "cast_members"})
    df.to_sql("titles", conn, if_exists="append", index=False)
    print(f"Loaded {len(df)} rows into titles table")


def run_demo_queries(conn: sqlite3.Connection):
    queries = [
        (
            "Content count by type",
            "SELECT type, COUNT(*) as count FROM titles GROUP BY type"
        ),
        (
            "Top 10 years by titles added",
            """SELECT year_added, COUNT(*) as count
               FROM titles
               GROUP BY year_added
               ORDER BY count DESC
               LIMIT 10"""
        ),
        (
            "Top 10 genres",
            """SELECT primary_genre, COUNT(*) as count
               FROM titles
               GROUP BY primary_genre
               ORDER BY count DESC
               LIMIT 10"""
        ),
        (
            "Top 10 producing countries",
            """SELECT primary_country, COUNT(*) as count
               FROM titles
               WHERE primary_country != 'Unknown'
               GROUP BY primary_country
               ORDER BY count DESC
               LIMIT 10"""
        ),
        (
            "Average movie duration (min) by rating",
            """SELECT rating, ROUND(AVG(duration_value), 1) as avg_minutes
               FROM titles
               WHERE type = 'Movie'
               GROUP BY rating
               ORDER BY avg_minutes DESC
               LIMIT 10"""
        ),
    ]

    print("\n" + "=" * 60)
    print("DEMO QUERIES")
    print("=" * 60)

    for label, sql in queries:
        print(f"\n--- {label} ---")
        cursor = conn.execute(sql)
        cols = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        # Simple table output
        header = "  ".join(f"{c:<20}" for c in cols)
        print(header)
        print("-" * len(header))
        for row in rows:
            print("  ".join(f"{str(v):<20}" for v in row))


def main():
    parser = argparse.ArgumentParser(description="Load cleaned data into SQLite")
    parser.add_argument("--input", type=Path, default=CLEAN_PATH)
    parser.add_argument("--db", type=Path, default=DB_PATH)
    parser.add_argument("--no-demo", action="store_true", help="Skip demo queries")
    args = parser.parse_args()

    args.db.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(args.db)
    create_schema(conn)
    load_data(conn, args.input)

    if not args.no_demo:
        run_demo_queries(conn)

    conn.close()
    print(f"\nDatabase saved to {args.db}")


if __name__ == "__main__":
    main()
