import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import requests
import textwrap # Added import

# df = pickle.load(open('movies.pkl', 'rb'))
df = pd.read_csv('data.csv')
titles = df['title'].values
cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(df['tags']).toarray()
similarity = cosine_similarity(vectors)
# similarity = pickle.load(open('similarity.pkl', 'rb'))

API_KEY_AUTH = "b8c96e534866701532768a313b978c8b"

# Constants for text formatting
TEXT_WRAP_WIDTH = 25  # Adjust as needed based on visual output in columns
TARGET_NUM_LINES = 3  # Target number of lines for each title display
# Estimate line height for h5, adjust as needed.
LINE_HEIGHT_EM = 1.5 # For h5, a common line height is around 1.2 to 1.5
TITLE_HEIGHT_EM = TARGET_NUM_LINES * LINE_HEIGHT_EM


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
        # Add <br> tags to make up the difference to TARGET_NUM_LINES
        # Each <br> effectively adds one line.
        # If 1 line and target is 3, need 2 <br> to make it "Line1<br><br>" (3 lines total)
        return current_text_html + ("<br>" * (TARGET_NUM_LINES - len(original_lines)))
    else: # len(original_lines) == TARGET_NUM_LINES
        return "<br>".join(original_lines)


def fetch_poster(movie_id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY_AUTH}')
    data = response.json()
    poster_path = data['poster_path']
    full_path = 'https://image.tmdb.org/t/p/w500/' + poster_path
    return full_path


def recommender(movie):
    movie_index = df[df['title'] == movie].index[0]
    distance = similarity[movie_index]
    movies_list = sorted(list(enumerate(distance)), reverse=True, key=lambda x: x[1])[1:21]
    movie_recommend = []
    movie_recommend_posters = []
    for i in movies_list:
        movie_id = df.iloc[i[0]]['movie_id']
        movie_recommend.append(df.iloc[i[0]]['title'])
        movie_recommend_posters.append(fetch_poster(movie_id))

    return movie_recommend, movie_recommend_posters


st.set_page_config(layout="wide")
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
hide_decoration_bar_style = '''
    <style>
        header {visibility: hidden;}
    </style>
'''
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)


st.title('CINEPHILE ENGINE')
selected_movie = st.selectbox('Type a Movie', options=titles)
if st.button('Recommend'):
    with st.spinner('Loading recommendations...'):
        recommended_movie_names, recommended_movie_posters = recommender(selected_movie)

        # Calculate the number of rows needed for 20 items, 5 per row
        num_recommendations = len(recommended_movie_names)
        num_rows = (num_recommendations + 4) // 5 # Ceiling division

        for row_index in range(num_rows):
            cols = st.columns(5)
            for col_index in range(5):
                recommendation_index = row_index * 5 + col_index
                if recommendation_index < num_recommendations:
                    with cols[col_index]:
                        # Display title with larger font and fixed height
                        st.markdown(
                            f"""<h6 style='text-align: center; height: {TITLE_HEIGHT_EM}em; display: flex; flex-direction: column; justify-content: center; overflow-y: hidden;'>
                                <div style='max-height: 100%; overflow-y: auto;'>
                                    {format_movie_title(recommended_movie_names[recommendation_index])}
                                </div>
                            </h6>""",
                            unsafe_allow_html=True
                        )
                        # Display poster, filling column width
                        if recommended_movie_posters[recommendation_index]:
                             st.image(recommended_movie_posters[recommendation_index], use_column_width='always')
                        else:
                             st.caption("Poster not available") # Placeholder if poster is missing
                             st.write("")
                else:
                    with cols[col_index]:
                        st.write("") # Empty column if no more recommendations