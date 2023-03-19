from pydantic import BaseModel

class Rating(BaseModel):
    sum: int
    count: int                  