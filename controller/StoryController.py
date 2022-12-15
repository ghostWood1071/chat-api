from fastapi import APIRouter, Response, Depends, HTTPException
from models.models import * 
from bussiness.user import *
from fastapi.security import (
    OAuth2PasswordRequestForm,
    SecurityScopes
)
from config import *
from datetime import timedelta, datetime
from security.token import Tokenizer
from bussiness.story import *


router = APIRouter()

@router.get("/get-story/{user1}/{user2}/{page}")
async def get_story(user1: str, user2: str, page:int):
    return await get_story_in_db(user1, user2, page)
