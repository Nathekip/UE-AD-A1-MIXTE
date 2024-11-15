from flask import Flask, request, jsonify, make_response
from ariadne import graphql_sync, make_executable_schema, load_schema_from_path, ObjectType, QueryType, MutationType
import resolvers as r

app = Flask(__name__)

PORT = 3200
HOST = '0.0.0.0'

# Create type definitions
type_defs = load_schema_from_path('movie.graphql')

# Create types
query = QueryType()
mutation = MutationType()
movie = ObjectType('Movie')

# Bind resolvers to fields
query.set_field('movies', r.get_movies)
query.set_field('movie_by_id', r.movie_by_id)
query.set_field('movie_by_title', r.movie_by_title)

mutation.set_field('add_movie', r.add_movie)
mutation.set_field('update_movie_rate', r.update_movie_rate)
mutation.set_field('delete_movie', r.delete_movie)

# Create executable schema
schema = make_executable_schema(type_defs, query, mutation, movie)

# Root message
@app.route("/", methods=['GET'])
def home():
    return make_response("<h1 style='color:blue'>Welcome to the Movie service!</h1>",200)

# GraphQL endpoint
@app.route('/graphql', methods=['POST'])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=None,
        debug=app.debug
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code

if __name__ == "__main__":
    print("Server running in port %s"%(PORT))
    app.run(host=HOST, port=PORT)