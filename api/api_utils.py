"""Utility functions for interacting with external APIs (e.g., TMDB)."""

import requests

def fetch_poster(movie_id: int, api_key: str) -> str | None:
    """Fetches the movie poster URL from TMDB API.

    Args:
        movie_id: The Movie Database (TMDB) ID for the movie.
        api_key: The API key for TMDB.

    Returns:
        The full URL to the movie poster image, or None if an error occurs or poster is not found.
    """

    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}')
    response.raise_for_status() 
    data = response.json()
    
    poster_path = data.get('poster_path')
    full_path = 'https://image.tmdb.org/t/p/w500/' + poster_path
    return full_path




