import grpc
from concurrent import futures
import showtime_pb2
import showtime_pb2_grpc
import json

class ShowtimeServicer(showtime_pb2_grpc.ShowtimeServicer):
    def __init__(self):
        with open('{}/showtime/data/times.json'.format("."), "r") as jsf:
            self.db = json.load(jsf)["schedule"]

    def GetShowtimes(self, request, context):
        for schedule in self.db:
            yield showtime_pb2.ShowtimeData(date=schedule["date"],movies=schedule["movies"])

    def GetShowmovies(self, request, context):
        for schedule in self.db:
            if schedule["date"] == request.date:
                return showtime_pb2.ShowtimeData(date=schedule["date"],movies=schedule["movies"])
        context.set_code(grpc.StatusCode.NOT_FOUND)
        return showtime_pb2.ShowtimeData(date="",movies=[])

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    showtime_pb2_grpc.add_ShowtimeServicer_to_server(ShowtimeServicer(), server)
    server.add_insecure_port('[::]:3304')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()