"""
ETL script: loads raw Netflix titles CSV, cleans it, and writes to data/clean/.

Cleaning steps:
  1. Parse date_added to datetime
  2. Fill missing director/cast/country with "Unknown"
  3. Drop rows missing date_added or rating (very few)
  4. Split duration into numeric value + unit columns
  5. Remove exact duplicate rows (none expected, but defensive)
  6. Strip whitespace from string columns
  7. Ensure consistent types
"""

import argparse
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT / "data" / "raw" / "netflix_titles.csv"
CLEAN_PATH = ROOT / "data" / "clean" / "netflix_titles_clean.csv"


def load_raw(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"Loaded {len(df)} rows from {path}")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    initial = len(df)

    # --- Remove exact duplicates ---
    df = df.drop_duplicates()
    dropped_dupes = initial - len(df)
    if dropped_dupes:
        print(f"  Dropped {dropped_dupes} duplicate rows")

    # --- Strip whitespace from all string columns ---
    str_cols = df.select_dtypes(include=["object", "str"]).columns
    for col in str_cols:
        df[col] = df[col].str.strip()

    # --- Fill missing text fields ---
    for col in ["director", "cast", "country"]:
        n_missing = df[col].isna().sum()
        df[col] = df[col].fillna("Unknown")
        if n_missing:
            print(f"  Filled {n_missing} missing {col} values with 'Unknown'")

    # --- Drop rows with missing date_added or rating (very few) ---
    before = len(df)
    df = df.dropna(subset=["date_added", "rating"])
    dropped = before - len(df)
    if dropped:
        print(f"  Dropped {dropped} rows missing date_added or rating")

    # --- Parse date_added to datetime ---
    df["date_added"] = pd.to_datetime(df["date_added"], format="%B %d, %Y")

    # --- Extract year_added and month_added for easier analysis ---
    df["year_added"] = df["date_added"].dt.year.astype(int)
    df["month_added"] = df["date_added"].dt.month.astype(int)

    # --- Split duration into value + unit ---
    duration_split = df["duration"].str.extract(r"(\d+)\s*(.*)")
    df["duration_value"] = duration_split[0].astype(int)
    df["duration_unit"] = duration_split[1].str.strip().str.lower()
    # Normalize unit names
    df["duration_unit"] = df["duration_unit"].replace({"seasons": "season"})

    # --- Extract primary country (first listed) ---
    df["primary_country"] = df["country"].str.split(",").str[0].str.strip()

    # --- Extract primary genre (first listed_in entry) ---
    df["primary_genre"] = df["listed_in"].str.split(",").str[0].str.strip()

    # --- Ensure show_id is string (it's an identifier, not numeric) ---
    df["show_id"] = df["show_id"].astype(str)

    # --- Sort by date_added for consistency ---
    df = df.sort_values("date_added").reset_index(drop=True)

    print(f"  Final clean dataset: {len(df)} rows, {len(df.columns)} columns")
    return df


def save_clean(df: pd.DataFrame, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Saved clean data to {path}")


def main():
    parser = argparse.ArgumentParser(description="Clean Netflix titles dataset")
    parser.add_argument("--input", type=Path, default=RAW_PATH)
    parser.add_argument("--output", type=Path, default=CLEAN_PATH)
    args = parser.parse_args()

    df = load_raw(args.input)
    df = clean(df)
    save_clean(df, args.output)


if __name__ == "__main__":
    main()
