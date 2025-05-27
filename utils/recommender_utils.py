"""Utility functions for the movie recommendation engine."""

import pandas as pd
from api.api_utils import fetch_poster 
from config.config import API_KEY_AUTH 

def get_titles(df_movies: pd.DataFrame) -> list:
    """Extracts movie titles from the DataFrame.

    Args:
        df_movies: DataFrame containing movie data with a 'title' column.

    Returns:
        A list of movie titles. Returns an empty list if input is None or 'title' column is missing.
    """
    if df_movies is not None and 'title' in df_movies.columns:
        return df_movies['title'].values.tolist() # Ensure it's a list
    return []

def get_movie_data(df_movies: pd.DataFrame, movie_title: str) -> pd.Series | None:
    """Retrieves the data row for a specific movie title.

    Args:
        df_movies: DataFrame containing movie data.
        movie_title: The title of the movie to find.

    Returns:
        A pandas Series containing the movie's data if found, otherwise None.
    """
    if df_movies is not None and movie_title:
        movie_row = df_movies[df_movies['title'] == movie_title]
        if not movie_row.empty:
            return movie_row.iloc[0] # Return as Series
    return None

def recommender(movie_title: str, df_movies: pd.DataFrame, similarity_matrix) -> tuple[list, list, list]:
    """Recommends movies similar to the given movie title.

    Args:
        movie_title: The title of the movie to base recommendations on.
        df_movies: DataFrame containing all movie data.
        similarity_matrix: Precomputed cosine similarity matrix.

    Returns:
        A tuple containing three lists:
        - recommended_movie_names: Titles of recommended movies.
        - recommended_movie_posters: URLs of posters for recommended movies.
        - recommended_movie_ids: IDs of recommended movies.
        Returns empty lists if inputs are invalid or movie is not found.
    """
    if df_movies is None or movie_title is None or similarity_matrix is None:
        return [], [], []
        
    try:
        if movie_title not in df_movies['title'].values:
            return [], [], [] 

        movie_index = df_movies[df_movies['title'] == movie_title].index[0]
    except IndexError:
        return [], [], []
        
    distances = similarity_matrix[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:16]
    
    recommended_movies = []
    recommended_movie_posters = []
    recommended_movie_ids = []
    
    for i_movie_info in movies_list:
        idx = i_movie_info[0]
        if idx < len(df_movies):
            movie_data = df_movies.iloc[idx]
            movie_id = movie_data.get('movie_id')
            current_movie_title = movie_data.get('title')

            if current_movie_title: 
                recommended_movies.append(current_movie_title)
                recommended_movie_ids.append(movie_id if pd.notna(movie_id) else None)
                
                if movie_id and pd.notna(movie_id):
                    poster_url = fetch_poster(int(movie_id), API_KEY_AUTH)
                    recommended_movie_posters.append(poster_url)
                else:
                    recommended_movie_posters.append(None)
        
    return recommended_movies, recommended_movie_posters, recommended_movie_ids

