import socketio
import uvicorn
from fastapi import FastAPI
from .routers.user_router import router as user_router

fastapi_app = FastAPI()
sio = socketio.AsyncServer(async_mode="asgi", cors_allowed_origins="*")

fastapi_app.include_router(user_router)

@sio.event
async def connect(sid, environ):
    print("client connected", sid)

@sio.event
async def message(sid, data):
    await sio.emit("reply", {"echo": data}, to=sid)

app = socketio.ASGIApp(sio, other_asgi_app=fastapi_app)
uvicorn.run(app, host="127.0.0.1", port=8000)