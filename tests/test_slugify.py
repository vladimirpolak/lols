from lols.utils import slugify
import unittest


class SlugifyTest(unittest.TestCase):
    def test_slugify(self):
        input_string = "AOTM+-+Break+My+Heart+Myself%27+covered+by+ITZY+YEJI+%26+RYUJIN"
