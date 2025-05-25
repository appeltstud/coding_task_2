"""Utility functions for the user interface."""

import textwrap
import ast
from config import TEXT_WRAP_WIDTH, TARGET_NUM_LINES, LINE_HEIGHT_EM, TITLE_HEIGHT_EM

def format_movie_title(title_text):
    """
    Formats a movie title to be wrapped to TEXT_WRAP_WIDTH,
    and then padded or truncated to occupy TARGET_NUM_LINES.
    Returns an HTML string with <br> for line breaks.
    """
    # Handle potential None or non-string inputs gracefully
    if not isinstance(title_text, str):
        title_text = str(title_text) # Convert to string or handle as empty

    wrapper = textwrap.TextWrapper(
        width=TEXT_WRAP_WIDTH,
        break_long_words=True,
        replace_whitespace=False,
        expand_tabs=False,
        fix_sentence_endings=False
    )
    original_lines = wrapper.wrap(text=title_text)

    if not original_lines: # Handle empty titles after wrapping
        return ("<br>" * (TARGET_NUM_LINES - 1)) if TARGET_NUM_LINES > 0 else ""

    if len(original_lines) > TARGET_NUM_LINES:
        # Truncate and add ellipsis
        processed_lines = original_lines[:TARGET_NUM_LINES]
        last_line_idx = TARGET_NUM_LINES - 1
        # Ensure last line has space for ellipsis
        if len(processed_lines[last_line_idx]) > 3:
            processed_lines[last_line_idx] = processed_lines[last_line_idx][:-3] + "..."
        elif len(processed_lines[last_line_idx]) > 0: # if line is 1,2,3 chars, replace with ...
             processed_lines[last_line_idx] = "..."
        # If last line was empty and we have more than 1 target line, put ... on previous if possible
        elif TARGET_NUM_LINES > 1 and last_line_idx > 0:
            if len(processed_lines[last_line_idx-1]) > 3:
                 processed_lines[last_line_idx-1] = processed_lines[last_line_idx-1][:-3] + "..."
                 processed_lines[last_line_idx] = "" # clear current last line
            else:
                 processed_lines[last_line_idx-1] = "..."
                 processed_lines[last_line_idx] = ""
        return "<br>".join(processed_lines)
    elif len(original_lines) < TARGET_NUM_LINES:
        # Pad with newlines
        current_text_html = "<br>".join(original_lines)
        return current_text_html + ("<br>" * (TARGET_NUM_LINES - len(original_lines)))
    else: # len(original_lines) == TARGET_NUM_LINES
        return "<br>".join(original_lines)

def generate_star_rating_html(ratings_data):
    """
    Generates an HTML string for star rating display.
    ratings_data can be a string representation of a list, an actual list, or None.
    Assumes ratings in the list are on a 1-5 scale.
    """
    ratings_list = None
    if isinstance(ratings_data, list):
        ratings_list = ratings_data
    elif isinstance(ratings_data, str):
        try:
            ratings_list = ast.literal_eval(ratings_data)
        except (ValueError, SyntaxError):
            ratings_list = None # Invalid string format

    if not isinstance(ratings_list, list) or not ratings_list:
        return "<p style='text-align: center; font-size: small; color: #888;'>No ratings available</p>"

    try:
        # Ensure all ratings are numbers, filter out non-numeric if any
        numeric_ratings = [r for r in ratings_list if isinstance(r, (int, float))]
        if not numeric_ratings:
            return "<p style='text-align: center; font-size: small; color: #888;'>No valid ratings</p>"

        avg_numeric_rating = sum(numeric_ratings) / len(numeric_ratings)
        num_total_ratings = len(numeric_ratings)

        num_filled_stars = round(avg_numeric_rating)
        num_filled_stars = max(0, min(5, int(num_filled_stars))) 
        
        num_empty_stars = 5 - num_filled_stars

        star_str = "★" * num_filled_stars + "☆" * num_empty_stars
        return f"<p style='text-align: center; font-size: small;'>{star_str}<br>({num_total_ratings} ratings)</p>"
    except Exception: 
        return "<p style='text-align: center; font-size: small; color: #888;'>Rating error</p>"
