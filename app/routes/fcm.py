from fastapi import APIRouter, Depends

from ..config.database import db
from ..models.user import UserOut, SystemUser
from ..config.deps import get_current_user
from ..utils.fcm import send_notification, send_notification_to_user

fcm = APIRouter()


@fcm.post('/add', response_model=UserOut)
async def add_firebase_token(token: str, current_user: SystemUser = Depends(get_current_user)):
    # fetch user from db
    user = db.find_one({"roll_no": current_user.roll_no})
    # append token to the list of tokens
    if token not in user["fcm_device_token"]:
        user["fcm_device_token"].append(token)
    # write to db
    db.update_one({"roll_no": user["roll_no"]}, {
                    "$set": {"fcm_device_token": user["fcm_device_token"]}})
    # Return user
    return user

@fcm.post('/remove', response_model=UserOut)
async def remove_firebase_token(token: str, current_user: SystemUser = Depends(get_current_user)):
    # fetch user from db
    user = db.find_one({"roll_no": current_user.roll_no})
    # remove token from the list of tokens
    user["fcm_device_token"].remove(token)
    # write to db
    db.update_one({"roll_no": user["roll_no"]}, {
                    "$set": {"fcm_device_token": user["fcm_device_token"]}})
    # Return user
    return user

# TODO: REMOVE THIS LATER
@fcm.post('/test')
async def send_notif(title: str, body: str, roll_no: int):
    send_notification_to_user(title, body, roll_no)
