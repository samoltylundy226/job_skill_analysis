"""
visualization.py
Generates publication-quality charts for the CS Job Skills Analysis.

Charts:
  1. Number of job postings by CS job title
  2. Top 15 most in-demand skills (horizontal bar)
  3. Skill frequency by job title (heatmap)
  4. Average salary by skill – top 15 (horizontal bar)
  5. Word cloud of all skills
  6. Top 8 skills for each of the 6 major job titles (small multiples)
  7. Top 5 skills by country (small multiples)
  8. Average salary by job title (horizontal bar)
  9. Job posting trend over time (daily line chart, Jan 2024)
  10. Skill categories (horizontal bar / donut)
  11. Skill importance ranking — number of job roles per skill
  12. Average number of skills required per job
"""

import pandas as pd
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.dates as mdates
from collections import Counter
from data_cleaning import load_and_clean
from analysis import SKILL_CATEGORIES

CHARTS_DIR = "charts"
os.makedirs(CHARTS_DIR, exist_ok=True)

# ── Design tokens ──────────────────────────────────────────────────────────────
NAVY    = "#1E3A5F"
BLUE    = "#2563EB"
INDIGO  = "#4F46E5"
TEAL    = "#0D9488"
AMBER   = "#D97706"
ROSE    = "#E11D48"
SLATE   = "#475569"
WHITE   = "#FFFFFF"
DARK    = "#1E293B"

PALETTE = [BLUE, INDIGO, TEAL, AMBER, ROSE, "#7C3AED", "#059669", "#DC2626", "#0891B2", "#65A30D"]

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": "#E2E8F0",
    "grid.linewidth": 0.6,
    "axes.facecolor": WHITE,
    "figure.facecolor": WHITE,
})


def save(fig, name):
    path = f"{CHARTS_DIR}/{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    print(f"  Saved: {path}")
    return path


# ── Load data ──────────────────────────────────────────────────────────────────
df_raw, df = load_and_clean()
df_sal = df[df["salary_year_avg"].notna()].copy()
all_skills = [sk for lst in df["skills_list"] for sk in lst]

# ─────────────────────────────────────────────────────────────────────────────
# Chart 1 – Job Postings by Title
# ─────────────────────────────────────────────────────────────────────────────
print("Generating Chart 1: Job Postings by Title …")
title_counts = df_raw["job_title_short"].value_counts()

fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.barh(title_counts.index[::-1], title_counts.values[::-1],
               color=[PALETTE[i % len(PALETTE)] for i in range(len(title_counts))],
               edgecolor=WHITE, linewidth=0.8)
for bar in bars:
    ax.text(bar.get_width() + max(title_counts.values) * 0.01, bar.get_y() + bar.get_height() / 2,
            f"{bar.get_width():,.0f}", va="center", fontsize=9, color=SLATE)
ax.set_xlabel("Number of Job Postings", fontsize=11, color=DARK)
ax.set_title("Computer Science Job Postings by Role", fontsize=15, fontweight="bold", color=NAVY, pad=15)
ax.set_xlim(0, title_counts.max() * 1.13)
fig.tight_layout()
save(fig, "chart1_job_postings_by_title")

# ─────────────────────────────────────────────────────────────────────────────
# Chart 2 – Top 15 Skills Overall
# ─────────────────────────────────────────────────────────────────────────────
print("Generating Chart 2: Top 15 Skills Overall …")
top15 = pd.Series(Counter(all_skills)).sort_values().tail(15)

fig, ax = plt.subplots(figsize=(11, 7))
bar_colors = [ROSE if i >= 13 else BLUE if i >= 10 else TEAL for i in range(len(top15))]
bars = ax.barh(top15.index, top15.values, color=bar_colors, edgecolor=WHITE, linewidth=0.8)
for bar in bars:
    ax.text(bar.get_width() + top15.max() * 0.01, bar.get_y() + bar.get_height() / 2,
            f"{bar.get_width():,.0f}", va="center", fontsize=9, color=SLATE)
ax.set_xlabel("Frequency in Job Postings", fontsize=11, color=DARK)
ax.set_title("Top 15 Most In-Demand Skills in CS Jobs", fontsize=15, fontweight="bold", color=NAVY, pad=15)
ax.set_xlim(0, top15.max() * 1.12)
legend_elems = [
    mpatches.Patch(color=ROSE, label="Top 2 (Python, SQL)"),
    mpatches.Patch(color=BLUE, label="Ranks 3–5"),
    mpatches.Patch(color=TEAL, label="Ranks 6–15"),
]
ax.legend(handles=legend_elems, fontsize=9, loc="lower right")
fig.tight_layout()
save(fig, "chart2_top15_skills_overall")

# ─────────────────────────────────────────────────────────────────────────────
# Chart 4 – Average Salary by Skill
# ─────────────────────────────────────────────────────────────────────────────
print("Generating Chart 4: Salary by Skill …")

skill_salaries = {}
for _, row in df_sal.iterrows():
    for sk in row["skills_list"]:
        skill_salaries.setdefault(sk, []).append(row["salary_year_avg"])

sal_series = pd.Series({
    sk: pd.Series(v).mean()
    for sk, v in skill_salaries.items() if len(v) >= 10
}).sort_values().tail(15)

fig, ax = plt.subplots(figsize=(11, 7))
bar_colors = [ROSE if v >= 150000 else AMBER if v >= 130000 else TEAL for v in sal_series.values]
bars = ax.barh(sal_series.index, sal_series.values / 1000, color=bar_colors, edgecolor=WHITE, linewidth=0.8)
for bar in bars:
    ax.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height() / 2,
            f"${bar.get_width():.0f}K", va="center", fontsize=9, color=SLATE)
ax.set_xlabel("Average Annual Salary (USD thousands)", fontsize=11, color=DARK)
ax.set_title("Top 15 CS Skills by Average Salary", fontsize=15, fontweight="bold", color=NAVY, pad=15)
ax.set_xlim(0, sal_series.max() / 1000 * 1.15)
legend_elems = [
    mpatches.Patch(color=ROSE,  label=">= $150K avg"),
    mpatches.Patch(color=AMBER, label="$130K – $150K"),
    mpatches.Patch(color=TEAL,  label="< $130K"),
]
ax.legend(handles=legend_elems, fontsize=9, loc="lower right")
fig.tight_layout()
save(fig, "chart4_salary_by_skill")

# ─────────────────────────────────────────────────────────────────────────────
# Chart 5 – Word Cloud
# ─────────────────────────────────────────────────────────────────────────────
print("Generating Chart 5: Word Cloud …")
try:
    from wordcloud import WordCloud
    wc = WordCloud(
        width=1400, height=700,
        background_color=WHITE,
        colormap="Blues_r",
        max_words=100,
        prefer_horizontal=0.75,
        min_font_size=10,
    ).generate_from_frequencies(Counter(all_skills))

    fig, ax = plt.subplots(figsize=(14, 7))
    ax.imshow(wc, interpolation="bilinear")
    ax.axis("off")
    ax.set_title("CS Job Skills – Word Cloud (larger = more frequent)", fontsize=15,
                 fontweight="bold", color=NAVY, pad=15)
    fig.tight_layout()
    save(fig, "chart5_wordcloud")
except ImportError:
    print("  wordcloud not installed – skipping. Run: pip install wordcloud")

# ─────────────────────────────────────────────────────────────────────────────
# Chart 6 – Top 8 Skills for Each Major Job Title (small multiples)
# ─────────────────────────────────────────────────────────────────────────────
print("Generating Chart 6: Top Skills by Job Title (small multiples) …")
major_jobs = df["job_title_short"].value_counts().head(6).index.tolist()

fig, axes = plt.subplots(2, 3, figsize=(16, 9))
for ax, job in zip(axes.flat, major_jobs):
    skills = [sk for lst in df.loc[df["job_title_short"] == job, "skills_list"] for sk in lst]
    top8 = pd.Series(Counter(skills)).sort_values().tail(8)
    bar_colors = [BLUE if i < 5 else TEAL for i in range(len(top8))]
    ax.barh(top8.index, top8.values, color=bar_colors, edgecolor=WHITE, linewidth=0.7)
    for j, v in enumerate(top8.values):
        ax.text(v + top8.max() * 0.02, j, f"{v:,.0f}", va="center", fontsize=7.5, color=SLATE)
    ax.set_title(f"{job}  (n={df['job_title_short'].eq(job).sum():,})", fontsize=11,
                 fontweight="bold", color=NAVY)
    ax.tick_params(axis="y", labelsize=8.5)
    ax.tick_params(axis="x", labelsize=7)
    ax.set_xlim(0, top8.max() * 1.2)

fig.suptitle("Top Skills by Job Title", fontsize=16, fontweight="bold", color=NAVY, y=1.01)
fig.tight_layout()
save(fig, "chart6_top_skills_by_job_title")

# ─────────────────────────────────────────────────────────────────────────────
# Chart 7 – Top 5 Skills by Country (small multiples)
# ─────────────────────────────────────────────────────────────────────────────
print("Generating Chart 7: Skills by Country …")
top_countries = df["job_country"].value_counts().head(5).index.tolist()

fig, axes = plt.subplots(1, 5, figsize=(18, 5.5))
for ax, country in zip(axes, top_countries):
    skills = [sk for lst in df.loc[df["job_country"] == country, "skills_list"] for sk in lst]
    top5 = pd.Series(Counter(skills)).sort_values().tail(5)
    ax.barh(top5.index, top5.values, color=PALETTE[:5], edgecolor=WHITE, linewidth=0.7)
    n = df["job_country"].eq(country).sum()
    ax.set_title(f"{country}\n(n={n:,})", fontsize=10, fontweight="bold", color=NAVY)
    ax.tick_params(axis="y", labelsize=8)
    ax.tick_params(axis="x", labelsize=7)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

fig.suptitle("Top 5 Skills by Country (Top 5 Countries by Posting Volume)", fontsize=14,
             fontweight="bold", color=NAVY, y=1.04)
fig.tight_layout()
save(fig, "chart7_skills_by_country")

# ─────────────────────────────────────────────────────────────────────────────
# Chart 8 – Average Salary by Job Title
# ─────────────────────────────────────────────────────────────────────────────
print("Generating Chart 8: Average Salary by Job Title …")
sal_by_job = df_sal.groupby("job_title_short")["salary_year_avg"].agg(["mean", "count"]).sort_values("mean")

fig, ax = plt.subplots(figsize=(10, 6))
bar_colors = [TEAL if c >= 50 else AMBER if c >= 10 else ROSE for c in sal_by_job["count"]]
bars = ax.barh(sal_by_job.index, sal_by_job["mean"] / 1000, color=bar_colors, edgecolor=WHITE, linewidth=0.8)
for bar, n in zip(bars, sal_by_job["count"]):
    ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
            f"${bar.get_width():.0f}K (n={n})", va="center", fontsize=8.5, color=SLATE)
ax.set_xlabel("Average Annual Salary (USD thousands)", fontsize=11, color=DARK)
ax.set_title("Average Salary by Job Title", fontsize=15, fontweight="bold", color=NAVY, pad=15)
ax.set_xlim(0, sal_by_job["mean"].max() / 1000 * 1.3)
legend_elems = [
    mpatches.Patch(color=TEAL,  label="n >= 50 (reliable)"),
    mpatches.Patch(color=AMBER, label="10 <= n < 50"),
    mpatches.Patch(color=ROSE,  label="n < 10 (low confidence)"),
]
ax.legend(handles=legend_elems, fontsize=8.5, loc="lower right")
fig.tight_layout()
save(fig, "chart8_avg_salary_by_job_title")

# ─────────────────────────────────────────────────────────────────────────────
# Chart 9 – Job Posting Trend Over Time (daily, Jan 2024)
# ─────────────────────────────────────────────────────────────────────────────
print("Generating Chart 9: Job Posting Trend …")
df_raw["post_date"] = pd.to_datetime(df_raw["job_posted_date"]).dt.normalize()
trend = df_raw.groupby("post_date").size()

fig, ax = plt.subplots(figsize=(12, 5.5))
ax.plot(trend.index, trend.values, color=BLUE, linewidth=2, marker="o", markersize=3.5)
ax.fill_between(trend.index, trend.values, color=BLUE, alpha=0.08)
ax.set_ylabel("Job Postings", fontsize=11, color=DARK)
ax.set_title("Job Posting Volume by Day (January 2024)", fontsize=15, fontweight="bold", color=NAVY, pad=15)
ax.xaxis.set_major_locator(mdates.DayLocator(interval=3))
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
fig.autofmt_xdate(rotation=45)
fig.tight_layout()
save(fig, "chart9_posting_trend")

# ─────────────────────────────────────────────────────────────────────────────
# Chart 10 – Skill Categories
# ─────────────────────────────────────────────────────────────────────────────
print("Generating Chart 10: Skill Categories …")
skill_freq = Counter(all_skills)
cat_totals = pd.Series({
    cat: sum(skill_freq.get(s, 0) for s in skills)
    for cat, skills in SKILL_CATEGORIES.items()
}).sort_values()

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(cat_totals.index, cat_totals.values, color=PALETTE[:len(cat_totals)], edgecolor=WHITE, linewidth=0.8)
for bar in bars:
    ax.text(bar.get_width() + cat_totals.max() * 0.01, bar.get_y() + bar.get_height() / 2,
            f"{bar.get_width():,.0f}", va="center", fontsize=9, color=SLATE)
ax.set_xlabel("Total Skill Mentions", fontsize=11, color=DARK)
ax.set_title("Skill Categories Across All CS Job Postings", fontsize=15, fontweight="bold", color=NAVY, pad=15)
ax.set_xlim(0, cat_totals.max() * 1.15)
fig.tight_layout()
save(fig, "chart10_skill_categories")

# ─────────────────────────────────────────────────────────────────────────────
# Chart 11 – Skill Importance Ranking (number of job roles)
# ─────────────────────────────────────────────────────────────────────────────
print("Generating Chart 11: Skill Importance Ranking …")
skill_role_set = {}
for job in df["job_title_short"].unique():
    job_skills_flat = set(sk for lst in df.loc[df["job_title_short"] == job, "skills_list"] for sk in lst)
    for sk in job_skills_flat:
        skill_role_set.setdefault(sk, set()).add(job)

importance = pd.Series({sk: len(roles) for sk, roles in skill_role_set.items()})
importance = importance.sort_values().tail(15)

fig, ax = plt.subplots(figsize=(10, 7))
total_roles = df["job_title_short"].nunique()
bar_colors = [INDIGO if v == importance.max() else BLUE for v in importance.values]
bars = ax.barh(importance.index, importance.values, color=bar_colors, edgecolor=WHITE, linewidth=0.8)
for bar in bars:
    pct = bar.get_width() / total_roles * 100
    ax.text(bar.get_width() + 0.07, bar.get_y() + bar.get_height() / 2,
            f"{bar.get_width():.0f} roles ({pct:.0f}%)", va="center", fontsize=8.5, color=SLATE)
ax.set_xlabel("Number of Job Roles Requiring This Skill", fontsize=11, color=DARK)
ax.set_title("Skill Importance Ranking — Used Across Most Job Roles", fontsize=14,
             fontweight="bold", color=NAVY, pad=15)
ax.set_xlim(0, total_roles + 2)
fig.tight_layout()
save(fig, "chart11_skill_importance")

# ─────────────────────────────────────────────────────────────────────────────
# Chart 12 – Average Number of Skills Required per Job
# ─────────────────────────────────────────────────────────────────────────────
print("Generating Chart 12: Average Skills Required per Job …")
df["n_skills"] = df["skills_list"].map(len)
avg_skills = df.groupby("job_title_short")["n_skills"].mean().sort_values()

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(avg_skills.index, avg_skills.values, color=PALETTE[:len(avg_skills)], edgecolor=WHITE, linewidth=0.8)
for bar in bars:
    ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
            f"{bar.get_width():.1f}", va="center", fontsize=9, color=SLATE)
ax.set_xlabel("Average Number of Skills Listed per Posting", fontsize=11, color=DARK)
ax.set_title("Average Number of Skills Required per Job Title", fontsize=14,
             fontweight="bold", color=NAVY, pad=15)
ax.set_xlim(0, avg_skills.max() * 1.2)
fig.tight_layout()
save(fig, "chart12_avg_skills_per_job")

print("\nAll charts saved to /charts/")