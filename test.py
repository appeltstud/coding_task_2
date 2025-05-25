import pandas as pd
import random

# Load the dataframe
# This assumes data.csv is in the same directory as test.py
df = pd.read_csv("data.csv")

# Function to generate a list of random ratings
def generate_random_ratings_list():
    # Determine a random number of ratings for this row (between 1 and 100)
    num_ratings = random.randint(0, 3)
    # Generate that many ratings, each being an integer 1 or 2
    ratings_list = [random.randint(1, 5) for _ in range(num_ratings)]
    return ratings_list

# Add the new 'ratings' column to the DataFrame
# Apply the function to each row (axis=1) to generate the list of ratings
df['ratings'] = df.apply(lambda row: generate_random_ratings_list(), axis=1)

# You can print the first few rows to see the result
print("First 5 rows of the DataFrame with the new 'ratings' column:")
print(df.head())

# If you want to save the modified DataFrame to a new CSV file, you can uncomment the following lines:
df.to_csv("data_with_ratings.csv", index=False)
# print("\nModified DataFrame saved to data_with_ratings.csv")
