import os
from datetime import datetime
import requests

AMADEU_ENDPOINT = "https://test.api.amadeus.com"


class FlightSearch:
    """
    Initialize an instance of the FlightSearch class.
    This constructor performs the following tasks:
    1. Retrieves the API key and secret from the environment variables 'AMADEUS_API_KEY'
    and 'AMADEUS_SECRET' respectively.
    Instance Variables:
    _api_key (str): The API key for authenticating with Amadeus, sourced from the .env file
    _api_secret (str): The API secret for authenticating with Amadeus, sourced from the .env file.
    _token (str): The authentication token obtained by calling the _get_new_token method.
    """
    def __init__(self):
        self.amadeu_api_key = os.environ["AMADEU_API_KEY"]
        self.amadeu_api_secret = os.environ["AMADEU_API_SECRET"]
        self.token = self.get_auth_token()

    def get_auth_token(self):
        """
        Generates the authentication token used for accessing the Amadeus API and returns it.
        This function makes a POST request to the Amadeus token endpoint with the required
        credentials (API key and API secret) to obtain a new client credentials token.
        Upon receiving a response, the function updates the FlightSearch instance's token.
        Returns:
            str: The new access token obtained from the API response.
        """
        token_endpoint = f"{AMADEU_ENDPOINT}/v1/security/oauth2/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.amadeu_api_key,
            "client_secret": self.amadeu_api_secret
        }
        response = requests.post(url=token_endpoint, data=payload, headers=headers)
        response.raise_for_status()
        token = response.json()["access_token"]
        return token

    def get_destination_code(self, city_name):
        """
        Retrieves the IATA code for a specified city using the Amadeus Location API.
        Parameters:
        city_name (str): The name of the city for which to find the IATA code.
        Returns:
        str: The IATA code of the first matching city if found; "N/A" if no match is found due to an IndexError,
        or "Not Found" if no match is found due to a KeyError.
        The function sends a GET request to the IATA_ENDPOINT with a query that specifies the city
        name and other parameters to refine the search. It then attempts to extract the IATA code
        from the JSON response.
        - If the city is not found in the response data (i.e., the data array is empty, leading to
        an IndexError), it logs a message indicating that no airport code was found for the city and
        returns "N/A".
        - If the expected key is not found in the response (i.e., the 'iataCode' key is missing, leading
        to a KeyError), it logs a message indicating that no airport code was found for the city
        and returns "Not Found".
        """
        iata_endpoint = f"{AMADEU_ENDPOINT}/v1/reference-data/locations/cities"
        parameters = {
            "keyword": city_name,
            "max": 2,
            "include": "AIRPORTS",
        }
        headers = {
            "Authorization": f"Bearer {self.token}"
        }
        try:
            response = requests.get(url=iata_endpoint, params=parameters, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        else:
            try:
                code = response.json()["data"][0]['iataCode']
            except IndexError:
                print(f"IndexError: No airport code found for {city_name}.")
                return "N/A"
            except KeyError:
                print(f"KeyError: No airport code found for {city_name}.")
                return "Not Found"

            return code

    def check_flights(self, origin_city_code, destination_city_code, from_time, to_time, is_direct=True):
        """
        Searches for flight options between two cities on specified departure and return dates
        using the Amadeus API.

        Parameters:
            is_direct (bool): True for non-stop flights.
            origin_city_code (str): The IATA code of the departure city.
            destination_city_code (str): The IATA code of the destination city.
            from_time (datetime): The departure date.
            to_time (datetime): The return date.

        Returns:
            dict or None: A dictionary containing flight offer data if the query is successful; None
            if there is an error.

        The function constructs a query with the flight search parameters and sends a GET request to
        the API. It handles the response, checking the status code and parsing the JSON data if the
        request is successful. If the response status code is not 200, it logs an error message and
        provides a link to the API documentation for status code details.
        """
        url = f"{AMADEU_ENDPOINT}/v2/shopping/flight-offers"
        headers = {
            "Authorization": f"Bearer {self.get_auth_token()}"
        }
        parameters = {
            "originLocationCode": origin_city_code,
            "destinationLocationCode": destination_city_code,
            "departureDate": from_time.strftime("%Y-%m-%d"),
            "returnDate": to_time.strftime("%Y-%m-%d"),
            "adults": 1,
            "nonStop": "true" if is_direct else "false",
            "currencyCode": "EUR",
            "max": "10",
        }
        response = requests.get(url, headers=headers, params=parameters)
        response.raise_for_status()
        if response.status_code != 200:
            print(f"check_flights() response code: {response.status_code}")
            print("There was a problem with the flight search.\n"
                  "For details on status codes, check the API documentation:\n"
                  "https://developers.amadeus.com/self-service/category/flights/api-doc/flight-offers-search/api"
                  "-reference")
            print("Response body:", response.text)
            return None

        return response.json()
