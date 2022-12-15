import json
from fastapi import FastAPI, WebSocket
from config import *
from starlette.middleware.cors import CORSMiddleware
from typing import *
from bussiness.user import *
from bussiness.story import *
from controller import UserController, StoryController
from Helper.SocketHelper import ConnectionManager
from starlette.websockets import WebSocketState
import uvicorn
from fastapi.staticfiles import StaticFiles

import logging

app = FastAPI()
logger = logging.getLogger(__name__)



app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGIN,  # can alter with time
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = ConnectionManager()

app.include_router(UserController.router, prefix="/api/user")
app.include_router(StoryController.router, prefix='/api/story')
app.mount("/public", StaticFiles(directory="public"), name="public")

@app.websocket('/ws')
async def endpoint(websocket: WebSocket, key:str = ""):
    user_in_db: UserInDB = await get_user_by_token(key)
    user = user_in_db.dict()
    try:
        await manager.connect(websocket, str(user['id']), user['account'])
        while True:
            if websocket.application_state == WebSocketState.CONNECTED:
                info = await websocket.receive_json()
                print(info)
                await manager.send(info, info['sender'], info['receiver'])
            else:
                await manager.connect(websocket, str(user['id']), user['account'])
    except Exception as e:
        
        logging.error(e)
        await manager.disconnect(user['account'])

if __name__ == '__main__':
    uvicorn.run("main:app", port=PORT, host=HOST, reload=True)


