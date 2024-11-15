import json

def load_movies():
    with open('{}/data/movies.json'.format("."), "r") as file:
        return json.load(file)["movies"]

def write_movies(movies):
    with open('{}/data/movies.json'.format("."), 'w') as f:
        json.dump({"movies": movies}, f)

# Query resolvers
def get_movies(_, info):
    return load_movies()

def movie_by_id(_, info, _id):
    movies = load_movies()
    for movie in movies:
        if str(movie['id']) == str(_id):
            return movie
    return None

def movie_by_title(_, info, _title):
    movies = load_movies()
    for movie in movies:
        if str(movie['title']) == str(_title):
            return movie
    return None

# Mutation resolvers
def add_movie(_, info, _id, _title, _director, _rating):
    movies = load_movies()    

    for movie in movies:
        if str(movie['id']) == str(_id):
            return None

    new_movie = {
        "id": _id,
        "title": _title,
        "director": _director,
        "rating": _rating
    }
    
    movies.append(new_movie)
    write_movies(movies)
    return new_movie

def update_movie_rate(_, info, _id, _rate):
    movies = load_movies()
    for movie in movies:
        if str(movie['id']) == str(_id):
            movie['rating'] = _rate
            write_movies(movies)
            return movie
    return None

def delete_movie(_, info, _id):
    movies = load_movies()
    for movie in movies:
        if str(movie['id']) == str(_id):
            movies.remove(movie)
            write_movies(movies)
            return movie
    return None