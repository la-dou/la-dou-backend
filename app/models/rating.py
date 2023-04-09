from pydantic import BaseModel

class Rating(BaseModel):
    sum: int = 0
    count: int = 0                