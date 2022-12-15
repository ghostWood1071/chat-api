from passlib.context import CryptContext

class Crypto:
    CONTEXT: CryptContext = None

    @classmethod
    def get_crypto(cls)->None:
        if cls.CONTEXT is None:
            cls.CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    @classmethod
    def hash_password(cls, password: str)->str:
        return cls.CONTEXT.hash(password)
    
    @classmethod
    def verify_password(cls, password, hashing)->bool:
        return cls.CONTEXT.verify(password, hashing)