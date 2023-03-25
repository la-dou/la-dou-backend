from typing import List, Optional
from pydantic import BaseModel, Field

class VerifyOTP(BaseModel):
    otp: int = Field(..., description="otp to verify")
    roll_no: str = Field(..., description="roll number of the user")
