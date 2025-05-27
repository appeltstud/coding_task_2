"""Converts CSV data to an SQLite database."""

import pandas as pd
import sqlite3

# Define paths
CSV_FILE_PATH = "data/data_with_ratings.csv"  # Adjusted path
DB_FILE_PATH = "data/movies.db"  # Adjusted path
TABLE_NAME = "movies"

def create_sqlite_from_csv():
    """
    Reads data from a CSV file and stores it in an SQLite database table.
    """
    try:
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(CSV_FILE_PATH)

        # Connect to SQLite database (it will be created if it doesn't exist)
        conn = sqlite3.connect(DB_FILE_PATH)
        cursor = conn.cursor()

        # Write the data to a new SQLite table
        # The 'if_exists="replace"' option will drop the table first if it already exists.
        # Use 'if_exists="append"' if you want to add data to an existing table.
        df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)

        print(f"Successfully created database '{DB_FILE_PATH}' and table '{TABLE_NAME}'.")
        print(f"Table '{TABLE_NAME}' contains {len(df)} rows.")

        # Verify by fetching a few rows
        cursor.execute(f"SELECT * FROM {TABLE_NAME} LIMIT 5")
        rows = cursor.fetchall()
        print("\nFirst 5 rows from the table:")
        for row in rows:
            print(row)

    except FileNotFoundError:
        print(f"Error: The file '{CSV_FILE_PATH}' was not found.")
    except pd.errors.EmptyDataError:
        print(f"Error: The file '{CSV_FILE_PATH}' is empty.")
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    create_sqlite_from_csv()
