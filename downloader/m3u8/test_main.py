#!/usr/bin/env python
# coding=utf-8

"""Project unit tests.

"""

import os.path
import sys

from m3u8downloader.main import get_suffix_from_url
from m3u8downloader.main import is_higher_resolution
from m3u8downloader.main import get_url_path
from m3u8downloader.main import get_basename
from m3u8downloader.main import get_fullpath
from m3u8downloader.main import get_local_file_for_url
from m3u8downloader.main import rewrite_key_uri
from m3u8downloader.main import safe_file_name


def test_safe_file_name():
    assert safe_file_name('abc/def/ghi') == 'abc_def_ghi'
    if sys.platform == 'win32':
        assert safe_file_name('abc:def:ghi > jk') == 'abc：def：ghi 》 jk'


def test_rewrite_key_uri():
    assert rewrite_key_uri("/tmp/foo", "https://example.com/foobar/foo.m3u8", "#EXT-X-KEY:METHOD=AES-128,URI=\"foo.key\"") == "#EXT-X-KEY:METHOD=AES-128,URI=\"/tmp/foo/foobar/foo.key\""
    assert rewrite_key_uri("/tmp/foo", "https://example.com/foo.m3u8", "#EXT-X-KEY:METHOD=AES-128,URI=\"foo.key\"") == "#EXT-X-KEY:METHOD=AES-128,URI=\"/tmp/foo/foo.key\""
    assert rewrite_key_uri("/tmp/foo", "https://example.com/foobar/foo.m3u8", "#EXT-X-KEY:METHOD=AES-128,URI=\"/abc/foo.key\"") == "#EXT-X-KEY:METHOD=AES-128,URI=\"/tmp/foo/abc/foo.key\""
    assert rewrite_key_uri("/tmp/foo", "https://example.com/foobar/foo.m3u8", "#EXT-X-KEY:METHOD=AES-128,URI=\"https://example.com/abc/foo.key\"") == "#EXT-X-KEY:METHOD=AES-128,URI=\"/tmp/foo/abc/foo.key\""
    assert rewrite_key_uri("C:\\Users\\foo\\temp", "https://example.com/foobar/foo.m3u8", "#EXT-X-KEY:METHOD=AES-128,URI=\"https://example.com/abc/foo.key\"") == "#EXT-X-KEY:METHOD=AES-128,URI=\"C:/Users/foo/temp/abc/foo.key\""


# test for get_local_file_for_url
def test_get_local_file_for_url():
    assert get_local_file_for_url("/tmp/foo", "abc.ts") == "/tmp/foo/abc.ts"
    assert get_local_file_for_url("/tmp/foo", "/abc.ts") == "/tmp/foo/abc.ts"
    assert get_local_file_for_url("/tmp/foo", "abc/def.ts") == "/tmp/foo/abc/def.ts"
    assert get_local_file_for_url("/tmp/foo", "./def.ts") == "/tmp/foo/def.ts"
    assert get_local_file_for_url("/tmp/foo", "http://example.com/abc/def.ts") == "/tmp/foo/abc/def.ts"
    assert get_local_file_for_url("/tmp/foo", "https://example.com/abc/def.ts") == "/tmp/foo/abc/def.ts"
    assert get_local_file_for_url("/tmp/foo", "https://example.com/abc/def.ts", "/tmp/foo/abc/def.ts") == "/tmp/foo/abc/def.ts"


# test for join
def test_join():
    assert os.path.normpath(os.path.join("/foo/bar/baz", "./abc.txt")) == "/foo/bar/baz/abc.txt"
    assert os.path.normpath(os.path.join(".", "./abc.txt")) == "abc.txt"


# test for get_url_path
def test_get_url_path():
    assert get_url_path('http://example.com/250kb/hls/index.m3u8') == '/250kb/hls/index.m3u8'
    assert get_url_path('http://example.com/index.m3u8') == '/index.m3u8'


# test for get_suffix_from_url
def test_get_suffix_from_url():
    assert get_suffix_from_url("250kb/hls/index.m3u8") == ".m3u8"
    assert get_suffix_from_url("qpdL6296102.ts") == ".ts"
    assert get_suffix_from_url("qpdL6296102") == ""


# test for is_higher_resolution
def test_is_higher_resolution():
    assert is_higher_resolution("480x854", None)
    assert not is_higher_resolution("480x854", "720x1280")
    assert is_higher_resolution("720x1280", "480x854")


# test for get_basename
def test_get_basename():
    assert get_basename("foo.mp4") == "foo"
    assert get_basename("~/d/t2/foo.mp4") == "foo"
    assert get_basename("d/t2/foo.mp4") == "foo"
    assert get_basename("./foo.mp4") == "foo"
    assert get_basename("./foo") == "foo"


# test for get_fullpath
def test_get_fullpath():
    assert get_fullpath("foo") == os.path.abspath(os.path.join(os.curdir, "foo"))
    assert get_fullpath("foo/") == os.path.abspath(os.path.join(os.curdir, "foo"))
    assert get_fullpath("foo/bar") == os.path.abspath(os.path.join(os.curdir, "foo", "bar"))
    assert get_fullpath("~/foo/") == os.path.expanduser("~/foo")
    assert get_fullpath("$HOME/foo/") == os.path.expanduser("~/foo")
