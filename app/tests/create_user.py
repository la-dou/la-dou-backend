import requests
import json

ENDPOINT = "http://localhost:8000"

def create_user(roll_no):
    payload =   {
        "roll_no": roll_no,
        "password": "test_password",
        "role": "customer",
        "name": f"Usman Javed {roll_no}",
        "gender": "Male",
        "phone_number": "03001234567",
        "email_verified": True,
        "phone_verified": True,
        "fcm_device_token": [],
        "customer": {
            "deactivated": False,
            "rating": {
            "sum": 0,
            "count": 0
            },
            "orders": []
        },
        "driver": {
            "deactivated": False,
            "rating": {
            "sum": 0,
            "count": 0
            },
            "orders": []
        }
    }
    create_response = requests.post(ENDPOINT + "/signup", json=payload)
    create_data = create_response.json()
