"""Provides utility functions for database operations."""

import sqlite3
import pandas as pd
import ast
import streamlit as st # Added for st.error
from config import DB_PATH, TABLE_NAME

def load_data_from_db():
    """Loads data from the SQLite database."""
   # print("run data")
    conn = sqlite3.connect(DB_PATH)
    query = f"SELECT * FROM {TABLE_NAME}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    st.write(df.loc[df["movie_id"] == 440])  # Display the first few rows of the DataFrame in Streamlit
    return df


def update_ratings(id: str, rating: int):
  #  print("run my friend")
    st.write("rating:", rating)
    st.write("title:", id)
    df = load_data_from_db()

    df.loc[df.movie_id == id, "ratings"] = (
        df.loc[df.movie_id == id, "ratings"]
            .apply(lambda x: ([] if pd.isna(x) else (x if isinstance(x, list) else [x])) + [rating])
        )
    st.write("updated ratings")
    st.write(df.loc[df["movie_id"] == 440])  

    conn = sqlite3.connect(DB_PATH)
    df.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
