from .config.database import db
from .schemas.user import usersEntity
from .routes.user import user
from .routes.rating import ratings_router
from typing import Union
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes.auth import auth
from .routes.otp import otp_router
from .routes.fcm import fcm
<< << << < Updated upstream
== == == =
>>>>>> > Stashed changes


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
app.include_router(otp_router, prefix="/otp",
                   tags=["User Verification using OTP"])
app.include_router(fcm, prefix="/fcm",
                   tags=["FCM (Firebase Cloud Messaging) Token Management"])
app.include_router(user, tags=["User Management"])
app.include_router(ratings_router, tags=["Ratings"])


@app.on_event("startup")
async def startup():
    pass


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/all")
def read_all():
    # return dict(db.find())
    response = db.find()
    print("Type of response: ", type(response))
    print("Response: ", response)

    for user in response:
        print(user["_id"])
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
