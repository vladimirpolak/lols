from collections import ChainMap


class HeadersMixin:
    @property
    def general_headers(self):
        return {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
            "accept-encoding": "gzip, deflate, utf-8",
            "accept-language": "en-US,en;q=0.9",
        }
