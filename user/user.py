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
#import movie_pb2
#import movie_pb2_grpc

# CALLING GraphQL requests
# todo to complete

app = Flask(__name__)

PORT_BOOKING = 3102
PORT_SHOWTIME = 3202
PORT_MOVIE = 3200
IP = '127.0.0.1'
PORT = 3203
HOST = '0.0.0.0'

with open('{}/user/data/users.json'.format("."), "r") as jsf:
   users = json.load(jsf)["users"]

@app.route("/", methods=['GET'])
def home():
   return "<h1 style='color:blue'>Welcome to the User service!</h1>"

@app.route("/users",methods=['GET'])
def get_json():
    res = make_response(jsonify(users),200)
    return res
 
@app.route("/users", methods=['POST'])
def add_user():
    new_user = request.get_json()
    users.append(new_user)
    with open('{}/user/data/users.json'.format("."), "w") as jsf:
        json.dump({"users": users}, jsf, indent=2)
    return make_response(jsonify(new_user), 201)
 
@app.route("/users/<user_id>", methods=['DELETE'])
def delete_user(user_id):
    for user in users:
        if user["id"] == user_id:
            users.remove(user)
            with open('{}/user/data/users.json'.format("."), "w") as jsf:
                json.dump({"users": users}, jsf, indent=2)
            return make_response(jsonify({"message": "user deleted"}), 200)
    return make_response(jsonify({"error": "user not found"}), 404)
 
@app.route("/users/<user_id>/bookings", methods=['POST'])
def add_booking_for_user(user_id):
   booking_data = request.get_json()
   date_request = booking_data["date"]
   movie_request = booking_data["movie_id"]
   try:
      AddBooking = booking_pb2.AddBooking(userid=user_id,date=date_request,movies=movie_request)
      with grpc.insecure_channel('localhost:3102') as channel:
         stub = booking_pb2_grpc.BookingStub(channel)
         bookings_reponse = stub.AddBookings(AddBooking)
         bookings = [
                {
                    "date": date_movie.date,
                    "movies": list(date_movie.movies)  # Convert the repeated field to a Python list
                }
                for date_movie in bookings_reponse.datemovies
            ]
         print(bookings)
         return make_response(jsonify({"bookings": bookings}), 200)
   except grpc.RpcError as e:
      print(e) 
      return make_response({"error": "could not add booking"}, 400)

@app.route("/users/bookings/<user>",methods=['GET'])
def get_bookings_byuser(user):
   id = -1
   for useri in users :
      if useri["name"] == user or useri["id"] == user :
         id = useri["id"]
         break
   if id == -1 :
      return make_response(jsonify({"error":"user not found"}), 400)
   try:
      UserID = booking_pb2.UserID(userid=id)
      with grpc.insecure_channel('localhost:3102') as channel:
         stub = booking_pb2_grpc.BookingStub(channel)
         bookings_reponse = stub.GetBookingsByUserId(UserID)
         bookings = [
                {
                    "date": date_movie.date,
                    "movies": list(date_movie.movies)  # Convert the repeated field to a Python list
                }
                for date_movie in bookings_reponse.datemovies
            ]
         print(bookings)
         return make_response(jsonify({"bookings": bookings}), 200)
   except grpc.RpcError as e:
      print(f"Erreur : {e}")
      return make_response({"error":"no bookings for this user"}, 400)
   

@app.route("/users/movies/<user>",methods=['GET'])
def get_movies_byuser(user):
   id = -1
   for useri in users :
      if useri["name"] == user or useri["id"] == user :
         id = useri["id"]
         break
   if id == -1 :
      return make_response(jsonify({"error":"user not found"}),400)
   response = requests.get(f"http://{IP}:{PORT_BOOKING}/bookings/{id}")
   if response.status_code != 200:
      return make_response({"error":"no bookings for this user"}, 400)
   movies_json = {"movies" : []}
   for movies in response.json()["dates"] :
      for movie in movies["movies"] :
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
         movie_response = requests.post(f"http://{IP}:{PORT_MOVIE}/graphql", json={'query': query})
         movies_json["movies"].append(movie_response.json().get('data', {}).get('movie_by_id', {}))
   print("test")
   print(movies_json)
   return make_response(jsonify(movies_json),200)

def run():
   print("--------------AddBookings--------------")

if __name__ == "__main__":
   print("Server running in port %s"%(PORT))
   app.run(host=HOST, port=PORT)