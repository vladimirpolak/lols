from config import Manager as Config
from urllib.parse import urlencode
from exceptions import ScraperInitError
import logging
import re

XfToken = str
XfSession = str
XfUser = str


class ForumThotsbayAuth:
    def authorize(self):
        auth_data = Config.load_config(self.DOMAIN)

        # If there isnt an auth file
        # create new file with username, password fields to fill in
        if not auth_data:
            self._save_auth(
                username="",
                password="",
            )
            raise ScraperInitError(f"New config file for {self.DOMAIN} was created, fill in the login details!")

        # With existing file
        else:
            self.username = auth_data["username"]
            self.password = auth_data["password"]

            # Parse existing cookies
            cookies = auth_data["cookies"]
            xf_token = cookies["xf_csrf"]
            session_id = cookies["xf_session"]
            user_id = cookies["xf_user"]

            # If some/all cookie values are missing
            if not (xf_token and session_id and user_id):
                # If there is no login information, raise an error
                if not (self.username and self.password):
                    raise ScraperInitError(f"You need to provide login information for {self.DOMAIN}!")
                # Create new login session with existing login information
                else:
                    self._new_login()

            # Load up existing cookies into current session
            else:
                logging.info(f"Using saved auth cookies for {self.DOMAIN}: {cookies}")
                self._downloader.update_cookies(
                    cookies=cookies,
                    domain=self.DOMAIN
                )

    def _new_login(self):
        index_page_token = self._index_page()
        pre_login_token = self._pre_login_page(index_page_token)
        xf_token, session_id, user_id = self._login_page(pre_login_token)

        self._save_auth(
            username=self.username,
            password=self.password,
            xf_token=xf_token,
            session_id=session_id,
            user_id=user_id
        )
        return xf_token, session_id, user_id

    def _index_page(self):
        """Access index page and extract 'xf' token."""
        response = self.request(
            url=self.base_url
        )
        html = response.text

        pattern = re.compile('data-csrf="(.*?)"')
        try:
            results = pattern.findall(html)
            token = results[0]
            return token
        except IndexError:
            raise ScraperInitError(f"Failed to extract csrf token from index page.")

    def _pre_login_page(self, index_page_token: str):
        """Access pre-login page and extract next 'xf' token."""
        headers = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            "x-requested-with": "XMLHttpRequest",
            "referer": "https://forum.thotsbay.com/"
        }

        pre_login_params = {
            "_xfRequestUri": "/forum/",
            "_xfWithData": "1",
            "_xfToken": index_page_token,
            "_xfResponseType": "json"
        }

        response = self.request(
            url=self.base_url + "/login/",
            headers=headers,
            params=pre_login_params
        )

        json_body = response.json()
        if json_body["status"] == "ok":
            html = json_body["html"]["content"]
            pattern = re.compile('<input type="hidden" name="_xfToken" value="(.*?)" />')
            try:
                match = pattern.findall(html)
                xf_token = match[0]
                return xf_token
            except KeyError:
                pass
        raise ScraperInitError("Failed to extract 'xf_token' from pre-login page.")

    def _login_page(self, pre_login_token) -> (XfToken, XfSession, XfUser):
        """Login with user credentials and obtain 'xf_user' and 'xf_session' tokens."""
        login_payload = {
            "login": self.username,
            "password": self.password,
            "remember": "1",
            "_xfRedirect": self.base_url,
            "_xfToken": pre_login_token
        }
        query_string = urlencode(login_payload)

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "content-type": "application/x-www-form-urlencoded",
            "content-length": str(len(query_string)),
            "origin": self.base_url,
            "referer": self.base_url
        }

        response = self.request(
            method='POST',
            url=self.base_url + "/login/login/",
            data=login_payload,
            headers=headers
        )
        logging.debug(f"Login response status code: {response.status_code}")

        cookies = dict(self._downloader._session.cookies)
        logging.debug(f"Session cookies: {cookies}")

        try:
            xf_token = cookies["xf_csrf"]
            session_id = cookies["xf_session"]
            user_id = cookies["xf_user"]
        except KeyError:
            raise ScraperInitError(
                f"Failed to create login session, check if the login information is correct."
            )

        logging.info(
            f"Created new login session."
            f"CSRF Token: {xf_token}"
            f"Session id: {session_id}"
            f"User id: {user_id}"
        )
        return xf_token, session_id, user_id

    def _save_auth(self,
                   username: str,
                   password: str,
                   xf_token: str = "",
                   session_id: str = "",
                   user_id: str = ""
                   ):
        data = {
            "username": username,
            "password": password,
            "cookies": {
                "xf_csrf": xf_token,
                "xf_session": session_id,
                "xf_user": user_id
            }
        }
        Config.save_config(
            domain_name=self.DOMAIN,
            data=data
        )