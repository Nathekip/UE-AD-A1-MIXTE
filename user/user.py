# REST API
from flask import Flask, render_template, request, jsonify, make_response
import requests
import json
from werkzeug.exceptions import NotFound

# CALLING gRPC requests
import grpc
from concurrent import futures
import booking_pb2
import booking_pb2_grpc
import os

# CALLING GraphQL requests
# todo to complete

app = Flask(__name__)

PORT_BOOKING = 3302
PORT_SHOWTIME = 3304
PORT_MOVIE = 3300
IP = '127.0.0.1'
PORT = 3303
HOST = '0.0.0.0'

base_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(base_dir, 'data/users.json')

with open(json_path, "r") as jsf:
   users = json.load(jsf)["users"]

@app.route("/", methods=['GET'])
def home():
   """
   Page d'accueil
   """
   return "<h1 style='color:blue'>Welcome to the User service!</h1>"

@app.route("/users",methods=['GET'])
def get_json():
    """
    Retourne la liste des utilisateurs
    """
    res = make_response(jsonify(users),200)
    return res
 
@app.route("/users", methods=['POST'])
def add_user():
    """ 
    Ajouter un utilisateur
    """
    new_user = request.get_json()
    users.append(new_user)
    with open(json_path, "w") as jsf:
        json.dump({"users": users}, jsf, indent=2)
    return make_response(jsonify(new_user), 201)
 
@app.route("/users/<user_id>", methods=['DELETE'])
def delete_user(user_id):
    """ 
    Supprimer un utilisateur
    """
    for user in users:
        if user["id"] == user_id:
            users.remove(user)
            with open(json_path, "w") as jsf:
                json.dump({"users": users}, jsf, indent=2)
            return make_response(jsonify({"message": "user deleted"}), 200)
    return make_response(jsonify({"error": "user not found"}), 404)
 
@app.route("/users/<user_id>/bookings", methods=['POST'])
def add_booking_for_user(user_id):
   """
   Ajouter une réservation pour un utilisateur
   """
   booking_data = request.get_json()
   date_request = booking_data["date"]
   movie_request = booking_data["movieid"]
   try:
      # Requête AddBooking pour le service grpc Booking
      AddBooking = booking_pb2.AddBooking(userid=user_id,date=date_request,movies=movie_request)
      with grpc.insecure_channel('localhost:3302') as channel:
         stub = booking_pb2_grpc.BookingStub(channel)
         # Appele la méthode AddBookings du service Booking
         bookings_reponse = stub.AddBookings(AddBooking)
         if not bookings_reponse.datemovies:
            return make_response({"error": "no data found in response"}, 400)
         bookings = [
                {
                    "date": date_movie.date,
                    "movies": list(date_movie.movies) 
                }
                for date_movie in bookings_reponse.datemovies
            ]
         return make_response(jsonify({"bookings": bookings}), 200)
   except grpc.RpcError as e:
      print(e)
      return make_response({"error": "could not add booking"}, 400)

@app.route("/users/bookings/<user>",methods=['GET'])
def get_bookings_byuser(user):
   """ 
   Retourne les réservations d'un utilisateur
   """
   id = -1
   for useri in users :
      if useri["name"] == user or useri["id"] == user :
         id = useri["id"]
         break
   if id == -1 :
      return make_response(jsonify({"error":"user not found"}), 400)
   try:
      # Requête UserID pour le service grpc Booking
      UserID = booking_pb2.UserID(userid=id)
      with grpc.insecure_channel('localhost:3302') as channel:
         stub = booking_pb2_grpc.BookingStub(channel)
         # Appele la méthode GetBookingsByUserId de Booking
         bookings_reponse = stub.GetBookingsByUserId(UserID)
         bookings = [
                {
                    "date": date_movie.date,
                    "movies": list(date_movie.movies)  
                }
                for date_movie in bookings_reponse.datemovies
            ]
         print(bookings)
         return make_response(jsonify({"bookings": bookings}), 200)
   except grpc.RpcError as e:
      print(f"Erreur : {e}")
      return make_response({"error":"no bookings for this user"}, 400)
   

@app.route("/users/movies/<user>", methods=['GET'])
def get_movies_byuser(user):
    """
    Retourne les films réservés par un utilisateur
    """
    id = -1
    # Trouver l'utilisateur par nom ou ID
    for useri in users:
        if useri["name"] == user or useri["id"] == user:
            id = useri["id"]
            break
    if id == -1:
        return make_response(jsonify({"error": "user not found"}), 400)
    
    try:
        # Requête UserID pour le service grpc Booking
        UserID = booking_pb2.UserID(userid=id)
        with grpc.insecure_channel('localhost:3302') as channel:
            stub = booking_pb2_grpc.BookingStub(channel)
            # Appele la méthode GetBookingsByUserId de Booking
            bookings_response = stub.GetBookingsByUserId(UserID)
            if not bookings_response.datemovies:
                return make_response({"error": "no bookings for this user"}, 400)
            
            movies_json = {"movies": []}
            for date_movie in bookings_response.datemovies:
                for movie in date_movie.movies:
                    #Construction de la requête GraphQL pour avoir les informations du film
                    query = f"""
                    query {{
                        movie_by_id(_id: "{movie}") {{
                            id
                            title
                            director
                            rating
                        }}
                    }}
                    """
                    # Envoyer la requête GraphQL au service Movie
                    movie_response = requests.post(f"http://{IP}:{PORT_MOVIE}/graphql", json={'query': query})
                    movie_data = movie_response.json().get('data', {}).get('movie_by_id', {})
                    if movie_data:
                        movies_json["movies"].append(movie_data)
            
            return make_response(jsonify(movies_json), 200)
    except grpc.RpcError as e:
        print(f"Erreur : {e}")
        return make_response({"error": "could not retrieve bookings"}, 400)

def run():
   print("--------------AddBookings--------------")

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)