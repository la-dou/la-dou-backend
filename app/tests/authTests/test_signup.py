import pytest
import requests
import random

ENDPOINT = "http://localhost:8000"

def test_signup():
    roll_no = 2000
    payload =   {
        "roll_no": roll_no,
        "password": "test_password",
        "role": "customer",
        "name": "Usman Jehangir",
        "gender": "Male",
        "phone_number": "03206850001",
        "email_verified": False,
        "phone_verified": False,
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
    # print("PAYLOAD: ", payload)
    create_response = requests.post(ENDPOINT + "/signup", json=payload)
    assert create_response.status_code == 200
    create_data = create_response.json()
    # print("CREATE DATA: ", create_data)
    delete_response = requests.get(ENDPOINT + f"/delete/user/{roll_no}")
    assert delete_response.status_code == 200
    delete_data = delete_response.json()
    # print("DELETE DATA: ", delete_data)

