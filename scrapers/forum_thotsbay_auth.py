from config import Manager as config
from urllib.parse import urlencode
from exceptions import ScraperInitError
import logging
import re


class ForumThotsbayAuth:
    def authorize(self):
        auth_data = config.load_config(self.DOMAIN)

        if not auth_data:
            # Create new file with username, password fields to fill in
            self._save_auth(
                username="",
                password="",
            )
            raise ScraperInitError(f"New config file for {self.DOMAIN} was created, fill in the login details!")
        else:
            self.username = auth_data["username"]
            self.password = auth_data["password"]
            cookies = auth_data["cookies"]

            #if not cookies:
            self._new_login()

        print(auth_data)
        exit()
        self._new_login()

    def _new_login(self):
        index_page_token = self._index_page()
        pre_login_token = self._pre_login_page(index_page_token)
        self._login_page(pre_login_token)

    def _index_page(self):
        """Access index page and extract 'xf' token."""
        response = self._request_page(
            url=self.base_url
        )
        html = response.text

        pattern = re.compile('data-csrf="(.*?)" ')
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

        response = self._request_page(
            url=self.base_url + "login/",
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

    def _login_page(self, pre_login_token):
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

        req = self._downloader._create_request(
            method='POST',
            url=self.base_url + "login/login/",
            data=login_payload,
            headers=headers
        )
        response = self._send_request_object(req)
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
            f"\nCSRF Token: {xf_token}"
            f"\nSession id: {session_id}"
            f"\nUser id: {user_id}"
        )
        self._save_auth(
            username=self.username,
            password=self.password,
            xf_token=xf_token,
            session_id=session_id,
            user_id=user_id
        )

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
        config.save_config(
            domain_name=self.DOMAIN,
            data=data
        )