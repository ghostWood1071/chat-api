from pymongo import MongoClient
from pymongo.cursor import Cursor
from pymongo.results import UpdateResult, InsertOneResult
import logging
from config import *
import asyncio
from pymongo.errors import *
from typing import *
from pymongo.collection import Collection

def get_client()->MongoClient:
    client:MongoClient = MongoClient(MONGO_DB_URL)
    client.server_info()
    return client

def get_info(client: MongoClient)->None:
    return client.server_info()

async def create_connection():
    loop = asyncio.get_running_loop()
    client:MongoClient = await loop.run_in_executor(None, get_client)
    return client

async def check_connection(client: MongoClient)->bool:
    loop = asyncio.get_running_loop()
    try:
        await loop.run_in_executor(None, get_info, (client))
        return True
    except InvalidOperation as e:
        logging.error(str(e))
        logging.error("reconnecting server ....")
        return False

def close_client(client:MongoClient)->None:
    client.close()

def find_one(client:MongoClient, db: str, col:str, query:Dict[str, Any], opts = None)->Dict[str, Any]:
    col: Collection = client[db][col]
    return col.find_one(query, opts)

def find(client: MongoClient, db:str, col:str, query:Dict[str, Any], opts=None)->Cursor:
    col:Collection = client[db][col]
    return col.find(query, opts)

def update_one(client:MongoClient, db:str, col:str, query:Dict[str,Any], val: Dict[str, Any])->Dict[str, Any]:
    col:Collection = client[db][col]
    return col.update_one(query, val).raw_result

def insert_one(client:MongoClient, db:str, col:str, data:Dict[str, Any])->Dict[str, Any]:
    col:Collection = client[db][col]
    return col.insert_one(data).inserted_id

def aggregate(client:MongoClient, db:str, col:str, query:List[Dict[str, Any]])->List[Dict[str, Any]]:
    col:Collection = client[db][col]
    db_set = col.aggregate(query)
    result = list()
    for item in db_set:
        result.append(item)
    return result

    