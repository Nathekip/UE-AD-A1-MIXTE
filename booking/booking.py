import grpc
from concurrent import futures
#import booking_pb2
#import booking_pb2_grpc
import showtime_pb2
import showtime_pb2_grpc

import json

#class BookingServicer(booking_pb2_grpc.BookingServicer):

#    def __init__(self):
#        with open('{}/data/bookings.json'.format("."), "r") as jsf:
#            self.db = json.load(jsf)["schedule"]

#def serve():
#    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
#    booking_pb2_grpc.add_BookingServicer_to_server(BookingServicer(), server)
#    server.add_insecure_port('[::]:3002')
#    server.start()
#    server.wait_for_termination()


def get_showtimes(stub):
    showtimes = stub.GetShowtimes(showtime_pb2.Empty())
    print(showtimes)

def get_showtime_by_date(stub, date):
    showtime = stub.GetShowmovies(date)
    print(showtime)

def run():
    with grpc.insecure_channel('localhost:3002') as channel:
        stub = showtime_pb2_grpc.ShowtimeStub(channel)
        print("--------------GetShowtimes--------------")
        get_showtimes(stub)
        print("--------------GetShowtimeByDate--------------")
        date = showtime_pb2.Date(date="20151130")
        #request = {"date":date}
        get_showtime_by_date(stub, date)


if __name__ == '__main__':
    run()