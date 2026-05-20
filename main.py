import sys
from server import main as server_main
from client.client import main as client_main

if __name__ == '__main__':
    if "server" in sys.argv:
        server_main()
    if "client" in sys.argv:
        client_main()
