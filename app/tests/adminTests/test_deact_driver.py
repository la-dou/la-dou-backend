import pytest
import requests
import json
from ..admin_login import admin_login
from ..create_user import create_user
from ..delete_user import delete_user

ENDPOINT = "http://localhost:8000"

def test_deactivate_driver():
    roll_no = 24100250
    login_response = admin_login()
    create_response = create_user(roll_no)
    access_token = login_response["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(ENDPOINT + f"/admin/toggle/driver?roll_no=24100250", headers=headers)
    data = response.json()
    assert response.status_code == 200
    assert data == True
    delete_response = delete_user(roll_no)
    