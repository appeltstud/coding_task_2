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
    """Updates the rating for a movie in the database.

    Args:
        movie_id_str: The ID of the movie (as a string, will be converted to int).
        rating: The new rating to add.
    """
    df = load_data_from_db() 

    try:
        movie_id_int = int(movie_id_str)
    except ValueError:
        st.error(f"Invalid movie_id: {movie_id_str}. It must be an integer.")
        return

    movie_exists = df["movie_id"] == movie_id_int
    if not movie_exists.any():
        st.error(f"Movie with id {movie_id_int} not found in the database.")
        return

    current_ratings = df.loc[movie_exists, "ratings"].iloc[0]
    if not isinstance(current_ratings, list): # Should already be a list from parse_ratings_column
        current_ratings = [] 

    new_ratings = current_ratings + [rating]
    # Update the DataFrame; ensure the new_ratings is treated as a single list element for the cell
    df.loc[movie_exists, "ratings"] = pd.Series([new_ratings], index=df[movie_exists].index)

    # Prepare DataFrame for saving: convert list-like 'ratings' to string
    df_to_save = df.copy()
    # Convert list of ratings to string representation for SQLite storage
    df_to_save['ratings'] = df_to_save['ratings'].apply(lambda x: str(x) if isinstance(x, list) else x)

    conn = sqlite3.connect(DB_PATH)
    try:
        df_to_save.to_sql(TABLE_NAME, conn, if_exists="replace", index=False)
        # st.write("Successfully saved updated ratings to database.") # Optional: success message
    except Exception as e:
        st.error(f"Error saving to database: {e}")
    finally:
        conn.close()
