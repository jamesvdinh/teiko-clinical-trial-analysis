import sqlite3
from pathlib import Path

DIR_PATH = Path(__file__).resolve().parent
DB_PATH = DIR_PATH.parent / "clinical_trials.db"


def run_query(query: str, params: tuple = ()):
    """Helper function to open a connection, run a query, and print results neatly."""
    if not DB_PATH.exists():
        print(f"Error: Database not found at {DB_PATH}")
        return

    with sqlite3.connect(DB_PATH) as connection:
        # This row factory lets you access columns by name (e.g., row['age']) instead of just index
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        try:
            cursor.execute(query, params)
            rows = cursor.fetchall()

            if not rows:
                print("No results returned.")
                return

            headers = rows[0].keys()
            print(" | ".join(headers))
            print("-" * (len(" | ".join(headers)) + 5))

            for row in rows:
                print(" | ".join(str(row[key]) for key in headers))

        except sqlite3.Error as e:
            print(f"SQL Error encountered: {e}")


def parse_query(path: Path):
    """Helper function to read an SQL file and extract text"""
    return path.read_text()


"""
QUERIES
"""
QUERY_PATH = DIR_PATH.parent / "sql"
cell_type_frequency_query = parse_query(QUERY_PATH / "cell_type_frequency.sql")


def main():
    print(f"Database: {DB_PATH.resolve()}")

    run_query(cell_type_frequency_query)


if __name__ == "__main__":
    main()
