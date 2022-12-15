from fastapi.security import OAuth2PasswordBearer


class OAuth2Bearer:
    SCHEME = None
    @classmethod
    def get_scheme(cls):
        if cls.SCHEME is None:
            cls.SCHEME = OAuth2PasswordBearer(tokenUrl="api/user/token")
        return cls.SCHEME
    
    