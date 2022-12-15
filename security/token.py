from jose import JWTError, jwt
from typing import *
from config import *
from datetime import timedelta,datetime
class Tokenizer:
    @classmethod
    def create_token(cls, data: Dict[str, Any], expire_delta: Union[timedelta, None] = None):
        copy_data = data.copy()
        if expire_delta:
            expire = datetime.utcnow() + expire_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        copy_data.update({'exp': expire})
        encoded = jwt.encode(copy_data, SECRET_KEY, algorithm=ALGORITHM)
        return encoded
    
    @classmethod
    def decode(cls, token):
        try:
            # print('lol', token)
            data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return data
        except JWTError as e:
            raise e
    