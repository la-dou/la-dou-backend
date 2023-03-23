from fastapi import APIRouter, status, HTTPException

from ..models.user import User

from ..utils.hashing import get_hashed_password

from ..config.database import db
from ..config.deps import get_current_user

reset_password = APIRouter()

@reset_password.post("/reset_password")
async def reset_password_route(roll_no: str, new_password: str):
    
    user = db.find_one({"roll_no" : roll_no})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    # Hash password
    hashed_password = get_hashed_password(new_password)

    stored_user = User(**user)
    updated_user = stored_user.copy()
    updated_user.password = hashed_password

    response = db.update_one({"roll_no": roll_no}, {"$set": updated_user.dict()})

    if response:
        return updated_user
    else:
        return {"detail": "User not found"}