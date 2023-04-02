from typing import List, Optional
from pydantic import BaseModel, Field
from .customer import Customer
from .driver import Driver
from typing import Optional


class UserAuth(BaseModel):
    roll_no: int = Field(..., description="user roll number")
    password: str = Field(..., min_length=5, max_length=24,
                          description="user password")
    role: Optional[str] = Field(None, description="user role")


class UserSignup(UserAuth):
    name: str = Field(..., description="user name")
    gender: str
    phone_number: str = Field(..., description="user phone number")
    email_verified: bool = False
    phone_verified: bool = False
    fcm_device_token: List[str] = []
    customer: Customer = None
    driver: Driver = None


class UserOut(BaseModel):
    name: str
    roll_no: int
    role: Optional[str]
    phone_number: str
    email_verified: Optional[bool]
    phone_verified: Optional[bool]
    driver_disabled: Optional[bool]
    customer_disabled: Optional[bool]


class SystemUser(UserOut):
    password: str


class User(UserOut):
    password: str
    gender: str
    email_verified: bool = False
    phone_verified: bool = False
    fcm_device_token: List[str] = []
    customer: Customer = None
    driver: Driver = None


class PasswordReset(BaseModel):
    roll_no: int = Field(..., description="roll number of the user")
    verification_token: str = Field(...,
                                    description="verification token for the user")
    password: str = Field(..., description="new password for the user")


class PasswordUpdate(BaseModel):
    old_password: str = Field(..., description="old password of the user")
    new_password: str = Field(..., description="new password for the user")


class PhoneUpdate(BaseModel):
    phone_number: str = Field(..., description="new phone number for the user")
    old_password: str = Field(..., description="old password of the user")
