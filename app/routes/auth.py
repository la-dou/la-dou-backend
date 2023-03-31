

from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from uuid import uuid4

from ..utils.hashing import (
    get_hashed_password, create_access_token, create_refresh_token, verify_password)

from ..models.token import TokenSchema
from ..models.user import UserOut, UserAuth, SystemUser, UserSignup

from ..config.database import db
from ..config.deps import get_current_user


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

auth = APIRouter()

@auth.post("/signup", response_model=UserOut)
async def signup(user: UserSignup):
    
    # Check if user already exists
    if db.find_one({"roll_no" : user.roll_no}): 
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )
        
    # Hash password
    hashed_password = get_hashed_password(user.password)
    
    # Create user
    user = {
        "id": str(uuid4()),
        "roll_no": user.roll_no,
        "name": user.name,
        "password": hashed_password,
        "phone_number": user.phone_number,
        "gender"   : user.gender,
    }
    
    # Insert user
    db.insert_one(user)
    
    # Return user
    return user


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



@auth.get('/me', response_model=UserOut)
async def me(current_user: SystemUser = Depends(get_current_user)):
    return current_user

@auth.post('/firebase/token/add', response_model=UserOut)
async def add_firebase_token(user: UserAuth):
    # Find user
    user = db.find_one({"roll_no": int(user.roll_no)})
    
    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Roll Number not found",
        )
    
    # Check if password is correct
    if not verify_password(user.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Your roll number or password is incorrect",
        )
    
    # Update user
    db.update_one({"roll_no": user["roll_no"]}, {"$set": {"firebase_token": user.firebase_token}})
    
    # Return user
    return user

