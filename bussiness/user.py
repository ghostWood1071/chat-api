from Helper.DbHelper import MongoDB
from typing import *
from config import DATABASE_NAME
from models.models import *
from security.password import Crypto
from fastapi import Depends, HTTPException, status
from security.auth import OAuth2Bearer
from security.token import Tokenizer
from jose import JWTError
from pydantic import ValidationError
from bson import ObjectId

col_name = 'users'

async def get_user(user_name: str)->UserInDB:
    await MongoDB.get_client()
    try: 
        result: Dict[str, Any] = await MongoDB.find_one(DATABASE_NAME, col_name, {'account': user_name})
        return UserInDB(**result)
    except TypeError:
        return None
    except Exception as e:
        raise e

async def create_user(user: User) -> str:
    await MongoDB.get_client()
    try:
       prev_users = await MongoDB.find(DATABASE_NAME, col_name, { '$or': [{'account': user.account}, {'email': user.email}]})
       if len(list(prev_users)) > 0:
        raise Exception("user existed")
       user_data = user.dict()
       Crypto.get_crypto()
       user_data.update({'password': Crypto.hash_password(user.password)})
       _id:str = await MongoDB.insert_one(DATABASE_NAME, col_name, user_data)
       return _id
    except Exception as e:
        raise e

async def auth_user(account, password)->UserInDB:
    try:
        await MongoDB.get_client()
        Crypto.get_crypto()
        user = await MongoDB.find_one(DATABASE_NAME, col_name, {'account': account})
        if user is None:
            return None
        if not Crypto.verify_password(password, user['password']):
            return None
        return UserInDB(**user)
    except Exception as e:
        raise e
        
async def get_user_by_token(token:str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials"
    )
    try:
        token_data:Dict[str, Any] = Tokenizer.decode(token)
    except (JWTError, ValidationError):
        raise credentials_exception
    
    await MongoDB.get_client()
    user = await MongoDB.find_one(DATABASE_NAME, col_name, {'_id': ObjectId(token_data['user_id'])}, {'friends': 0})
    if user is None:
        raise credentials_exception
    return UserInDB(**user)

async def get_current_user(token: str = Depends(OAuth2Bearer.get_scheme())):
    return await get_user_by_token(token)
    
async def change_profile(user:Dict[str, Any])->UserInDB:
    await MongoDB.get_client()
    if user['avatar'] != '' or user['avatar'] is not None:
        await MongoDB.update_one(DATABASE_NAME, col_name, {'account': user['account']}, {'$set': {'name': user['name'], 'avatar': user['avatar'], 'about': user['about']}})
    await MongoDB.update_one(DATABASE_NAME, col_name, {'account': user['account']}, {'$set': {'name': user['name'], 'about': user['about']}})
    return await MongoDB.find_one(DATABASE_NAME, col_name, {'account': user['account']}, {'friends': 0, 'password': 0, '_id': 0})

async def update_user_state(user_id:str, state: bool):
    await MongoDB.get_client()
    user: Dict[str, any] = await MongoDB.find_one(DATABASE_NAME, col_name, {'_id': ObjectId(user_id)})
    if user is None:
        raise Exception("user not existed")
    if user.get('active') != state:
        return await MongoDB.update_one(DATABASE_NAME, col_name,  {'_id': ObjectId(user_id)} ,{'$set': {'active': state}})
    return {}

async def get_friend_list(user: UserInDB, page: int):
    data: List[Dict[str, Any]] = await MongoDB.aggregate(DATABASE_NAME, col_name, [
        {'$match': { "_id": user.id} }, 
        { 
            '$lookup': {
                    'from': 'users',        
                    'localField': 'friends',
                    'foreignField': 'account',
                    'as': 'people' 
            }       
        },
        {'$project': 
            {
                '_id': 0, 
                'people.account': 1, 
                'people.name': 1, 
                'people.avatar': 1, 
                'active': 1,
            } 
        },
        {'$project':  {'list_friends': {'$slice': ['$people', (page-1)*10, 10]}}}
    ])
    result = data[0].get('list_friends')
    return result
    




    

