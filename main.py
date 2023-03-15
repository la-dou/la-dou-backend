from typing import Union
from fastapi import FastAPI
from .config.database import db


app = FastAPI()


@app.get("/")
def read_root():
    print(db)
    print(db.find_one())
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    print(db)
    return {"item_id": item_id, "q": q}
