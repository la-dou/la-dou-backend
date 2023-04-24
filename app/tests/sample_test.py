import pytest
import requests

ENDPOINT = "http://localhost:8000"

# Write a dummy test to make sure the test runner is working
def test_root():
    response = requests.get(ENDPOINT)
    print(response)
    assert response.status_code == 200
    data = response.json()
    pass