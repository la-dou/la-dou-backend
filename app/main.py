from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.auth import auth
from .routes.otp import otp_router

from .schemas.user import usersEntity

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
app.include_router(otp_router)

@app.on_event("startup")
async def startup():
    pass

@app.get("/")
def read_root():
    print(db)
    print(db.find_one())
    return {"Hello": "World"}


@app.get("/all")
def read_all():
    # return dict(db.find())
    response = db.find()
    print("Type of response: ", type(response))
    print("Response: ", response)

    for user in response:
        print(user["_id"])
        print(user["id"])
        print(user["name"])
        print(user["roll_no"])
        print(user["email_verified"])


    return {"detail": "All users"}
    # return dict(response)

# TODO: Remove this route
@app.get("/dump")
def dump():
    db.drop()
    return {"detail": "Database dropped"}