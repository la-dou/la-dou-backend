import pytest
import requests
from ..create_user import create_user
from ..login import login
from ..delete_user import delete_user


ENDPOINT = "http://localhost:8000"


def test_get_customer_rating():
    '''
    New users have no rating
    '''

    # Create a new user
    roll_no = 69696969
    create_user(roll_no)

    # Login the user
    _, login_data = login(roll_no)
    access_token = login_data["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Get the user's rating
    get_rating_response = requests.get(ENDPOINT + f"/rating/customer?roll_no={roll_no}", headers=headers)
    assert get_rating_response.status_code == 200
    get_rating_data = get_rating_response.json()

    # Check if the user's rating is 0
    assert get_rating_data["rating"] == 0

    delete_user(roll_no)