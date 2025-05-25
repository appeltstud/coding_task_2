"""Main application file for the movie recommender system."""

import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Import functions and constants from utility files
from config import DB_PATH, TABLE_NAME, API_KEY_AUTH, TEXT_WRAP_WIDTH, TARGET_NUM_LINES, LINE_HEIGHT_EM, TITLE_HEIGHT_EM
from database_utils import load_data_from_db, update_ratings
from ui_utils import format_movie_title, generate_star_rating_html
from api_utils import fetch_poster
from recommender_utils import recommender, get_titles, get_movie_data

df = load_data_from_db()
titles = get_titles(df) # Pass df

# Initialize CountVectorizer and compute similarity matrix
# This part remains in app.py as it's specific to the main app logic
cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(df['tags']).toarray()
similarity = cosine_similarity(vectors)


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
    df = load_data_from_db()
    with st.spinner('Loading recommendations...'):
        # Pass df and similarity to the recommender function
        recommended_movie_names, recommended_movie_posters = recommender(selected_movie, df, similarity)

        num_recommendations = len(recommended_movie_names)
        num_rows = (num_recommendations + 4) // 5

        for row_index in range(num_rows):
            cols = st.columns(5)
            for col_index in range(5):
                recommendation_index = row_index * 5 + col_index
                if recommendation_index < num_recommendations:
                    with cols[col_index]:
                        movie_title_for_display = recommended_movie_names[recommendation_index]
                        
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
                        
                        # Display star ratings
                        # Fetch the specific movie's data row
                        movie_data_row = get_movie_data(df, movie_title_for_display)
                        
                        rating_value_for_html = None
                        if movie_data_row is not None and not movie_data_row.empty:
                            if 'ratings' in movie_data_row.columns and pd.notna(movie_data_row['ratings'].iloc[0]):
                                rating_value_for_html = movie_data_row['ratings'].iloc[0]
                        
                        rating_display_html = generate_star_rating_html(rating_value_for_html)
                        st.markdown(rating_display_html, unsafe_allow_html=True)

                        feedback_key = f"rating_{row_index}_{col_index}_{recommendation_index}_{movie_title_for_display.replace(' ', '_')}"
                        
                        with st.form(key=f"form_for_{feedback_key}"):
                            user_rating_input = st.feedback( 
                                options="stars",
                                key=feedback_key,
                            )
                            submitted = st.form_submit_button("Rate")

                        if submitted:
                            if user_rating_input is not None:
                                st.write("")
                                update_ratings(new_rating=user_rating_input, title=recommendation_index)
                else:
                    with cols[col_index]:
                        st.empty() # Fill empty columns to maintain layout