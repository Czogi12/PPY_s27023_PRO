import argparse
import socketio
import uvicorn
from fastapi import FastAPI
from server.routers.user_router import create_user_router
from services.user_service import UserService

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--salt", default="5163068586cbe53083a4d33e9d910989", help="Password salt")
    parser.add_argument("--hash_key", default="885bab4433b81fd61b0c0bb9eb5fefae", help="Password hash key")
    args = parser.parse_args()

    fastapi_app = FastAPI()
    sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

    user_service = UserService(args.salt, args.hash_key)
    user_router = create_user_router(user_service)
    fastapi_app.include_router(user_router)

    @sio.event
    async def connect(sid, environ):
        print("client connected", sid)

    @sio.event
    async def message(sid, data):
        await sio.emit("reply", {"echo": data}, to=sid)

    app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)
    uvicorn.run(app, host="127.0.0.1", port=8000)
