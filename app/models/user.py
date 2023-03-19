from uuid import UUID
from typing import List
from pydantic import BaseModel, Field
from .customer import Customer
from .driver import Driver



class UserAuth(BaseModel):
    roll_no: int = Field(..., description="user roll number")
    password: str = Field(..., min_length=5, max_length=24, description="user password")
    role: str = Field(..., description="user role")

class UserSignup(UserAuth):
    name : str = Field(..., description="user name")
    gender: str
    phone_number: str = Field(..., description="user phone number")
    

class UserOut(BaseModel):
    id: UUID
    roll_no: int


class SystemUser(UserOut):
    role: str
    password: str
    
class User(UserOut):
    name: str
    password: str
    phone_number: str
    gender: str
    email_verified: bool
    phone_verified: bool
    fcm_registration_token: List[str]
    customer: Customer
    driver: Driver
    
    