"""Contains utility functions for the recommendation engine."""

import pandas as pd
from api_utils import fetch_poster
from config import API_KEY_AUTH # Ensure API_KEY_AUTH is imported if fetch_poster needs it directly or is refactored

def get_titles(df_movies):
    """Returns the list of movie titles from the DataFrame."""
    if df_movies is not None and 'title' in df_movies.columns:
        return df_movies['title'].values
    return []

def get_movie_data(df_movies, movie_title):
    """Returns the DataFrame row for a specific movie title."""
    if df_movies is not None and movie_title:
        movie_row = df_movies[df_movies['title'] == movie_title]
        if not movie_row.empty:
            return movie_row # Return the DataFrame row (or Series if .iloc[0] is used by caller)
    return None

def recommender(movie_title, df_movies, similarity_matrix):
    """
    Recommends movies similar to the given movie title.
    Requires the main DataFrame and the precomputed similarity matrix.
    Returns a list of recommended movie titles and their posters.
    """
    if df_movies is None or movie_title is None or similarity_matrix is None:
        return [], []
        
    try:
        # Check if movie_title exists in the DataFrame
        if movie_title not in df_movies['title'].values:
            # st.error(f"Movie '{movie_title}' not found in the database.") # Consider logging or specific UI feedback
            return [], [] # Movie not found

        movie_index = df_movies[df_movies['title'] == movie_title].index[0]
    except IndexError:
        # This case should ideally be caught by the check above, but as a fallback:
        return [], []
        
    distances = similarity_matrix[movie_index]
    # Get top 20 similar movies (excluding the movie itself, hence [1:21])
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:21]
    
    recommended_movies = []
    recommended_movie_posters = []
    
    for i_movie_info in movies_list:
        idx = i_movie_info[0]
        # Ensure index is within bounds of the DataFrame
        if idx < len(df_movies):
            movie_id = df_movies.iloc[idx].get('movie_id')
            current_movie_title = df_movies.iloc[idx].get('title')

            if current_movie_title: # Ensure title is not None
                recommended_movies.append(current_movie_title)
                if movie_id and pd.notna(movie_id): # Check for NaN movie_id
                    # Pass API_KEY_AUTH to fetch_poster if it's not globally configured there
                    recommended_movie_posters.append(fetch_poster(int(movie_id), API_KEY_AUTH))
                else:
                    recommended_movie_posters.append(None) # No movie_id, no poster
            # If title is None, we skip adding this movie to recommendations.
        
    return recommended_movies, recommended_movie_posters

