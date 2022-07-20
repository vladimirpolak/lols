from config import Manager as config
from exceptions import ScraperInitError
from datetime import datetime
import logging

GOFILE_TOKEN_REQ_URL = "https://api.gofile.io/createAccount"
GOFILE_CONTENT_URL = "https://api.gofile.io/getContent"


class GoFileAuth:
    """GoFile Authorization mixin."""
    ACCESS_TOKEN = ""

    def login(self):
        auth_data = config.load_config(self.DOMAIN)

        if not auth_data:
            self._create_login()
            return self.ACCESS_TOKEN

        self.ACCESS_TOKEN = auth_data["token"]
        date_created = auth_data["created_at"]

        if not self.token_is_valid(date_created):
            self._create_login()
        return self.ACCESS_TOKEN

    def _create_login(self):
        self.ACCESS_TOKEN = self.request_token()

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
        req = self._downloader._create_request(method='GET', url=GOFILE_TOKEN_REQ_URL)
        r = self._send_request_object(req)

        if r.status_code == 200:

            json = r.json()
            if json["status"] == "ok":
                # Extract access token
                token = json["data"]["token"]

                logging.debug(f"New GoFile token: {token}")
                return token
            raise ScraperInitError(f"Failed to retrieve access token from data: {json}")
        logging.debug(r)
        raise ScraperInitError(f"Failed to retrieve access token, response code: {r.status_code}")

    @classmethod
    def token_is_valid(cls, date):
        """Invalid token if current is older than 24 hours."""
        difference = datetime.now() - date
        return difference.days == 0


def gf_query_params(album_id, token):
    """Query parameters for GoFile 'getContent' URL."""
    query_params = {
        "contentId": album_id,
        "token": token,
        "websiteToken": "12345"
    }
    return query_params