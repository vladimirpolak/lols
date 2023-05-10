import logging

from .headers import HeadersMixin

import time
import requests
from requests.exceptions import SSLError
from urllib3.exceptions import ProtocolError
import retry


class HttpClient(HeadersMixin):
    """
    Class responsible for HTTP communication.
    """
    def __init__(self,
                 session: requests.Session,
                 ):
        self._session = session

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, session: requests.Session):
        self._session = session

    def send_request(self, url, method, **kwargs) -> requests.Response:
        prepped_req = self._prepare_request(
            url=url,
            method=method,
            **kwargs
        )
        try:
            response = self._send_request(prepped_req, **kwargs)
        except requests.RequestException as e:
            logging.error(f"Failed accessing url '{url}' {e}")
            response = self.failed_response
        return response

    def _prepare_request(self, method: str, url: str, **kwargs) -> requests.PreparedRequest:
        headers = self.general_headers
        headers.update(kwargs.pop("headers", dict()))

        req = requests.Request(
            method=method,
            url=url,
            headers=headers,
            data=kwargs.pop("data", None),
            params=kwargs.pop("params", None),
            cookies=kwargs.pop("cookies", None)
        )
        return self._session.prepare_request(req)

    @retry.retry((requests.exceptions.RequestException, ProtocolError), tries=3, delay=3)
    def _send_request(self, prepared_request, **kwargs) -> requests.Response:
        try:
            res = self._session.send(
                request=prepared_request,
                stream=kwargs.get("stream", None),
                allow_redirects=kwargs.get("allow_redirects", True),
                verify=kwargs.get("verify", True)
            )
        except SSLError:
            res = self._session.send(
                request=prepared_request,
                stream=kwargs.get("stream", None),
                allow_redirects=kwargs.get("allow_redirects", True),
                verify=False
            )

        # Timeout in case of rate limiting
        if res.status_code == 429:
            retry_after = int(res.headers.get('Retry-After', 0))
            if retry_after:
                time.sleep(retry_after)
                raise requests.exceptions.RequestException()
        return res

    @property
    def failed_response(self) -> requests.Response:
        response = requests.Response()
        response.status_code = 500
        response.reason = "Internal Server Error"
        response._content = b"An error occurred while making the request"
        return response

    def update_cookies(self, cookies: dict, domain: str):
        for k, v in cookies.items():
            self._session.cookies.set(k, v, domain=domain)
