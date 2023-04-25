import pytest
import requests
import json
# import sys
# sys.path.append("../")
# from tests.login_for_test import login

def login():
    head = {"Content-Type": "application/x-www-form-urlencoded"}
    auth_info = {"username": "24100101", "password": "test_password"}
    response = requests.post(ENDPOINT + "/login", data=auth_info, headers=head)
    response = json.loads(response.text)
    return response

ENDPOINT = "http://localhost:8000"

def test_login_userexists():
    response = login()
    print() # Skipping Line
    print(response)

def test_login_usernotexist():
    head = {"Content-Type": "application/x-www-form-urlencoded"}
    auth_info = {"username": "0", "password": "test_password"}
    response = requests.post(ENDPOINT + "/login", data=auth_info, headers=head)
    print() # Skipping Line
    response = json.loads(response.text)
    print(response)