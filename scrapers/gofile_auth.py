from config import Manager as Config
from exceptions import ScraperInitError
from datetime import datetime
import logging

GOFILE_TOKEN_REQ_URL = "https://api.gofile.io/createAccount"


def token_is_valid(date: datetime):
    """Invalid token if current is older than 24 hours."""
    difference = datetime.now() - date
    return difference.days == 0


class GoFileAuth:
    """GoFile Authorization mixin."""
    ACCESS_TOKEN = ""

    def authorize(self):
        auth_data = config.load_config(self.DOMAIN)

        if not auth_data:
            self._create_login()
        else:
            self.ACCESS_TOKEN = auth_data["token"]
            date_created = auth_data["created_at"]

            if not token_is_valid(date_created):
                self._create_login()
            else:
                self.load_cookies(token=self.ACCESS_TOKEN)

    def _create_login(self):
        self.ACCESS_TOKEN = self.request_token()
        self.load_cookies(token=self.ACCESS_TOKEN)

        auth_data = {
            "token": self.ACCESS_TOKEN
        }
        config.save_config(
            self.DOMAIN,
            auth_data
        )

    def request_token(self):
        """Method for requesting new GoFile access token."""
        logging.debug("Requesting GoFile access token.")

        # Create guest account URL
        response = self.request(
            method='GET',
            url=GOFILE_TOKEN_REQ_URL
        )

        if response.status_code == 200:
            json = response.json()
            if json["status"] == "ok":
                # Extract access token
                token = json["data"]["token"]
                logging.debug(f"New GoFile token: {token}")
                return token
            raise ScraperInitError(f"Failed to retrieve access token from data: {json}")
        logging.debug(response)
        raise ScraperInitError(f"Failed to retrieve access token, response code: {response.status_code}")

    def load_cookies(self, token):
        self._downloader.update_cookies(
            cookies={"accountToken": token},
            domain=self.DOMAIN
        )
