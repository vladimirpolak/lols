# ------------------------------------------------- DEPRICATED -----------------------------------------------------
# import requests
#
# from ._scraper_base import ExtractorBase
# from downloader.types import (determine_content_type,
#                             img_extensions,
#                             vid_extensions,
#                             archive_extensions,
#                             ContentType,
#                             ContentTypeError)
# from exceptions import ExtractionError
# from utils import split_filename_ext
# from typing import Union
# import yarl
# import logging
# import re
# import json
#
# # Constant URLs
# STREAM_URL = "https://media-files{server_num}.bunkr.is"
#
# # Regex Patterns
# PATTERN_BUNKR_ALBUM = r"((?:https?://)?bunkr\.[a-z]+/a/\w+)"
# PATTERN_BUNKR_ALBUM_DATA_SCRIPT = r'<script id="__NEXT_DATA__" type="application/json">(?P<json>\{.*?})</script>'
# PATTERN_BUNKR_VIDEO = rf"((?:https?://)(?:stream|media-files|cdn)\d*\.bunkr\.[a-z]+/(?:v/)?[-~%\w]+(?:{'|'.join(vid_extensions)}))"
# PATTERN_BUNKR_IMAGE = rf"((?:https://)?cdn\d+\.bunkr\.[a-z]+/[-\w]+(?:{'|'.join(img_extensions)}))"
# PATTERN_BUNKR_ARCHIVE = rf"((?:https://)?cdn\d+\.bunkr\.[a-z]+/[-\w]+(?:{'|'.join(archive_extensions)}))"
#
#
# def extract_server_number(url: str) -> str:
#     pattern = re.compile(r"(?:cdn|stream|i|media-files)(?P<server_num>\d+)\.bunkr\.is")
#     match = re.search(pattern, url)
#     if match:
#         return match.group("server_num")
#     return ""
#
#
# def fallback_pageprops(domain: str, build_id: str, album_path: str) -> str:
#     """
#     Creates fallback fetch URL for page props (content).
#     """
#     return "https://" + domain + "/_next/data/" + build_id + album_path + '.json'
#
#
# def parse_fallback_response(res: requests.Response) -> dict:
#     if res.status_code != 200:
#         raise ExtractionError("Failed to fetch data with fallback URL.")
#     json_ = res.json()
#     return json_["pageProps"]
#
#
# class BunkrAlbumExtractor(ExtractorBase):
#     VALID_URL_RE = re.compile(PATTERN_BUNKR_ALBUM)
#     PROTOCOL = "https"
#     DOMAIN = "bunkr.is"
#     DESC = "Bunkr.is Album"
#     CONTENT_TYPE = "ALBUM"
#
#     def _extract_data(self, url):
#         self.url = url
#         response = self.request(
#             url=self.url,
#             headers={
#                 "accept": "application/signed-exchange;v=b3;q=0.9"
#             }
#         )
#         html = response.text
#         data = self._extract_data_tag(html)
#
#         if data and not data["isFallback"]:
#             page_props = data["props"]["pageProps"]
#         else:
#             page_props = self._fallback_method(build_id=data['buildId'])
#
#         self._parse_page_props(page_props)
#
#     def _extract_data_tag(self, html):
#         """Returns data in json format"""
#         pattern = re.compile(PATTERN_BUNKR_ALBUM_DATA_SCRIPT)
#         data_tag = re.search(pattern, html)
#         if not data_tag:
#             raise ExtractionError(
#                 f"Didn't find data tag on page {self.url}."
#             )
#
#         return json.loads(data_tag.group('json'))
#
#     def _parse_page_props(self, page_props: dict):
#         self.title = self._get_title(page_props)
#         files = self._get_album_files(page_props)
#
#         for item in files:
#             self._parse_item(item)
#
#     @staticmethod
#     def _get_title(page_props):
#         try:
#             title = page_props['album']['name']
#         except KeyError:
#             raise ExtractionError(f"Failed to extract album title. Data: {page_props}")
#         else:
#             return title
#
#     @staticmethod
#     def _get_album_files(page_props):
#         try:
#             files = page_props['album']['files']
#         except KeyError:
#             raise ExtractionError(f"Failed to extract album files. Data: {page_props}")
#         else:
#             return files
#
#     def _parse_item(self, item: dict):
#         album_title = self.title
#         file_w_extension = item['name']
#         filename, extension = split_filename_ext(file_w_extension)
#         try:
#             content_type = determine_content_type(extension)
#         except ContentTypeError:
#             logging.error(
#                 f"Error parsing data for bunkr.\n"
#                 f"Data to parse: {item}"
#             )
#         else:
#             source = None
#             if content_type == ContentType.IMAGE:
#                 source = f"{item['i']}/{file_w_extension}"
#             elif content_type == ContentType.VIDEO:
#                 server_num = extract_server_number(item['cdn'])
#                 source = f"{STREAM_URL.format(server_num=server_num)}/{file_w_extension}"
#             elif content_type == ContentType.AUDIO:
#                 source = f"{item['cdn']}/{file_w_extension}"
#             elif content_type == ContentType.ARCHIVE:
#                 source = f"{item['cdn']}/{file_w_extension}"
#
#             if source:
#                 self.add_item(
#                     content_type=content_type,
#                     filename=filename,
#                     extension=extension,
#                     source=source,
#                     album_title=album_title
#                 )
#
#     def _fallback_method(self, build_id: str) -> dict:
#         """
#         Transform the album URL into URL that fetches album's data in json format
#
#         :param build_id:
#         :return: dict
#         """
#         url = yarl.URL(self.url)
#         pageprops_url = fallback_pageprops(domain=url.host, build_id=build_id, album_path=url.path)
#         return parse_fallback_response(self.request(pageprops_url))
#
#     @classmethod
#     def extract_from_html(cls, html):
#         return [data for data in set(re.findall(cls.VALID_URL_RE, html))]
#
#
# class BunkrVideoExtractor(ExtractorBase):
#     VALID_URL_RE = re.compile(PATTERN_BUNKR_VIDEO)
#     PROTOCOL = "https"
#     DOMAIN = "stream.bunkr.is"
#     DESC = "Bunkr.is Video Page"
#     CONTENT_TYPE = "ITEM"
#
#     def _extract_data(self, url: str):
#         self.url = url
#         if "stream.bunkr" in self.url:
#             response = self.request(self.url)
#             html = response.text
#             if "<title>404: This page could not be found</title>" in html:
#                 return
#             source = self._extract_direct_link(html)
#
#             filename, extension = split_filename_ext(source.split("/")[-1])
#             content_type = determine_content_type(extension)
#
#         else:
#             server_num = extract_server_number(self.url)
#
#             file_w_extension = self.url.split("/")[-1]
#             filename, extension = split_filename_ext(file_w_extension)
#
#             content_type = determine_content_type(extension)
#
#             source = f"{STREAM_URL.format(server_num=server_num)}/{file_w_extension}"
#
#         self.add_item(
#             content_type=content_type,
#             filename=filename,
#             extension=extension,
#             source=source,
#         )
#
#     def _extract_direct_link(self, html) -> Union[str, None]:
#         # Extract the script that fetches album data in json format
#         pattern = re.compile(PATTERN_BUNKR_ALBUM_DATA_SCRIPT)
#         data_tag = re.search(pattern, html)
#
#         if not data_tag:
#             logging.debug(
#                 f"Failed to extract data.\n"
#                 f"Didn't find html script tag containing data."
#             )
#             return None
#
#         # Load into json
#         json_ = json.loads(data_tag.group(1))
#         is_fallback = json_["isFallback"]
#         page_props = json_["props"]["pageProps"]
#
#         if json_ and is_fallback:
#             page_props = self._fallback_method(json_['buildId'])
#
#         try:
#             item_info = page_props["file"]
#             filename = item_info["name"]
#             url_base = item_info["mediafiles"]
#         except KeyError:
#             raise ExtractionError(f"Failed to extract info: {page_props}")
#         return f"{url_base}/{filename}"
#
#     def _fallback_method(self, build_id: str) -> dict:
#         url = yarl.URL(self.url)
#         pageprops_url = fallback_pageprops(domain=url.host, build_id=build_id, album_path=url.path)
#         return parse_fallback_response(self.request(pageprops_url))
#
#     @classmethod
#     def extract_from_html(cls, html):
#         data = [data[0] for data in set(re.findall(cls.VALID_URL_RE, html))]
#         return data
#
#
# class BunkrImageExtractor(ExtractorBase):
#     VALID_URL_RE = re.compile(PATTERN_BUNKR_IMAGE)
#     PROTOCOL = "https"
#     DOMAIN = "bunkr.is"
#     DESC = "Bunkr.is Image Direct URL"
#     CONTENT_TYPE = "ITEM"
#
#     def _extract_data(self, url):
#         file_w_extension = url.split("/")[-1]
#         filename, extension = split_filename_ext(file_w_extension)
#         content_type = determine_content_type(extension)
#
#         self.add_item(
#             content_type=content_type,
#             filename=filename,
#             extension=extension,
#             source=url,
#         )
#
#     @classmethod
#     def extract_from_html(cls, html):
#         return [data for data in set(re.findall(cls.VALID_URL_RE, html))]
#
#
# class BunkrArchiveExtractor(ExtractorBase):
#     VALID_URL_RE = re.compile(PATTERN_BUNKR_IMAGE)
#     PROTOCOL = "https"
#     DOMAIN = "bunkr.is"
#     DESC = "Bunkr.is Archive direct link"
#     CONTENT_TYPE = "ITEM"
#     SAMPLE_URLS = [
#         "https://cdn.bunkr.is/in-paris-NFp4EcUK.zip"
#     ]
#
#     def _extract_data(self, url):
#         file_w_extension = url.split("/")[-1]
#         filename, extension = split_filename_ext(file_w_extension)
#         content_type = determine_content_type(extension)
#
#         self.add_item(
#             content_type=content_type,
#             filename=filename,
#             extension=extension,
#             source=url,
#         )