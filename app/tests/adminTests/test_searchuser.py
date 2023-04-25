import pytest
import requests
import json

ENDPOINT = "http://localhost:8000"

def admin_login():
    head = {"Content-Type": "application/x-www-form-urlencoded"}
    auth_info = {"username": "0", "password": "super_secret"}
    response = requests.post(ENDPOINT + "/login", data=auth_info, headers=head)
    response = json.loads(response.text)
    return response

def test_search_user():
    login_response = admin_login()
    print() # Skipping Line
    print(login_response)
    access_token = login_response["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(ENDPOINT + f"/admin/search?search=24100101", headers=headers)
    print(response.json())
    data = response.json()
    assert response.status_code == 200
    assert data[0]["name"] == "Usman Jehangir"
    assert data[0]["roll_no"] == 24100101

