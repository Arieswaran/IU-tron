import datetime
import requests

CURRENT_TOKEN = None
def get_auth_token():
    url = "https://login.kekademo.com/connect/token"

    payload = {
        "grant_type": "kekaapi",
        "scope": "kekaapi",
        "client_id": "a",
        "client_secret": "a",
        "api_key": "a"
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded"
    }

    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(response.status_code)
    return None


def get_all_leave_requests():

    url = "https://firefox.kekademo.com/api/v1/time/leaverequests"

    payload={}
    headers = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        return response.json()
    else:
        print(response.status_code)
    return None

