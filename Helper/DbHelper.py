from pymongo import MongoClient
from pymongo.cursor import Cursor
from pymongo.results import UpdateResult
import logging
from config import *
import asyncio
from pymongo.errors import *
from typing import *
from Helper.DBLogic import *

class MongoDB:
    CLIENT: MongoClient = None 
    
    @classmethod
    async def get_client(cls)->MongoClient:
        try:
            if cls.CLIENT == None or not await check_connection(cls.CLIENT):
                cls.CLIENT = await create_connection()
            return cls.CLIENT
        except (InvalidOperation, ServerSelectionTimeoutError) as e:
        # except Exception as e:
            logging.error(e)
            raise e
    
    @classmethod
    async def close_client(cls)->bool:
        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(None, close_client, (cls.CLIENT))
            return True
        except Exception as e:
            logging.error(e)
            raise e
    
    @classmethod
    async def find_one(cls, database: str ,collection:str, query: Dict[str, Any], opts=None)->Dict[str, Any]:
        loop = asyncio.get_running_loop()
        try:
            result: Dict[str, Any] = await loop.run_in_executor(None, find_one, cls.CLIENT, database, collection, query, opts)
            return result
        except Exception as e:
            logging.error(e)
            raise e
    
    @classmethod
    async def find(cls, db:str, col:str, query:Dict[str, Any], opts=None)->Cursor:
        loop = asyncio.get_event_loop()
        try:
            result: Dict[str, Any] = await loop.run_in_executor(None, find, cls.CLIENT, db, col, query, opts)
            return result
        except Exception as e:
            logging.error(e)
            raise e
    
    @classmethod
    async def update_one(cls, db:str, col:str, query:Dict[str, Any], val: Dict[str, Any])->Dict[str, Any]:
        loop = asyncio.get_event_loop()
        try:
            result: Dict[str, Any] = await loop.run_in_executor(None, update_one, cls.CLIENT, db, col, query, val)
            return result
        except Exception as e:
            logging.error(e)
            raise e
    
    @classmethod 
    async def insert_one(cls, db:str, col:str, data:Dict[str, Any])->str:
        loop = asyncio.get_event_loop()
        try:
            result: Dict[str, Any] = await loop.run_in_executor(None, insert_one, cls.CLIENT, db, col, data)
            return result
        except Exception as e:
            logging.error(e)
            raise e
    
    @classmethod
    async def aggregate(cls, db:str, col:str, query:List[Dict[str, Any]])->List[Dict[str, Any]]:
        loop = asyncio.get_event_loop()
        try:
            result: List[Dict[str, Any]] = await loop.run_in_executor(None, aggregate, cls.CLIENT, db, col, query)
            return result
        except Exception as e:
            logging.error(e)
            raise e