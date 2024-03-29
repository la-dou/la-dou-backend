from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from ..utils.hashing import (
    get_hashed_password, create_access_token, create_refresh_token, verify_password)

from ..models.token import TokenSchema
from ..models.user import UserOut, UserSignup, PasswordReset
from ..config.database import db
from ..config.deps import get_current_user
from ..utils.otp import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

auth = APIRouter()


@auth.post("/signup", response_model=UserOut)
async def signup(userInfo: UserSignup):

    # Check if user already exists
    if db.find_one({"roll_no": userInfo.roll_no}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    # Hash password
    hashed_password = get_hashed_password(userInfo.password)

   
    userInfo.password = hashed_password

    # Insert user
    # print(userInfo.dict())
    db.insert_one(userInfo.dict())

    # Return user
    return userInfo


@auth.post("/login", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):

    # Find user
    user = db.find_one({"roll_no": int(form_data.username)})

    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roll Number not found",
        )

    # Check if password is correct
    if not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your roll number or password is incorrect",
        )

    # Create access token
    access_token = create_access_token(user["roll_no"])

    # Create refresh token
    refresh_token = create_refresh_token(user["roll_no"])

    # Return tokens
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@auth.post("/reset-password")
async def reset_password(password_reset: PasswordReset):
    user = db.find_one({"roll_no": password_reset.roll_no})
    # check if the user has a valid token (generated by the otp route)
    verified, messsage = verify_token(
        password_reset.roll_no, password_reset.verification_token)
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=messsage,
        )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Hash password
    hashed_password = get_hashed_password(password_reset.password)

    response = db.update_one({"roll_no": password_reset.roll_no}, {
                             "$set": {"password": hashed_password}})

    if response:
        return {"detail": "Password updated successfully"}
    else:
        return {"detail": "User not found"}
