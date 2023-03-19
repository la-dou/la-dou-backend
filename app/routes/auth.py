

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


@auth.get('/me', response_model=UserOut)
async def me(current_user: SystemUser = Depends(get_current_user)):
    return current_user

