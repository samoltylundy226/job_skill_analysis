"""
analysis.py
Runs all analyses and saves results as CSV files to /output/.

Analyses:
  1. Job postings count by CS job title
  2. Top 15 most requested skills across all CS jobs
  3. Top skills for each CS job title (top 5, all jobs + top 8 for major roles)
  4. Skills by country (top 5 countries)
  5. Average salary by job title
  6. Job posting trend over time (daily, Jan 2024)
  7. Skill categories (Programming, Database, Cloud, etc.)
  8. Skill importance ranking (number of job roles using each skill)
  9. Average number of skills required per job
  10. Average salary by skill (top 15, min 10 data points)
"""

import pandas as pd
from collections import Counter
from data_cleaning import load_and_clean

OUTPUT_DIR = "output"

SKILL_CATEGORIES = {
    "Programming":        ["python", "java", "r", "c", "c++", "javascript", "scala", "go", "ruby", "php", "c#", "sas", "matlab"],
    "Database":           ["sql", "mysql", "postgresql", "mongodb", "oracle", "nosql", "sql server", "redshift", "bigquery", "snowflake"],
    "Cloud":              ["aws", "azure", "gcp", "google cloud"],
    "Visualization / BI": ["tableau", "power bi", "looker", "qlik", "excel"],
    "Version Control":    ["git", "github", "gitlab", "bitbucket"],
    "Big Data":           ["spark", "hadoop", "kafka", "pyspark", "airflow", "databricks"],
    "AI / ML":            ["tensorflow", "pytorch", "scikit-learn", "keras", "sklearn"],
    "DevOps / Containers": ["docker", "kubernetes", "jenkins", "terraform", "ansible"],
}


def run():
    print("=" * 55)
    print("  CS Job Skills Analysis")
    print("=" * 55)

    df_raw, df = load_and_clean()
    df_sal = df[df["salary_year_avg"].notna()].copy()

    print(f"\nDataset loaded: {len(df_raw):,} CS job postings")
    print(f"With skills data: {len(df):,}")
    print(f"With salary data: {len(df_sal):,}")

    # ── Analysis 1: Job Postings Count by Title ──────────────────────────────
    title_counts = df_raw["job_title_short"].value_counts().reset_index()
    title_counts.columns = ["job_title", "postings"]
    title_counts.to_csv(f"{OUTPUT_DIR}/analysis1_job_title_counts.csv", index=False)
    print(f"\n[1] Job postings by title:\n{title_counts.to_string(index=False)}")

    # ── Analysis 2: Top 15 Skills Overall ────────────────────────────────────
    all_skills = [sk for lst in df["skills_list"] for sk in lst]
    top15 = pd.Series(Counter(all_skills)).sort_values(ascending=False).head(15).reset_index()
    top15.columns = ["skill", "count"]
    top15["pct_of_postings"] = (top15["count"] / len(df) * 100).round(1)
    top15.to_csv(f"{OUTPUT_DIR}/analysis2_top15_skills.csv", index=False)
    print(f"\n[2] Top 15 skills overall:\n{top15.to_string(index=False)}")

    # ── Analysis 3: Top 5 Skills per Job Title ────────────────────────────────
    rows = []
    for job in df["job_title_short"].unique():
        skills = [sk for lst in df.loc[df["job_title_short"] == job, "skills_list"] for sk in lst]
        for rank, (skill, count) in enumerate(Counter(skills).most_common(5), start=1):
            rows.append({"job_title": job, "rank": rank, "skill": skill, "count": count})
    top5_per_job = pd.DataFrame(rows)
    top5_per_job.to_csv(f"{OUTPUT_DIR}/analysis3_top5_per_job.csv", index=False)
    print(f"\n[3] Top 5 skills per job title:\n{top5_per_job.to_string(index=False)}")

    # ── Analysis 4: Average Salary by Skill ──────────────────────────────────
    skill_salaries = {}
    for _, row in df_sal.iterrows():
        for sk in row["skills_list"]:
            skill_salaries.setdefault(sk, []).append(row["salary_year_avg"])

    sal_data = [
        {"skill": sk, "avg_salary": round(pd.Series(v).mean(), 0), "data_points": len(v)}
        for sk, v in skill_salaries.items()
        if len(v) >= 10
    ]
    sal_df = pd.DataFrame(sal_data).sort_values("avg_salary", ascending=False).head(15)
    sal_df.to_csv(f"{OUTPUT_DIR}/analysis4_salary_by_skill.csv", index=False)
    print(f"\n[4] Top 15 skills by avg salary:\n{sal_df.to_string(index=False)}")

    # ── Analysis 5: Top Skills for Major Job Titles (top 8 each) ─────────────
    major_jobs = df["job_title_short"].value_counts().head(6).index.tolist()
    rows5 = []
    for job in major_jobs:
        skills = [sk for lst in df.loc[df["job_title_short"] == job, "skills_list"] for sk in lst]
        for rank, (skill, count) in enumerate(Counter(skills).most_common(8), start=1):
            rows5.append({"job_title": job, "rank": rank, "skill": skill, "count": count})
    top8_major = pd.DataFrame(rows5)
    top8_major.to_csv(f"{OUTPUT_DIR}/analysis5_top8_major_jobs.csv", index=False)
    print(f"\n[5] Top 8 skills for major job titles:\n{top8_major.to_string(index=False)}")

    # ── Analysis 6: Skills by Country (top 5 countries) ──────────────────────
    top_countries = df["job_country"].value_counts().head(5).index.tolist()
    rows6 = []
    for country in top_countries:
        skills = [sk for lst in df.loc[df["job_country"] == country, "skills_list"] for sk in lst]
        for rank, (skill, count) in enumerate(Counter(skills).most_common(5), start=1):
            rows6.append({"country": country, "rank": rank, "skill": skill, "count": count})
    country_skills = pd.DataFrame(rows6)
    country_skills.to_csv(f"{OUTPUT_DIR}/analysis6_skills_by_country.csv", index=False)
    print(f"\n[6] Top 5 skills by country:\n{country_skills.to_string(index=False)}")

    # ── Analysis 7: Average Salary by Job Title ───────────────────────────────
    sal_by_job = (
        df_sal.groupby("job_title_short")["salary_year_avg"]
        .agg(avg_salary="mean", data_points="count")
        .reset_index()
        .sort_values("avg_salary", ascending=False)
    )
    sal_by_job["avg_salary"] = sal_by_job["avg_salary"].round(0)
    sal_by_job.to_csv(f"{OUTPUT_DIR}/analysis7_salary_by_job_title.csv", index=False)
    print(f"\n[7] Average salary by job title:\n{sal_by_job.to_string(index=False)}")

    # ── Analysis 8: Job Posting Trend Over Time (daily, Jan 2024) ────────────
    df_raw["post_date"] = pd.to_datetime(df_raw["job_posted_date"]).dt.date
    trend = df_raw.groupby("post_date").size().reset_index(name="postings")
    trend.to_csv(f"{OUTPUT_DIR}/analysis8_posting_trend.csv", index=False)
    print(f"\n[8] Job posting trend (daily): {len(trend)} days, "
          f"min={trend['postings'].min()}, max={trend['postings'].max()}")

    # ── Analysis 9: Skill Categories ──────────────────────────────────────────
    skill_freq = Counter(all_skills)
    cat_rows = []
    for cat, skills in SKILL_CATEGORIES.items():
        total = sum(skill_freq.get(s, 0) for s in skills)
        cat_rows.append({"category": cat, "total_mentions": total})
    cat_df = pd.DataFrame(cat_rows).sort_values("total_mentions", ascending=False)
    cat_df.to_csv(f"{OUTPUT_DIR}/analysis9_skill_categories.csv", index=False)
    print(f"\n[9] Skill categories:\n{cat_df.to_string(index=False)}")

    # ── Analysis 10: Skill Importance Ranking (number of job roles) ──────────
    skill_role_set = {}
    for job in df["job_title_short"].unique():
        job_skills_flat = set(sk for lst in df.loc[df["job_title_short"] == job, "skills_list"] for sk in lst)
        for sk in job_skills_flat:
            skill_role_set.setdefault(sk, set()).add(job)

    importance = pd.Series({sk: len(roles) for sk, roles in skill_role_set.items()}).sort_values(ascending=False).head(15)
    importance_df = importance.reset_index()
    importance_df.columns = ["skill", "num_job_roles"]
    importance_df.to_csv(f"{OUTPUT_DIR}/analysis10_skill_importance.csv", index=False)
    print(f"\n[10] Skill importance ranking (top 15):\n{importance_df.to_string(index=False)}")

    # ── Analysis 11: Average Number of Skills Required per Job ───────────────
    df["n_skills"] = df["skills_list"].map(len)
    avg_skills = df.groupby("job_title_short")["n_skills"].mean().sort_values(ascending=False).reset_index()
    avg_skills.columns = ["job_title", "avg_skills_required"]
    avg_skills["avg_skills_required"] = avg_skills["avg_skills_required"].round(1)
    avg_skills.to_csv(f"{OUTPUT_DIR}/analysis11_avg_skills_per_job.csv", index=False)
    print(f"\n[11] Average skills required per job:\n{avg_skills.to_string(index=False)}")

    print("\n" + "=" * 55)
    print("  Done. CSVs saved to /output/")
    print("=" * 55)


if __name__ == "__main__":
    run()