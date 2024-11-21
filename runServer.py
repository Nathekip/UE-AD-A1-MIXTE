import subprocess
import os

def run_server(command):
    return subprocess.Popen(command, shell=True)

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    servers = [
        f'pymon "{os.path.join(base_dir, "user/user.py")}"',
        f'pymon "{os.path.join(base_dir, "movie/movie.py")}"',
        f'pymon "{os.path.join(base_dir, "showtime/showtime.py")}"',
        f'pymon "{os.path.join(base_dir, "booking/booking.py")}"'
    ]

    processes = [run_server(server) for server in servers]

    for process in processes:
        process.wait()