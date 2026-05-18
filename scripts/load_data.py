import argparse
import csv
import sqlite3
from pathlib import Path

DIR_PATH = Path(__file__).resolve().parent


def apply_schema(connection: sqlite3.Connection, schema_path: Path):
    """Executes the SQL schema file to create the db structure"""
    with schema_path.open('r', encoding="utf-8") as schema_file:
        connection.executescript(schema_file.read())


def load_csv(connection: sqlite3.Connection, csv_path: Path):
    """Loads data from a CSV file into the database"""
    with csv_path.open('r', encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        placeholders = ','.join(['?'] * len(reader.fieldnames))
        rows = [
            (
                row["sample"],
                row["project"],
                row["subject"],
                row["condition"],
                int(row["age"]),
                row["sex"],
                row["treatment"],
                row["response"] or None,
                row["sample_type"],
                int(row["time_from_treatment_start"]),
                int(row["b_cell"]),
                int(row["cd8_t_cell"]),
                int(row["cd4_t_cell"]),
                int(row["nk_cell"]),
                int(row["monocyte"])
            )
            for row in reader
        ]
        insert_query = (
            f"""
            INSERT INTO clinical_trial_observations (
                sample_id,
                project_id,
                subject_id,
                condition,
                age,
                sex,
                treatment,
                response,
                sample_type,
                time_from_treatment_start,
                b_cell,
                cd8_t_cell,
                cd4_t_cell,
                nk_cell,
                monocyte
                ) VALUES ({placeholders})
            """
        )
        connection.executemany(insert_query, rows)
        return len(rows)


def init_database(db_path: Path, schema_path: Path, csv_path: Path):
    """Initializes the database by applying the schema and loading the CSV data"""
    with sqlite3.connect(db_path) as connection:
        apply_schema(connection, schema_path)
        num_rows = load_csv(connection, csv_path)
        print(f"Loaded {num_rows} rows into the database.")
        connection.commit()

    return num_rows


def main():
    parser = argparse.ArgumentParser(
        description="Load clinical trial data into a SQLite database.")
    parser.add_argument("--db_path", type=Path, default=DIR_PATH.parent /
                        "clinical_trials.db", help="Path to the SQLite database file.")
    parser.add_argument("--schema_path", type=Path, default=DIR_PATH.parent /
                        "schemas" / "schema.sql", help="Path to the SQL schema file.")
    parser.add_argument("--csv_path", type=Path, default=DIR_PATH.parent /
                        "data" / "cell-count.csv", help="Path to the CSV data file.")

    args = parser.parse_args()
    inserted_rows = init_database(
        Path(args.db_path), Path(args.schema_path), Path(args.csv_path)
    )
    print(
        f"Database initizliazed at {args.db_path} with {inserted_rows} rows inserted.")


if __name__ == "__main__":
    main()
