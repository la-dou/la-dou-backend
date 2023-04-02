from fastapi import APIRouter, Depends, HTTPException, status
from ..config.deps import get_current_user
from ..models.user import UserOut, SystemUser, PasswordUpdate, PhoneUpdate
from ..config.database import db
from ..utils.hashing import verify_password, get_hashed_password

user = APIRouter()


@user.get('/me', response_model=UserOut)
async def me(current_user: SystemUser = Depends(get_current_user)):
    # fetch user from db
    user = db.find_one({"roll_no": current_user.roll_no})
    response = UserOut(**user)
    # check if Driver Mode is enabled
    if not user["driver"]:
        response.driver_disabled = False
    else:
        response.driver_disabled = user["driver"]["deactivated"]
    if not user["customer"]:
        response.customer_disabled = False
    else:
        response.customer_disabled = user["customer"]["deactivated"]
    return response


@user.post('/update-password', response_model=bool)
async def update_password(password: PasswordUpdate, current_user: SystemUser = Depends(get_current_user)):
    # fetch user from db
    user = db.find_one({"roll_no": current_user.roll_no})
    # check if old password matches
    if not verify_password(password.old_password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password",
        )
    # hash new password
    hashed_password = get_hashed_password(password.new_password)
    # update password
    db.update_one({"roll_no": user["roll_no"]}, {
                  "$set": {"password": hashed_password}})
    return True


@user.post('/update-phone', response_model=bool)
async def update_phone(phone: PhoneUpdate, current_user: SystemUser = Depends(get_current_user)):
    # fetch user from db
    user = db.find_one({"roll_no": current_user.roll_no})
    # check if old password matches
    if not verify_password(phone.old_password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password",
        )
    # update phone
    db.update_one({"roll_no": user["roll_no"]}, {
                  "$set": {"phone_number": phone.phone_number}})
    # set phone_verified to false
    db.update_one({"roll_no": user["roll_no"]}, {
        "$set": {"phone_verified": False}})
    return True
