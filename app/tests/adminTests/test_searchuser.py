import pytest
import requests
import json
from ..admin_login import admin_login

ENDPOINT = "http://localhost:8000"

def test_search_user():
    login_response = admin_login()
    access_token = login_response["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(ENDPOINT + f"/admin/search?search=24100101", headers=headers)
    data = response.json()
    assert response.status_code == 200
    assert data[0]["name"] == "Usman Jehangir"
    assert data[0]["roll_no"] == 24100101

