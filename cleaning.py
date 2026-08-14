"""
data_cleaning.py
Loads computer_science_jobs_cleaned.xlsx and returns a cleaned DataFrame
ready for analysis.
"""

import pandas as pd
import ast


def parse_skills(raw):
    """Convert a raw skill string like \"['python','sql']\" into a clean list."""
    if pd.isna(raw):
        return []
    try:
        return [skill.strip().lower() for skill in ast.literal_eval(raw)]
    except Exception:
        return []


def load_and_clean(filepath="dataset/computer_science_jobs_cleaned.xlsx"):
    """Load and clean the CS job postings dataset."""
    df = pd.read_excel(filepath)

    # Parse skills into Python lists
    df["skills_list"] = df["job_skills"].apply(parse_skills)

    # Drop rows with no skills (should be none, but kept for safety/reuse)
    df_clean = df[df["skills_list"].map(len) > 0].copy()

    return df, df_clean


if __name__ == "__main__":
    df_raw, df_clean = load_and_clean()
    print(f"Raw rows: {len(df_raw):,}")
    print(f"Rows after removing missing skills: {len(df_clean):,}")
    print(f"Job titles: {df_raw['job_title_short'].nunique()}")
    print(f"Countries: {df_raw['job_country'].nunique()}")
    print(f"Rows with salary data: {df_clean['salary_year_avg'].notna().sum():,}")