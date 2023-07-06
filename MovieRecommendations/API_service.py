import requests
import json
import pandas as pd
import config as config

api_key = config.API_KEY
genre_URL = "https://api.themoviedb.org/3/genre/movie/list"
discover_URL = "https://api.themoviedb.org/3/discover/movie"
movie_id_URL = "https://api.themoviedb.org/3/search/movie"

class MovieDetails:
    def __init__(self, title, genre_names, vote_average, vote_count, cast, director, duration, tmdb_id):
        self.title = title
        self.genre_names = genre_names
        self.vote_average = vote_average
        self.vote_count = vote_count
        self.cast = cast
        self.director = director
        self.duration = duration
        self.tmdb_id = tmdb_id

def get_genre_dict():
    # FETCH GENRE DICTIONARY
    params = {"api_key": api_key, "language": "en-US"}
    response = requests.get(genre_URL, params=params)
    data = json.loads(response.text)
    genres = data["genres"]
    genre_dict = {}

    # Print the list of genre names and IDs
    for genre in genres:
        genre_dict[genre['name']] = genre['id']
    
    return genre_dict

def get_movie_ID(name):

    params = {"api_key": api_key, "query": "{}".format(name)}
    response = requests.get(movie_id_URL, params=params)
    movie_data = response.json()
    if(movie_data["results"] == []):
        return None
    
    movie_id = movie_data["results"][0]["id"]

    print("Movie ID:", movie_id)
    return movie_id

# Return appropriate URL for fetching movie details
def return_details_URLs(num=550):
    movie_url = "https://api.themoviedb.org/3/movie/{}".format(num)
    credits_url = "https://api.themoviedb.org/3/movie/{}/credits".format(num)

    return movie_url, credits_url

# For each preference of user, find
# correct id and append to list
def get_genre_ids(person, dict):
    ids = ""
    pref_list = []
    for elem in person.movie_prefs:
        pref_list.append(str(dict[elem]))

    my_string = ", ".join(pref_list)
    
    return my_string

def movieId_to_tmdbId(movieId):
    links_df = pd.read_csv('data/links.csv')
    row = links_df.loc[links_df['movieId'] == movieId]
    tmdb_id = row['tmdbId'].values[0]
    return tmdb_id
     
def get_movie_details(movieId, verbose=False):
    # Convert movieId to The Movie Database ID to request info
    links_df = pd.read_csv('data/links.csv')
    row = links_df.loc[links_df['movieId'] == movieId]
    tmdb_id = row['tmdbId'].values[0]

    if(verbose):
        print("Converted movieID: {} to TMDB ID: {} ".format(movieId, tmdb_id))

    # GET data for specific movie
    params = {"api_key": api_key, "language": "en-US"}
    movie_url, credits_url = return_details_URLs(tmdb_id) # Fetch correctly formatted URL for getting details for movie 

    # Get response for both credits and movie details
    response = requests.get(movie_url, params=params)
    credits_response = requests.get(credits_url, params=params)

    data = json.loads(response.text)
    data_credits = json.loads(credits_response.text)

    # Extract the relevant information
    # Check if data has a title key, if not, return None
    if("title" in data):
        title = data["title"]
        genre_names = [genre["name"] for genre in data["genres"]]
        vote_average = data["vote_average"]
        vote_count = data["vote_count"]
        cast = [actor["name"] for actor in data_credits["cast"][:5]]
        director = next((person["name"] for person in data_credits["crew"] if person["job"] == "Director"), "Unknown")
        duration = data["runtime"]  
    else:
        print("Error, movie with MovieID: {} and TmdbId: {} not found".format(movieId, tmdb_id))
        details = MovieDetails("Unknown", [], 0, 0, [], "Unknown", 0, 0)
        return details
                            
    if(verbose):
        print(f"Title: {title}")
        print(f"Genres: {', '.join(genre_names)}")
        print(f"Vote average: {vote_average}")
        print(f"Vote count: {vote_count}")
        print(f"Director: {director}")
        print(f"Duration in minutes: {duration}")
        print(f"Main cast: {', '.join(cast)}")

    # Create MovieDetails object
    movieObj = MovieDetails(title, genre_names, vote_average, vote_count, cast, director, duration, tmdb_id)
    
    return movieObj


