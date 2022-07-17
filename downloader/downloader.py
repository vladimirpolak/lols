import requests
from pathlib import Path
from .headers import HeadersMixin
from collections import ChainMap
import logging


class Downloader(HeadersMixin):
    _session: requests.Session

    def set_session(self, session: requests.Session):
        self._session = session

    def get_page(self,
                 url_or_request,
                 headers: dict = None,
                 data: dict = None,
                 params: dict = None,
                 cookies: dict = None
                 ) -> requests.Response:
        if isinstance(url_or_request, str):
            return self._get_page(url_or_request, headers, data, params, cookies)
        elif isinstance(url_or_request, requests.Request):
            return self.send_request(url_or_request)

    def send_request(self, req: requests.Request) -> requests.Response:
        prepped = self._session.prepare_request(req)

        resp = self._session.send(prepped)
                      # stream=stream,
                      # verify=verify,
                      # proxies=proxies,
                      # cert=cert,
                      # timeout=timeout
        return resp

    def _get_page(self,
                  url: str,
                  headers: dict = None,
                  data: dict = None,
                  params: dict = None,
                  cookies: dict = None
                  ) -> requests.Response:
        request = {"url": url}
        if not headers:
            headers = self.general_headers
        else:
            headers = ChainMap(headers, self.general_headers)
        request["headers"] = headers

        if data:
            request["data"] = data
        if params:
            request["params"] = params
        if cookies:
            request["cookies"] = cookies

        try:
            r = self._session.get(**request)
        except requests.exceptions.RequestException as e:
            logging.error(e, url)
            raise e
        else:
            if r.status_code >= 300:
                logging.error(f"STATUS CODE: {r.status_code} FOR PAGE: {url}")
            return r

    def _create_request(self,
                        method: str,
                        url: str,
                        headers: dict = None,
                        data: dict = None,
                        params: dict = None,
                        cookies=None
                        ) -> requests.Request:
        if headers:
            headers = ChainMap(self.general_headers, headers)

        return requests.Request(
            method=method,
            url=url,
            headers=headers,
            data=data,
            params=params,
            cookies=cookies
        )

    def download_file(self):
        pass

    def update_cookies(self, cookies: dict, domain: str):
        for k, v in cookies.items():
            self._session.cookies.set(k, v, domain=domain)

    def create_output_directory(self, output_folder_path: Path):
        """Creates main Output directory along with target model directory."""
        if not output_folder_path.exists():
            output_folder_path.mkdir()



