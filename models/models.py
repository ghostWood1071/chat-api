from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from models.Id import Id
from typing import *
from bson import ObjectId
from enum import Enum


class EventType(Enum):
    CONNECT = 1
    DISCONNECT = 2
    FRIEND_REQUEST = 3
    CHAT = 4
    FRIEND_ACCEPT = 5

class User(BaseModel):
    name: str = Field(default='')
    account: str = Field(default='')
    password: str  = Field(default='')
    avatar: str = Field(default='')
    birth: datetime = Field(default=datetime.now())
    email: str = Field(default='')
    about: str = Field(default='')
    active: bool = Field(default=True)
    friends: List[str] = Field(default=[])

class UserInDB(User):
    id: Id = Field(alias='_id')
    created_date = Field(default=datetime.now())
    class Config:
        json_encoders = {ObjectId: str}


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None
    scopes: List[str] = [] 

class Story(BaseModel):
    peers: List[str] = Field(default=[])
    messages: List[Any] = Field(default=[])

class StoryInDB(Story):
    id: Id = Field(alias='_id')
    created_date: datetime = Field(default=datetime.now())

class Event(BaseModel):
    sender: str
    receiver: str
    content: str
    type: int = Field(default=1)
    create_date: float = Field(default= datetime.now().timestamp())




