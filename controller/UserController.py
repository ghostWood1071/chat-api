from fastapi import APIRouter, Response, Depends, HTTPException, UploadFile, File
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
import os


router = APIRouter()

@router.post("/signup")
async def sign_up(user:User):
    try:
        _id:str = await create_user(user)
        return str(_id)
    except Exception as e:
        return Response(str(e), status_code=500, media_type="text/plain")

@router.post("/token", response_model=Token)
async def get_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user:UserInDB = await auth_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(400, "incorrect username or password")
    expire = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = Tokenizer.create_token(
        data = {'user_id': str(user.id)},
        expire_delta= expire
    )
    return {"access_token": token, "token_type": "bearer"}

@router.get("/auth", response_model=UserInDB, response_model_exclude={"password"})
async def authenthicate(user: UserInDB = Depends(get_current_user)):
    return user

@router.get("/info", response_model=User, response_model_exclude={"password", "friends"})
async def get_info(user: User = Depends(get_current_user)):
    return user;

@router.get("/find/{account}", response_model=User, response_model_exclude={"password", "friends", "_id"})
async def find_user(account:str):
    user: UserInDB = await get_user(account)
    return user

@router.get("/friends/{page}")
async def get_friends(page:int, user: UserInDB = Depends(get_current_user)):
    data = await get_friend_list(user, page)
    return data

@router.post("/uploadfile")
async def create_upload_file(file: UploadFile = File(), user: UserInDB = Depends(get_current_user)):
    try:
        if not os.path.exists(f"public/{user.account}/"):
            os.mkdir(f"public/{user.account}/")
        content = file.file.read()
        with open(f"public/{user.account}/{file.filename}", mode='wb') as f:
            f.write(content)
        return {'file_name': f"public/{user.account}/{file.filename}"}
    except Exception as e:
        raise e
        return e

@router.post("/changeprofile")
async def update_profile(user:User, auth:User = Depends(get_current_user)):
    result =  await change_profile(user.dict())
    return result;
    