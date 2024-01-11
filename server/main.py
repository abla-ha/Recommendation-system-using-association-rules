from fastapi import FastAPI, HTTPException
import pandas as pd
import ast
import requests
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
origins = ["http://localhost:3000"]  # Add the origin of your frontend application

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
 

# Load association rules or recommendation data from CSV
recommendation_data = pd.read_csv('Apriorii_rules.csv')

def extract_book_names(frozenset_value):
    return list(frozenset_value)

def flatten_and_remove_duplicates(nested_list):
    # Use ast.literal_eval to safely evaluate the string representation of lists
    flat_list = [item for sublist in map(ast.literal_eval, nested_list) for item in sublist]
    unique_list = []
    for item in flat_list:
        if isinstance(item, list):
            unique_list.extend(item)
        elif item not in unique_list:
            unique_list.append(item)
    return unique_list

def get_movie_image(api_key, movie_name):
    base_url = "https://api.themoviedb.org/3"
    search_endpoint = "/search/movie"

    # Parameters for the search query
    params = {
        'api_key': api_key,
        'query': movie_name
    }

    # Make the request to the TMDb API
    response = requests.get(base_url + search_endpoint, params=params)
    data = response.json()

    # Check if the request was successful
    if response.status_code == 200 and data['total_results'] > 0:
        # Get the first result (assuming it's the most relevant)
        movie = data['results'][0]

        # Get the poster path
        poster_path = movie['poster_path']

        # Generate the full URL for the image
        image_url = f"https://image.tmdb.org/t/p/w500/{poster_path}"

        return image_url

    else:
        print(f"Error: {response.status_code}")
        return None

@app.get("/")
def hello():
    return {"message": "Hello World"}

@app.get("/recommend/{book_name}")
async def get_recommendations(book_name: str):
    try:
        # Filter recommendations based on the provided book name
        recommendations = recommendation_data[recommendation_data['book_names'].apply(lambda x: book_name in x)]
        
        # Extract recommended books and use flatten_and_remove_duplicates
        nested_recommended_books = recommendations['recomendation'].tolist()
        unique_recommended_books = flatten_and_remove_duplicates(nested_recommended_books)

        return {"book_name": book_name, "unique_recommended_books": unique_recommended_books}
    except KeyError:
        raise HTTPException(status_code=404, detail="Book not found in recommendations")

@app.get("/movie/{movie_name}")
def get_movie_info(movie_name: str):
    # Replace 'YOUR_API_KEY' with your actual TMDb API key
    api_key = '3fa4d0f2e92a564e8ebbc1f21ad517f4'

    # Get the movie image URL using the get_movie_image function
    image_url = get_movie_image(api_key, movie_name)

    if image_url:
        return {"movie_name": movie_name, "image_url": image_url}
    else:
        raise HTTPException(status_code=404, detail=f"No movie found with the name: {movie_name}")
