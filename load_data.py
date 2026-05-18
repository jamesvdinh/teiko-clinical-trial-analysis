import argparse
import csv
import sqlite3
from pathlib import Path


def apply_schema(connection: sqlite3.Connection, schema_path: Path) -> None:
    with schema_path.open("r", encoding="utf-8") as schema_file:
        connection.executescript(schema_file.read())


def load_csv_data(connection: sqlite3.Connection, csv_path: Path) -> int:
    with csv_path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        rows = [
            (
                row["participant_id"],
                row["trial_arm"],
                row["visit_date"],
                row["immune_cell_type"],
                int(row["cell_count"]),
                float(row["biomarker_level"]),
                row["adverse_event"] or None,
            )
            for row in reader
        ]

    connection.executemany(
        """
        INSERT INTO clinical_trial_observations (
            participant_id,
            trial_arm,
            visit_date,
            immune_cell_type,
            cell_count,
            biomarker_level,
            adverse_event
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        rows,
    )
    return len(rows)


def initialize_database(db_path: Path, schema_path: Path, csv_path: Path) -> int:
    with sqlite3.connect(db_path) as connection:
        apply_schema(connection, schema_path)
        inserted_rows = load_csv_data(connection, csv_path)
        connection.commit()
    return inserted_rows


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Initialize a SQLite database with clinical trial data."
    )
    parser.add_argument(
        "--schema",
        default="schema.sql",
        help="Path to the SQL schema file (default: schema.sql)",
    )
    parser.add_argument(
        "--input",
        default="clinical_trial_data.csv",
        help="Path to the clinical trial CSV file (default: clinical_trial_data.csv)",
    )
    parser.add_argument(
        "--db",
        default="clinical_trial.db",
        help="Output SQLite database file path (default: clinical_trial.db)",
    )
    args = parser.parse_args()

    inserted_rows = initialize_database(
        Path(args.db),
        Path(args.schema),
        Path(args.input),
    )
    print(f"Database initialized at {args.db} with {inserted_rows} rows loaded.")


if __name__ == "__main__":
    main()
