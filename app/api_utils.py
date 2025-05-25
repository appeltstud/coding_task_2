"""Provides utility functions for interacting with an external API."""

import requests
import streamlit as st

def fetch_poster(movie_id, api_key):
    """
    Fetches the movie poster path from TMDB API.
    Requires movie_id and the API key.
    """
    if not movie_id or not api_key:
        return None
    try:
        response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}')
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)
        data = response.json()
        
        poster_path = data.get('poster_path')
        if poster_path:
            full_path = 'https://image.tmdb.org/t/p/w500/' + poster_path
            return full_path
        else:
            return None # Poster path not found in API response
    except requests.exceptions.RequestException as e:
        # Log error or handle it as per application's requirement
        print(f"API request failed: {e}")
        return None
    except KeyError:
        # Log error: poster_path key missing from response
        print(f"Invalid API response format for movie_id {movie_id}")
        return None



