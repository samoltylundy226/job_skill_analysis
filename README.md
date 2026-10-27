# Computer Science Job Skills Analysis

Analysis of in-demand technical skills, salaries, and hiring trends across **478,895 Computer Science job postings** (Full Year 2024, 160 countries, 10 roles).

## Project Structure

```text
job_skill_analysis/
├── data/
│   ├── raw/
│   │   └── job_postings_flat.csv      # Raw 2024 dataset (478,895 rows, 17 columns)
│   └── processed/                     # Cleaned/processed datasets
├── notebooks/
│   └── CS_Job_Skills_Analysis.ipynb   # Interactive exploratory analysis notebook
├── src/
│   ├── __init__.py
│   ├── cleaning.py                    # Data loading & skill parsing utilities
│   ├── analysis.py                    # Aggregation & statistical summaries
│   └── visualization.py               # Publication-quality chart generation
├── outputs/
│   ├── charts/                        # Saved chart PNGs
│   └── tables/                        # Exported summary CSV tables
├── .gitignore
├── requirements.txt
└── README.md
```
