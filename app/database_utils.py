"""Provides utility functions for database operations."""

import sqlite3
import pandas as pd
import ast
import streamlit as st # Added for st.error
from config import DB_PATH, TABLE_NAME

def load_data_from_db():
    """Loads data from the SQLite database."""
    print("run data")
    conn = sqlite3.connect(DB_PATH)
    query = f"SELECT * FROM {TABLE_NAME}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def update_ratings(title: str, new_rating: int):
    print("run")
    import sqlite3, json
    with sqlite3.connect(DB_PATH) as con:
        cur = con.execute(f"SELECT ratings FROM {TABLE_NAME} WHERE title=?", (title,))
        ratings = json.loads(cur.fetchone()[0])          # -> list[int]
        ratings.append(new_rating)                       # list erweitern
        con.execute(f"UPDATE {TABLE_NAME} SET ratings=? WHERE title=?",
                    (json.dumps(ratings), title))
        con.commit()
