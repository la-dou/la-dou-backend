from pydantic import BaseModel

class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    
    
class TokenPayload(BaseModel):
    sub: str = None
    exp: int = None

class TokenData(BaseModel):
    roll_no: int = None
    role: str = None