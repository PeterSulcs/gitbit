from dotenv import load_dotenv, set_key
import os
PATH_TO_ENV = os.path.join('.', '.env')
load_dotenv(PATH_TO_ENV)
from requests.auth import AuthBase
import requests
from datetime import datetime, timedelta
from tqdm import tqdm
from time import sleep


class BearerTokenAuth(AuthBase):
    """Implements a custom authentication scheme."""

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        """Attach an API token to a custom auth header."""
        r.headers['Authorization'] = f'Bearer {self.token}'  # Python 3.6+
        return r

class GitBit(object):
    """
    Connect to FitBit API
    """
    def __init__(self, max_retries: int = 5):
        self.token = os.getenv("TOKEN")
        self.refresh_token = os.getenv("REFRESH_TOKEN")
        self.client_id = os.getenv("CLIENT_ID")
        self.client_secret = os.getenv("CLIENT_SECRET")
        self.callback_url = os.getenv("CALLBACK_URL")
        self.refresh_token_url = os.getenv("REFRESH_TOKEN_URL")
        self.MAX_RETRIES = max_retries

    def get_token(self):
        """
        Call when you only have client_is and client_secret to get tokens
        """
        pass

    def get_new_token(self):
        """
        This will fetch a new token.
        """
        # curl	-X POST -i 
        # -H "Authorization: Basic <SECRET>" 
        # -H "Content-Type: application/x-www-form-urlencoded" 
        # -d "grant_type=refresh_token" 
        # -d "refresh_token=<SECRET>"
        # https://api.fitbit.com/oauth2/token

        response = requests.post(url=self.refresh_token_url, data={"grant_type": "refresh_token", 
                            "refresh_token": self.refresh_token}, auth=(self.client_id, self.client_secret))

        print(type(response))
        print(response)
        if response.ok:
            response_json = response.json()
            self.token = response_json['access_token']
            self.refresh_token = response_json['refresh_token']
            # Set the values in the .env file
            set_key(dotenv_path=PATH_TO_ENV, key_to_set="ACCESS_TOKEN", value_to_set=self.token)
            set_key(dotenv_path=PATH_TO_ENV, key_to_set="REFRESH_TOKEN", value_to_set=self.refresh_token)


    def call_endpoint(self, url):
        """
        Call a specific endpoint expecting JSON response.
        Try up to self.MAX_RETRIES with a reauthentication in between.
        """
        n = 0
        success = False
        while (n < self.MAX_RETRIES):
            with requests.session() as session:
                session.auth = BearerTokenAuth(self.token)
                d = session.get(url)
            if d.ok:
                return d.json()
            elif d.status_code == 429:
                print(f"You are being rate limited. waiting: {d.headers['Fitbit-Rate-Limit-Reset']} seconds...")
                for second in tqdm(range(0, int(d.headers['Fitbit-Rate-Limit-Reset']))):
                    sleep(1)
                n = 0
                print(f"Retrying after waiting for rate limit reset...")
            else:
                n += 1
                print(f"Retrying after status code of {d.status_code}... Try number: {n}")
                self.get_new_token()
                
        print(f"Request to {url} failed completely... with content: {d.content}, headers: {d.headers} ")

    def get_heart_rate_data(self, date_string, resolution: str = "1min"):
        """
        Get 1min resolution for datestr specified as YYYY-MM-DD
        """
        assert(resolution in {"1min", "1sec"})
        return self.call_endpoint(url=f'https://api.fitbit.com/1/user/-/activities/heart/date/{date_string}/1d/{resolution}.json')


def date_to_string(date_object):
    """
    Accepts a Python datetime object, converts to date format "YYYY-MM-DD"
    """
    return datetime.strftime(date_object, "%Y-%m-%d")

def string_to_date(string):
    """
    Accepts a date as a string ("YYYY-MM-DD") and converts to Python datetime object.
    """
    return datetime.strptime(string, "%Y-%m-%d")

def generate_date_range(start, end=date_to_string(datetime.today())):
    """
    Generate dates from start date specified as string to end date specified as string
    "YYYY-MM-DD".
    """
    start_date = string_to_date(start)
    end_date = string_to_date(end)

    current_date = string_to_date(start)

    while current_date <= end_date:
        yield date_to_string(current_date)
        current_date += timedelta(days=1)

    

