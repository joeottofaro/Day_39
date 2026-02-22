import os

import requests

SHEETY_AUTH = os.environ["SHEETY_AUTH"]
SHEETY_PRICES_ENDPOINT = os.environ["SHEETY_PRICES_ENDPOINT"]
SHEETY_USER_ENDPOINT = os.environ["SHEETY_USER_ENDPOINT"]


class DataManager:
    def __init__(self):
        self.sheety_endpoint = SHEETY_PRICES_ENDPOINT
        self.sheety_user_endpoint = SHEETY_USER_ENDPOINT
        self.sheety_headers = {
            "Authorization": SHEETY_AUTH
        }
        self.destination_data = {}
        self.customer_data = {}

    def get_destination_data(self):
        sheety_response = requests.get(SHEETY_PRICES_ENDPOINT, headers=self.sheety_headers)
        sheety_response.raise_for_status()
        data = sheety_response.json()
        self.destination_data = data["prices"]
        return self.destination_data

    def update_destination_codes(self):
        for city in self.destination_data:
            new_data = {
                "price": {
                    "iataCode": city["iataCode"]
                }
            }
            response = requests.put(
                url=f"{SHEETY_PRICES_ENDPOINT}/{city['id']}",
                json=new_data,
                headers=self.sheety_headers
            )
            response.raise_for_status()

    def get_customer_emails(self):
        response = requests.get(url=self.sheety_user_endpoint)
        data = response.json()
        # Name of spreadsheet 'tab' with the customer emails should be "users".
        self.customer_data = data["users"]
        return self.customer_data

