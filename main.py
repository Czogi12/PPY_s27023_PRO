import sys

if __name__ == '__main__':
    if "server" in sys.argv:
        import server.main
    if "client" in sys.argv:
        import client.main
