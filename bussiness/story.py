from Helper.DbHelper import MongoDB
from typing import *
from config import DATABASE_NAME
from models.models import *
from bson import ObjectId

COL_NAME = 'stories'
USER_COL_NAME = 'users'

async def update_queue(account: str, event: Dict[str, Any]):
    await MongoDB.get_client()
    user: Dict[str, any] = await MongoDB.find_one(DATABASE_NAME, USER_COL_NAME, {'account': account})
    if user is None:
        raise Exception("user not existed")
    # event['receiver'] = str(user['_id'])
    message_queue: List[str] = user.get("message_queue")
    if message_queue is None:
        message_queue = [event]
        return await MongoDB.update_one(DATABASE_NAME, USER_COL_NAME, {'_id': user['_id']}, {'$set': {'message_queue': message_queue}})
    return await MongoDB.update_one(DATABASE_NAME, USER_COL_NAME, {'_id': user['_id']}, {'$push': {'message_queue': event}})

async def pull_queue(account: str)->List[any]:
    await MongoDB.get_client()
    user: Dict[str, any] = await MongoDB.find_one(DATABASE_NAME, USER_COL_NAME, {'account': account})
    if user is None:
        raise Exception("user not existed")
    message_queue: List[str] = user.get("message_queue")
    if message_queue is not None:
        await MongoDB.update_one(DATABASE_NAME, USER_COL_NAME, {'_id': ObjectId(user['_id'])}, {'$unset': {'message_queue': []}})
    else: 
        message_queue = []
    return message_queue

async def update_story(sender:str, receiver:str ,message: Dict[str, Any], is_online = True):
    await MongoDB.get_client()
    print('update story: ', message, datetime.now().timestamp())
    if message['type'] == EventType.CHAT.value:
        await MongoDB.update_one(DATABASE_NAME, COL_NAME, {
            '$or': [
                {'peers': [sender, receiver]}, 
                {'peers': [receiver, sender]}
            ]}, 
            {'$push': 
                {'messages': message}
            })
    elif message['type'] == EventType.FRIEND_ACCEPT.value:
        new_story_content: Dict[str, Any] = {
            'peers': [sender, receiver],
            'messages': []
        }
        story = Story(**new_story_content)
        await MongoDB.insert_one(DATABASE_NAME, COL_NAME, story.dict())
        await MongoDB.update_one(DATABASE_NAME, USER_COL_NAME, {'account': sender}, {'$push': {'friends': receiver}})
        await MongoDB.update_one(DATABASE_NAME,USER_COL_NAME, {'account': receiver}, {'$push': {'friends': sender}})
    if not is_online:
        await update_queue(receiver, message)

async def get_story_in_db(user1: str, user2:str, page:int):
    await MongoDB.get_client()
    data = await MongoDB.aggregate(DATABASE_NAME, COL_NAME, [
        {'$match': {'$or': [{'peers': [user1, user2]}, {'peers': [user2, user1]}]}},
        {'$unwind': '$messages'},
        {'$sort': {'messages.create_date': -1} },
        {'$group': {'_id': '$_id', 'messages': {'$push': '$messages'}}},
        {'$project': {'_id': 0}},
        {'$project': {'mess_list': {'$slice': ['$messages', (page-1)*20, 20]}}}
    ])
    if(len(data)>0):
        result = data[0].get('mess_list')
    else:
        result = []
    return result