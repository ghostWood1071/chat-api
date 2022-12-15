from fastapi import WebSocket
import logging
from typing import List, Dict
from models.models import Event, EventType
from bussiness.user import *
from bussiness.story import *


logging = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.connections: Dict[str, Dict[str, WebSocket]] = dict()
    
    async def connect(self, websocket:WebSocket, user_id: str, account:str):
        await websocket.accept()
        self.connections.update({account: {user_id: websocket}})
        print(self.connections);
        await update_user_state(user_id, True)
        unseens = await pull_queue(account) #list string 
        for mess in unseens:
            if mess['type'] != EventType.FRIEND_ACCEPT.value:
                await update_story(mess['sender'], mess['receiver'], mess)
            mess.update({'create_date' : str(mess['create_date'])})
            await websocket.send_json(mess)
        
    async def disconnect(self, account: str):
        conn: Dict[str, Any] = self.connections.get(account) 
        if conn is not None:
            self.connections.pop(account)
            user_id = list(conn.keys())[0]
            await update_user_state(user_id, False)
    
    async def send(self, info, sender ,receiver):
        message = Event(**{
            'sender': sender,
            'receiver':  receiver,
            'type': info['type'],
            'content': info['content'],
            'create_date': datetime.now().timestamp()
        })
        receiver_conn = self.connections.get(info['receiver'])
        send_data = message.dict()
        if receiver_conn is not None:
           online_user = list(receiver_conn.values())[0]
           print('ok: ', send_data)
        #    send_data.update({'create_date': str(message.create_date)})
           await update_story(message.sender, message.receiver, send_data)
           await online_user.send_json(send_data)
        else:
            print('data: ', send_data)
            await update_story(message.sender, message.receiver, send_data, False)
            