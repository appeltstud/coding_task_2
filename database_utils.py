"""Provides utility functions for database operations."""

import sqlite3
import pandas as pd
import ast
import streamlit as st # Added for st.error
from app.config import DB_PATH, TABLE_NAME

def load_data_from_db():
    conn = sqlite3.connect(DB_PATH)
    query = f"SELECT * FROM {TABLE_NAME}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def update_movie_rating(movie_title, new_rating):
    """
    Updates the movie rating in the database by adding the new rating to existing ratings.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get current ratings for the movie
        cursor.execute(f"SELECT ratings FROM {TABLE_NAME} WHERE title = ?", (movie_title,))
        result = cursor.fetchone()
        
        existing_ratings = []
        if result and result[0]: # result[0] is the ratings string
            try:
                current_ratings_str = result[0]
                if isinstance(current_ratings_str, str) and current_ratings_str.strip():
                    parsed_value = ast.literal_eval(current_ratings_str)
                    if isinstance(parsed_value, list):
                        existing_ratings = parsed_value
            except (ValueError, SyntaxError):
                pass 
        
        existing_ratings.append(int(new_rating))
        
        cursor.execute(f"UPDATE {TABLE_NAME} SET ratings = ? WHERE title = ?", 
                      (str(existing_ratings), movie_title))
        conn.commit()
    except sqlite3.Error as e:
        st.error(f"Database error while updating rating for {movie_title}: {e}") # Use st.error for user feedback
        return False
    except Exception as e:
        st.error(f"An unexpected error occurred while updating rating for {movie_title}: {e}") # Use st.error
        return False
    finally:
        if 'conn' in locals() and conn:
            conn.close()
    return True
