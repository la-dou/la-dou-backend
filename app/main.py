from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.auth import auth
from .routes.otp import otp_router
from .routes.fcm import fcm
from .routes.user import user
from .routes.order import order_router
from .routes.rating import ratings_router
from .config.database import db
from .schemas.user import usersEntity
from .routes.admin import admin
from .models.user import UserSignup


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
app.include_router(ratings_router, prefix="/rate", tags=["Ratings"])
app.include_router(order_router, tags=["Order Management"])
app.include_router(admin, prefix="/admin", tags=["Admin Management"])

@app.on_event("startup")
async def startup():
    pass


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/all")
def read_all():
    response = db.find()
    return (usersEntity(response))


# TODO: Remove this route
@app.get("/dump")
def dump():
    db.drop()
    return {"detail": "Database dropped"}

@app.get("/delete/user/{roll_no}") #used for testing only
def delete_user(roll_no: int):
    query = {"roll_no": roll_no}
    db.delete_one(query)
    return {"detail": "User deleted"}

@app.post("/add/user/forced/{roll_no}")  #used for testing only
def add_user(userInfo: UserSignup):
    db.insert_one(userInfo.dict())

