import sqlite3
import tempfile
import unittest
from pathlib import Path

from load_data import initialize_database


class LoadDataTests(unittest.TestCase):
    def test_initialize_database_creates_table_and_loads_rows(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        schema_path = repo_root / "schema.sql"
        csv_path = repo_root / "clinical_trial_data.csv"

        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "clinical_trial.db"
            inserted_rows = initialize_database(db_path, schema_path, csv_path)

            self.assertTrue(db_path.exists())
            self.assertEqual(inserted_rows, 5)

            with sqlite3.connect(db_path) as connection:
                count = connection.execute(
                    "SELECT COUNT(*) FROM clinical_trial_observations"
                ).fetchone()[0]
                first_row = connection.execute(
                    """
                    SELECT participant_id, trial_arm, immune_cell_type
                    FROM clinical_trial_observations
                    ORDER BY observation_id
                    LIMIT 1
                    """
                ).fetchone()

            self.assertEqual(count, 5)
            self.assertEqual(first_row, ("P001", "Treatment", "CD4_T_Cell"))


if __name__ == "__main__":
    unittest.main()
