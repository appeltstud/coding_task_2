"""Utility functions for the user interface, primarily for formatting text and ratings."""

import textwrap
import ast
import streamlit as st
from config.config import TEXT_WRAP_WIDTH, TARGET_NUM_LINES # Corrected import paths
# TITLE_HEIGHT_EM and LINE_HEIGHT_EM are not directly used in this file's functions.

def format_movie_title(title_text: str | None) -> str:
    """Formats a movie title for display.
    
    Wraps text to TEXT_WRAP_WIDTH and pads/truncates to TARGET_NUM_LINES.

    Args:
        title_text: The movie title string.

    Returns:
        An HTML string with <br> for line breaks, formatted for display.
    """
    if not isinstance(title_text, str):
        title_text = str(title_text) if title_text is not None else ""

    wrapper = textwrap.TextWrapper(
        width=TEXT_WRAP_WIDTH,
        break_long_words=True, # Consider if True is always desired
        replace_whitespace=False,
        expand_tabs=False,
        fix_sentence_endings=False # Usually False for titles
    )
    original_lines = wrapper.wrap(text=title_text)

    if not original_lines:
        return ("<br>" * (TARGET_NUM_LINES - 1)) if TARGET_NUM_LINES > 0 else ""

    if len(original_lines) > TARGET_NUM_LINES:
        processed_lines = original_lines[:TARGET_NUM_LINES]
        last_line_idx = TARGET_NUM_LINES - 1
        # Ensure last line has space for ellipsis, or replace if very short
        if len(processed_lines[last_line_idx]) > 3:
            processed_lines[last_line_idx] = processed_lines[last_line_idx][:-3] + "..."
        elif len(processed_lines[last_line_idx]) > 0 : # Line is 1-3 chars
             processed_lines[last_line_idx] = "..."
        # If last line became empty and we have previous lines, try to put ellipsis on the (now) last visible line
        elif TARGET_NUM_LINES > 1 and last_line_idx > 0:
            if len(processed_lines[last_line_idx-1]) > 3:
                 processed_lines[last_line_idx-1] = processed_lines[last_line_idx-1][:-3] + "..."
            else: # Previous line also too short, just make it ellipsis
                 processed_lines[last_line_idx-1] = "..."
            processed_lines[last_line_idx] = "" # Ensure the actual last line is empty if ellipsis moved
        return "<br>".join(line for line in processed_lines if line) # Join non-empty lines
    elif len(original_lines) < TARGET_NUM_LINES:
        current_text_html = "<br>".join(original_lines)
        return current_text_html + ("<br>" * (TARGET_NUM_LINES - len(original_lines)))
    else: # len(original_lines) == TARGET_NUM_LINES
        return "<br>".join(original_lines)

def generate_star_rating_html(ratings_data: str | list | None) -> str:
    """Generates HTML for star rating display based on average rating.

    Args:
        ratings_data: Can be a string representation of a list (e.g., "[4,5]"), 
                      an actual list of ratings [4,5], or None. 
                      Ratings are assumed to be on a 1-5 scale.

    Returns:
        An HTML string displaying stars and rating count, or a message if no ratings.
    """
    ratings_list = [] # Default to empty list
    if isinstance(ratings_data, list):
        ratings_list = ratings_data
    elif isinstance(ratings_data, str):
        try:
            evaluated_data = ast.literal_eval(ratings_data)
            if isinstance(evaluated_data, list):
                ratings_list = evaluated_data
            # elif isinstance(evaluated_data, (int, float)): # If string was a single number e.g. "'4'"
                # ratings_list = [evaluated_data]
        except (ValueError, SyntaxError):
            # Could be a simple string not meant to be a list, or malformed
            # print(f"Could not parse ratings_data string: {ratings_data}") # Optional logging
            pass # Keep ratings_list empty

    if not ratings_list or not all(isinstance(r, (int, float)) for r in ratings_list):
        # Fallback for empty list or list with non-numeric items after parsing
        # Check if it was a single number string that didn't get converted to list by ast.literal_eval
        if isinstance(ratings_data, str) and ratings_data.isdigit():
             try:
                 ratings_list = [int(ratings_data)]
             except ValueError:
                 return "<p style='text-align: center; font-size: small; color: #888;'>No ratings available<br>&nbsp;</p>" # Adding space for alignment
        else:
            return "<p style='text-align: center; font-size: small; color: #888;'>No ratings available<br>&nbsp;</p>"


    try:
        numeric_ratings = [r for r in ratings_list if isinstance(r, (int, float))]
        if not numeric_ratings: # Should be caught above, but as a safeguard
            return "<p style='text-align: center; font-size: small; color: #888;'>No valid ratings<br>&nbsp;</p>"

        avg_numeric_rating = sum(numeric_ratings) / len(numeric_ratings)
        num_total_ratings = len(numeric_ratings)

        # Round to nearest star, ensuring it's within 0-5 range
        num_filled_stars = max(0, min(5, round(avg_numeric_rating)))
        num_empty_stars = 5 - num_filled_stars

        star_str = "★" * num_filled_stars + "☆" * num_empty_stars
        return f"<p style='text-align: center; font-size: small;'>{star_str}<br>({num_total_ratings} ratings)</p>"
    except Exception as e: 
        # print(f"Error generating star rating HTML: {e}") # Optional logging
        return "<p style='text-align: center; font-size: small; color: #888;'>Rating display error<br>&nbsp;</p>"
