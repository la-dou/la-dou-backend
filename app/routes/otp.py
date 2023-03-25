from ..utils.email_verification_utils import generate_OTP, verify_OTP, send_email
from ..models.otp import VerifyOTP

from fastapi import APIRouter, status, HTTPException

otp_router = APIRouter()


@otp_router.post("/otp/email/generate")
async def generate_email_otp(roll_no: str):
    otp = generate_OTP(roll_no)
    # send otp to the user
    await send_email(f"{roll_no}@lums.edu.pk", otp)

    return {"message": "OTP sent to your email"}


@otp_router.post("/otp/email/verify", response_model=bool)
async def verify_email_otp(data: VerifyOTP):
    verification_result, message = verify_OTP(data.roll_no, data.otp)

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

@otp_router.post("/opt/phone/generate")
async def generate_phone_otp(roll_no: str):
    '''
    Generate OTP and send it to the user's phone number
    This will fetch the phone number from the database
    '''
    pass #TODO: Implement this

@otp_router.post("/otp/phone/verify", response_model=bool)
async def verify_phone_otp(roll_no: str, otp: int):
    '''
    Generate OTP and send it to the user's phone number
    Fetch the phone number from the database
    '''
    pass #TODO: Implement this
