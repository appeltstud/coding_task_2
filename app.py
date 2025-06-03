"""Main application file for the movie recommender system."""

import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Import functions and constants from utility files
from config.config import TITLE_HEIGHT_EM
from utils.database_utils import load_data_from_db, update_ratings
from utils.ui_utils import format_movie_title, generate_star_rating_html
from utils.recommender_utils import recommender, get_titles, get_movie_data

st.set_page_config(layout="wide")


# Process ratings from session state
data = st.session_state
for id, rating in data.items():
    # rating need to be increased by 1 to match the database logic
    update_ratings(id, rating)

df = load_data_from_db()
titles = get_titles(df)

# Initialize CountVectorizer and compute similarity matrix
cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(df['tags']).toarray()
similarity = cosine_similarity(vectors)

# Hide Streamlit's default UI elements
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
    with st.form(key='rating_form'):
        with st.spinner('Loading recommendations...'):
            recommended_movie_names, recommended_movie_posters, recommended_movie_ids = recommender(selected_movie, df, similarity)

            num_recommendations = len(recommended_movie_names)
            num_rows = (num_recommendations + 4) // 5

            for row_index in range(num_rows):
                cols = st.columns(5)
                for col_index in range(5):
                    recommendation_index = row_index * 5 + col_index
                    if recommendation_index < num_recommendations:
                        with cols[col_index]:
                            movie_title_for_display = recommended_movie_names[recommendation_index]
                            movie_id_for_display = recommended_movie_ids[recommendation_index]
                            
                            st.markdown(
                                f"""<h6 style='text-align: center; height: {TITLE_HEIGHT_EM}em; display: flex; flex-direction: column; justify-content: center; overflow-y: hidden;'>
                                    <div style='max-height: 100%; overflow-y: auto;'>
                                        {format_movie_title(movie_title_for_display)} 
                                    </div>
                                </h6>""",
                                unsafe_allow_html=True
                            )
                            
                            if recommended_movie_posters[recommendation_index]:
                                st.image(recommended_movie_posters[recommendation_index], use_container_width=True)
                            else:
                                st.caption("Poster not available")
                            
                            movie_data_row = get_movie_data(df, movie_title_for_display)
                            
                            rating_value_for_html = None
                            if movie_data_row is not None: # movie_data_row is a Series
                                # Check if 'ratings' is in the Series index and the list of ratings is not empty
                                if 'ratings' in movie_data_row.index and movie_data_row['ratings']:
                                    rating_value_for_html = movie_data_row['ratings'] # Pass the entire list of ratings
                            
                            rating_display_html = generate_star_rating_html(rating_value_for_html)
                            st.markdown(rating_display_html, unsafe_allow_html=True)

                            st.markdown(
                                "<p style='text-align: center; font-size: 0.8em;margin: 0;'>Give Feedback</p>",
                                unsafe_allow_html=True,
                            )
                            st.feedback( 
                                options="stars",
                                key=str(movie_id_for_display), 
                            )
                    else:
                        with cols[col_index]:
                            st.empty()

                    st.write("")
               

        submitted = st.form_submit_button(label="Save", help="Submit your ratings for the recommended movies.")
