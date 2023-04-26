import pytest
import requests
import json
from ..login import login

ENDPOINT = "http://localhost:8000"

def test_login_userexists():
    response, data = login(24100101)
    assert response.status_code == 200
    assert data["access_token"] != None

def test_login_usernotexist():
    head = {"Content-Type": "application/x-www-form-urlencoded"}
    auth_info = {"username": "50", "password": "test_password"}
    response = requests.post(ENDPOINT + "/login", data=auth_info, headers=head)
    assert response.status_code == 404
    response = json.loads(response.text)
    assert response["detail"] == "Roll Number not found"