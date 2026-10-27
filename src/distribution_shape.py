"""
distribution_shape.py
Analyzes Distribution Shape (Symmetric vs. Skewed, Unimodal vs. Multimodal)
for key numerical features in the Data Science Jobs dataset.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Visual styling
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'axes.spines.top': False,
    'axes.spines.right': False
})


def get_paths():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(current_dir, "data", "DS_Jobs_cleaned.csv"),
        os.path.join(os.path.dirname(current_dir), "data", "DS_Jobs_cleaned.csv"),
        os.path.join(os.path.dirname(os.path.dirname(current_dir)), "data", "DS_Jobs_cleaned.csv"),
        os.path.abspath("data/DS_Jobs_cleaned.csv"),
    ]
    data_path = None
    for c in candidates:
        if os.path.exists(c):
            data_path = c
            break

    if data_path is None:
        raise FileNotFoundError("Could not find DS_Jobs_cleaned.csv")

    repo_root = os.path.dirname(os.path.dirname(data_path)) if "data" in data_path else current_dir
    charts_dir = os.path.join(os.path.dirname(os.path.dirname(data_path)), "outputs", "charts")
    if not os.path.exists(os.path.dirname(charts_dir)):
        charts_dir = os.path.join(os.path.dirname(data_path), "outputs", "charts")
    os.makedirs(charts_dir, exist_ok=True)
    return data_path, charts_dir


DATA_PATH, CHARTS_DIR = get_paths()


def load_data():
    df = pd.read_csv(DATA_PATH)
    print(f" Loaded dataset from: {DATA_PATH}")
    print(f" Dimensions: {df.shape[0]} rows, {df.shape[1]} columns")
    return df


def calculate_metrics(df):
    num_cols = ['Rating', 'avg_salary', 'company_age', 'min_salary', 'max_salary']
    summary_list = []

    for col in num_cols:
        s = df[col].dropna()
        mean_val = s.mean()
        med_val = s.median()
        mode_val = s.mode()[0]
        skew_val = s.skew()
        kurt_val = s.kurtosis()

        if abs(skew_val) < 0.5:
            shape_type = 'Symmetric (Normal)'
        elif skew_val >= 0.5:
            shape_type = 'Right-Skewed (Positive)'
        else:
            shape_type = 'Left-Skewed (Negative)'

        summary_list.append({
            'Variable': col,
            'Mean': round(mean_val, 2),
            'Median': round(med_val, 2),
            'Mode': round(mode_val, 2),
            'Skewness': round(skew_val, 2),
            'Kurtosis': round(kurt_val, 2),
            'Distribution Shape': shape_type,
            'Modality': 'Unimodal'
        })

    return pd.DataFrame(summary_list)


def plot_distributions(df):
    # 1. Symmetric Distribution: Rating
    fig, ax = plt.subplots(figsize=(10, 5))
    data = df['Rating'].dropna()
    mean_val = data.mean()
    median_val = data.median()
    mode_val = data.mode()[0]
    skew_val = data.skew()

    sns.histplot(data, kde=True, bins=25, color='#0D9488', edgecolor='white', alpha=0.6, ax=ax)
    ax.axvline(mean_val, color='#DC2626', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.2f}')
    ax.axvline(median_val, color='#16A34A', linestyle='-', linewidth=2, label=f'Median: {median_val:.2f}')
    ax.axvline(mode_val, color='#F59E0B', linestyle=':', linewidth=2, label=f'Mode: {mode_val:.2f}')

    ax.set_title(f'Symmetric & Unimodal: Company Rating (Skew: {skew_val:.2f} ≈ 0)', fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel('Company Rating (2.0 - 5.0)')
    ax.set_ylabel('Frequency')
    ax.legend()
    plt.tight_layout()
    rating_path = os.path.join(CHARTS_DIR, "dist_shape_rating.png")
    fig.savefig(rating_path, dpi=150)
    plt.close(fig)
    print(f" Saved chart: {rating_path}")

    # 2. Right-Skewed Distribution: avg_salary
    fig, ax = plt.subplots(figsize=(10, 5))
    data = df['avg_salary'].dropna()
    mean_val = data.mean()
    median_val = data.median()
    mode_val = data.mode()[0]
    skew_val = data.skew()

    sns.histplot(data, kde=True, bins=30, color='#2563EB', edgecolor='white', alpha=0.6, ax=ax)
    ax.axvline(mean_val, color='#DC2626', linestyle='--', linewidth=2, label=f'Mean: ${mean_val:.1f}K')
    ax.axvline(median_val, color='#16A34A', linestyle='-', linewidth=2, label=f'Median: ${median_val:.1f}K')
    ax.axvline(mode_val, color='#F59E0B', linestyle=':', linewidth=2, label=f'Mode: ${mode_val:.1f}K')

    ax.set_title(f'Right-Skewed & Unimodal: Average Salary (Skew: {skew_val:.2f} > 0)', fontsize=13, fontweight='bold', pad=12)
    ax.set_xlabel('Average Salary ($K USD)')
    ax.set_ylabel('Frequency')
    ax.legend()
    plt.tight_layout()
    sal_path = os.path.join(CHARTS_DIR, "dist_shape_salary.png")
    fig.savefig(sal_path, dpi=150)
    plt.close(fig)
    print(f" Saved chart: {sal_path}")

    # 3. Comparative Overview across 3 key variables
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    plot_configs = [
        ('Rating', 'Company Rating', '#0D9488', 20),
        ('avg_salary', 'Average Salary ($K)', '#2563EB', 25),
        ('company_age', 'Company Age (Years)', '#7C3AED', 25)
    ]

    for ax, (c, title, color, bins) in zip(axes, plot_configs):
        d = df[c].dropna()
        mean = d.mean()
        med = d.median()
        skew = d.skew()

        sns.histplot(d, kde=True, bins=bins, color=color, edgecolor='white', alpha=0.6, ax=ax)
        ax.axvline(mean, color='#DC2626', linestyle='--', linewidth=2, label=f'Mean: {mean:.1f}')
        ax.axvline(med, color='#16A34A', linestyle='-', linewidth=2, label=f'Median: {med:.1f}')

        shape_label = 'Symmetric' if abs(skew) < 0.5 else 'Right-Skewed'
        ax.set_title(f'{title}\n{shape_label} (Skew: {skew:.2f})', fontsize=12, fontweight='bold')
        ax.set_xlabel(title, fontsize=10)
        ax.set_ylabel('Frequency', fontsize=10)
        ax.legend(fontsize=9)

    plt.suptitle('Distribution Shape Comparison across Key Numerical Variables', fontsize=15, fontweight='bold', y=1.03)
    plt.tight_layout()
    comp_path = os.path.join(CHARTS_DIR, "dist_shape_comparison.png")
    fig.savefig(comp_path, dpi=150)
    plt.close(fig)
    print(f" Saved chart: {comp_path}")


if __name__ == '__main__':
    print("=" * 60)
    print(" 3. Distribution Analysis — Distribution Shape")
    print("=" * 60)

    df = load_data()
    metrics_table = calculate_metrics(df)
    print("\n--- Statistical Diagnosis Table ---")
    print(metrics_table.to_string(index=False))

    print("\n--- Generating & Saving Charts ---")
    plot_distributions(df)

    print("\n" + "=" * 60)
    print(" Analysis Complete. All charts saved to outputs/charts/")
    print("=" * 60)
