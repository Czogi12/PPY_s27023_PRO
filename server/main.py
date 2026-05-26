import argparse
import socketio
import uvicorn
from fastapi import FastAPI
from server.routers.lobby_router import create_lobby_router
from server.routers.user_router import create_user_router
from server.services.lobby_service import LobbyService
from server.sockets.lobby_socket import register_lobby_socket
from server.services.user_service import UserService

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--salt", default="5163068586cbe53083a4d33e9d910989", help="Password salt")
    parser.add_argument("--hash_key", default="885bab4433b81fd61b0c0bb9eb5fefae", help="Password hash key")
    args = parser.parse_args()

    fastapi_app = FastAPI()
    sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

    user_service = UserService(args.salt, args.hash_key)
    lobby_service = LobbyService(sio)

    fastapi_app.include_router(create_user_router(user_service))
    fastapi_app.include_router(create_lobby_router(lobby_service, user_service))

    register_lobby_socket(sio, lobby_service, user_service)

    app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)
    uvicorn.run(app, host="127.0.0.1", port=8000)
