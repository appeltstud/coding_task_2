"""Utility functions for database operations."""

import sqlite3
import pandas as pd
import ast
import streamlit as st 
from config.config import DB_PATH, TABLE_NAME

def parse_ratings_column(value: str | list | None) -> list:
    """Converts a database value (string or list) into a list of ratings.

    Args:
        value: The value from the 'ratings' column. Can be None, a list, 
               or a string representation of a list or a single rating.

    Returns:
        A list of ratings. Returns an empty list if input is None or parsing fails.
    """
    if pd.isna(value):
        return []
    if isinstance(value, list):
        return value
    
    try:
        evaluated = ast.literal_eval(str(value))
        if isinstance(evaluated, list):
            return evaluated
        else:
            return [evaluated]
    except (ValueError, SyntaxError):
        return [value] if value else []


def load_data_from_db() -> pd.DataFrame:
    """Loads movie data from the SQLite database.
    
    Parses the 'ratings' column into lists of numbers.

    Returns:
        A pandas DataFrame with movie data.
    """
    conn = sqlite3.connect(DB_PATH)
    query = f"SELECT * FROM {TABLE_NAME}"
    df = pd.read_sql_query(query, conn)
    conn.close()

    if 'ratings' in df.columns:
        df['ratings'] = df['ratings'].apply(parse_ratings_column)
    else:
        df['ratings'] = [[] for _ in range(len(df))] # Initialize if 'ratings' column is missing
        
    return df


def update_ratings(movie_id_str: str, rating: int) -> None:
    df = load_data_from_db() 
