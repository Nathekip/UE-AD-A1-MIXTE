import grpc
from concurrent import futures
import booking_pb2
import booking_pb2_grpc
import showtime_pb2
import showtime_pb2_grpc

import json

class BookingServicer(booking_pb2_grpc.BookingServicer):

    PORT_SHOWTIME = 3202
    IP = "127.0.0.1"

    def __init__(self):
        with open('{}/booking/data/bookings.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["bookings"]

    def write_in_database(self):
        with open('{}/booking/data/bookings.json'.format("."), "w") as file:
            json.dump({"bookings":self.db}, file, indent=2)

    def create_error(self, context):
        context.set_code(grpc.StatusCode.NOT_FOUND)
        return booking_pb2.BookingResponse(userid="",datemovies=[])

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
        userid_request = request.userid
        date_request = request.date
        movie_request = request.movies
        try:
            with grpc.insecure_channel('localhost:3202') as channel:
                stub = showtime_pb2_grpc.ShowtimeStub(channel)
                response = get_showtime_by_date(stub, date_request)
                if movie_request not in response.movies:
                    return self.create_error(context)
                for booking in self.db:
                    if userid_request == booking["userid"]:
                        for date in booking["dates"]:
                            if str(date["date"]) == str(date_request):
                                for movie in date["movies"]:
                                    if movie == movie_request:
                                        return self.create_error(context)
                                date["movies"].append(movie_request)
                                self.write_in_database()
                                return self.create_response(userid_request)
                        booking["dates"].append({"date":date_request,"movies":[movie_request]})
                        self.write_in_database()
                        return self.create_response(userid_request)
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
        except grpc.RpcError as e:
            if (e.code() == grpc.StatusCode.NOT_FOUND):
                return self.create_error(context)
        

    def create_response(self, userid):
        for booking in self.db:
            if booking["userid"] == userid:
                print("test userid == userid")
                datemovies = [booking_pb2.DateMovies(date=schedule["date"],movies=schedule["movies"]) for schedule in booking["dates"]]
                print("test datemovies")
        return booking_pb2.BookingResponse(userid=userid,datemovies=datemovies)





def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    booking_pb2_grpc.add_BookingServicer_to_server(BookingServicer(), server)
    server.add_insecure_port('[::]:3102')
    server.start()
    server.wait_for_termination()


def get_showtimes(stub):
    showtimes = stub.GetShowtimes(showtime_pb2.Empty())
    print(showtimes)

def get_showtime_by_date(stub, date):
    Date = showtime_pb2.Date(date=date)
    showtime = stub.GetShowmovies(Date)
    return showtime

def run():
    with grpc.insecure_channel('localhost:3202') as channel:
        stub = showtime_pb2_grpc.ShowtimeStub(channel)
        print("--------------GetShowtimes--------------")
        get_showtimes(stub)
        print("--------------GetShowtimeByDate--------------")
        date = showtime_pb2.Date(date="20151130")
        get_showtime_by_date(stub, date)


if __name__ == '__main__':
    #run()
    serve()