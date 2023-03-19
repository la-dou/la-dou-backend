from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.auth import auth

from .config.database import db


app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth)

@app.on_event("startup")
async def startup():
    pass

@app.get("/")
def read_root():
    print(db)
    print(db.find_one())
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    print(db)
    return {"item_id": item_id, "q": q}
