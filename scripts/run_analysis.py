import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# isort: split

from scripts.query_db import cell_type_frequency_query, run_query
from src.analysis import SIGNIFICANCE_THRESHOLD, compute_statistics, load_baseline_data, load_data
from src.charts import build_boxplot


OUTPUT_DIR = Path(__file__).parent.parent / "output"


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    df = load_data()
    baseline_df = load_baseline_data()

    # Statistics (Parts 2 & 4)
    stats_df = compute_statistics(df)
    stats_path = OUTPUT_DIR / "statistics.csv"
    stats_df.to_csv(stats_path, index=False)
    print(f"Wrote {stats_path}")

    sig = stats_df[stats_df["Significant"]
                   == "Yes"]["Cell Population"].tolist()
    if sig:
        print(
            f"\nSignificant populations (p < {SIGNIFICANCE_THRESHOLD}): {', '.join(sig)}")
    else:
        print(
            f"\nNo populations reached significance at p < {SIGNIFICANCE_THRESHOLD}")

    # Boxplot (Part 3)
    plot_path = OUTPUT_DIR / "boxplot.html"
    build_boxplot(df).write_html(plot_path)
    print(f"Wrote {plot_path}")

    # Baseline summary
    samples_per_project = (
        baseline_df.groupby("project_id").size().reset_index(name="samples")
    )
    response_counts = (
        baseline_df.dropna(subset=["response"])
        .drop_duplicates("subject_id")
        .groupby("response").size().reset_index(name="subjects")
    )
    sex_counts = (
        baseline_df.drop_duplicates("subject_id")
        .groupby("sex").size().reset_index(name="subjects")
    )

    baseline_path = OUTPUT_DIR / "baseline_summary.csv"
    samples_per_project.to_csv(baseline_path, index=False)
    print(f"Wrote {baseline_path}")

    print("\n--- Baseline: Samples per Project ---")
    print(samples_per_project.to_string(index=False))
    print("\n--- Baseline: Subjects by Response ---")
    print(response_counts.to_string(index=False))
    print("\n--- Baseline: Subjects by Sex ---")
    print(sex_counts.to_string(index=False))

    # Cell type frequency summary
    print("\n--- Cell Type Frequency (first 10 rows) ---")
    run_query(cell_type_frequency_query)


if __name__ == "__main__":
    main()
