import grpc
from concurrent import futures
import booking_pb2
import booking_pb2_grpc
import showtime_pb2
import showtime_pb2_grpc

import json
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(base_dir, 'data/bookings.json')

class BookingServicer(booking_pb2_grpc.BookingServicer):

    PORT_SHOWTIME = 3304
    IP = "127.0.0.1"

    def __init__(self):
        with open(json_path, "r") as jsf:
            self.db = json.load(jsf)["bookings"]

    def write_in_database(self):
        with open(json_path, "w") as file:
            json.dump({"bookings":self.db}, file, indent=2)

    def GetBookings(self):
        for booking in self.db:
            yield booking_pb2.BookingResponse(
                userid=booking["userid"],
                datemovies=booking["dates"])

    def GetBookingsByUserId(self, request, context):
        for booking in self.db :
            if str(booking["userid"]) == str(request.userid):
                return booking_pb2.BookingResponse(
                    userid=booking["userid"],
                    datemovies=booking["dates"])
        return booking_pb2.BookingResponse(
            userid="",
            datemovies=[])

    def AddBookings(self, request, context):
        # récupération des arguments de la requête : utilisateur, jour et film de la réservation
        userid_request = request.userid
        date_request = request.date
        movie_request = request.movies
        try:
            # appel à l'api showtime pour vérifier que le film passe bien le jour demandé
            with grpc.insecure_channel('localhost:3304') as channel:
                stub = showtime_pb2_grpc.ShowtimeStub(channel)
                response = get_showtime_by_date(stub, date_request)
                if movie_request not in response.movies:
                    return self.create_error(context)
                # vérification dans la database des réservations que la réservation demandée n'existe pas déjà
                for booking in self.db:
                    if userid_request == booking["userid"]:
                        for date in booking["dates"]:
                            if str(date["date"]) == str(date_request):
                                for movie in date["movies"]:
                                    if movie == movie_request:
                                        return self.create_error(context)
                                # création de la réservation si l'utilisateur et la date sont déjà dans la DB
                                date["movies"].append(movie_request)
                                self.write_in_database()
                                return self.create_response(userid_request)
                            # création de la réservation si l'utilisateur est déjà dans la DB
                        booking["dates"].append({"date":date_request,"movies":[movie_request]})
                        self.write_in_database()
                        return self.create_response(userid_request)
                # création de la réservation si aucune donnée n'est déjà dans la DB
                self.db.append({"userid": userid_request,
                                "dates": [
                                {
                                "date": date_request,
                                "movies": [movie_request]
                                }
                                ]
                            })
                self.write_in_database()
                return self.create_response(userid_request)
        # traitement des erreurs éventuelles
        except grpc.RpcError as e:
            if (e.code() == grpc.StatusCode.NOT_FOUND):
                return self.create_error(context)
        
    # création d'un objet BookingResponse vide si la demande d'ajout de réservation échoue
    def create_error(self, context):
        context.set_code(grpc.StatusCode.NOT_FOUND)
        return booking_pb2.BookingResponse(userid="",datemovies=[])

    # création d'un objet BookingResponse affichant les réservations de l'utilisateur concerné si sa demande d'ajout de réservation est validée
    def create_response(self, userid):
        datemovies=[]
        for booking in self.db:
            if booking["userid"] == userid:
                datemovies = [booking_pb2.DateMovies(date=schedule["date"],movies=schedule["movies"]) for schedule in booking["dates"]]
        return booking_pb2.BookingResponse(userid=userid,datemovies=datemovies)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    booking_pb2_grpc.add_BookingServicer_to_server(BookingServicer(), server)
    server.add_insecure_port('[::]:3302')
    server.start()
    server.wait_for_termination()

def get_showtimes(stub):
    showtimes = stub.GetShowtimes(showtime_pb2.Empty())
    print(showtimes)

def get_showtime_by_date(stub, date):
    Date = showtime_pb2.Date(date=date)
    showtime = stub.GetShowmovies(Date)
    return showtime

if __name__ == '__main__':
    serve()