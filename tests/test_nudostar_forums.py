import unittest
from lols.scrapers.forum_nudostar import ForumNudostarContentExtractor


class NudostarNameProcessingTest(unittest.TestCase):
    def test_process_nudostar_filename_image1(self):
        url = "https://nudostar.com/forum/attachments/rn1yfyd2og471-jpg.895744"
        filename_extension = ForumNudostarContentExtractor._nudostar_process_filename(url)
        self.assertEqual(filename_extension, ("rn1yfyd2og471", ".jpg"))

    def test_process_nudostar_filename_image2(self):
        url = "https://nudostar.com/forum/attachments/f6b2f53d-93ce-46e0-a4af-051f52552b92-jpeg.895754/"
        filename_extension = ForumNudostarContentExtractor._nudostar_process_filename(url)
        self.assertEqual(filename_extension, ("f6b2f53d-93ce-46e0-a4af-051f52552b92", ".jpeg"))

    def test_process_nudostar_filename_video(self):
        url = "https://nudostar.com/forum/attachments/2021-02-12_0gnkzibiiotprbhyr5e54_source-m4v.3284635/"
        filename_extension = ForumNudostarContentExtractor._nudostar_process_filename(url)
        self.assertEqual(filename_extension, ("2021-02-12_0gnkzibiiotprbhyr5e54_source", ".m4v"))
