from ._scraper_base import ExtractorBase, CrawlerBase
from downloader.types import determine_content_type_, img_extensions, vid_extensions
from exceptions import ExtractionError, ScraperInitError
from config import Manager as config
from utils import split_filename_ext
from urllib.parse import urlencode
import logging
import re
import json

# All constant URLs here

PATTERN_THOTSBAYFORUM_THREAD = r"(?:https://)?forum\.thotsbay\.com/threads/[-\w\d\.]+/"


class ForumThotsbayAuth:
    def login(self):
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
        # headers = self.sexyegirls_index_headers

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
             "origin": self.base_url
        }

        req = self._downloader._create_request(
            method='POST',
            url=self.base_url + "login/login/",
            data=login_payload,
            headers=headers
        )
        response = self._send_request_object(req)
        print(f"Response cookies: {dict(response.cookies)}")

        cookies = dict(self._downloader._session.cookies)
        print(f"Session cookies: {cookies}")

        xf_token = cookies["xf_csrf"]
        session_id = cookies["xf_session"]
        user_id = cookies["xf_user"]

        logging.debug(
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


class ForumThotsbayCrawler(CrawlerBase, ForumThotsbayAuth):
    VALID_URL_RE = re.compile(r"")
    PROTOCOL = "https"
    DOMAIN = "forum.thotsbay.com"
    DESC = "Thotsbay Forum Thread"
    CONTENT_TYPE = "THREAD"
    SAMPLE_URLS = [
        "https://forum.thotsbay.com/threads/nataliexking-bbyluckie.12408/#post-337758",
        "https://forum.thotsbay.com/threads/abby-rao-abbyrao.10221/",
        "https://forum.thotsbay.com/threads/genesis-mia-lopez.24/",
        "https://forum.thotsbay.com/threads/angelie-dolly.13727/",
        "https://forum.thotsbay.com/threads/kelly-kay.14707/"
    ]

    def initialize(self):
        self.login()

    # Extractor method
    # def _extract_data(self, url):
    #     response = self._request_page(
    #         url=url,
    #     )
    #
    #     self.add_item(
    #         content_type=content_type,
    #         filename=filename,
    #         extension=extension,
    #         source=source,
    #         album_title=album_title
    #     )

    # Extractor method only
    # @classmethod
    # def _extract_from_html(cls, html):
    #     return [data for data in set(re.findall(cls.VALID_URL_RE, html))]

    # Crawler method only
    # def _crawl_link(self, url) -> html[str]:
    #     pass
