from ..utils.email_verification_utils import generate_OTP, verify_OTP, send_email

from fastapi import APIRouter, status, HTTPException

otp_router = APIRouter()

@otp_router.post("/generate_otp")
async def generate_otp(roll_no: str):
    otp = generate_OTP(roll_no)
    # send otp to the user
    await send_email(f"{roll_no}@lums.edu.pk", otp)

@otp_router.post("/verify_otp", response_model=bool)
async def verify_otp(roll_no: str, otp: int):
    verification_result, message = verify_OTP(roll_no, otp)

    if verification_result and message == "success":
        return True
    
    elif message == "OTP expired":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP expired",
        )
    elif message == "Invalid OTP":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP",
        )
    elif message == "Invalid client id":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid client id",
        )
    
    return False