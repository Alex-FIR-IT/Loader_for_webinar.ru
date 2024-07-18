import unittest
from unittest.mock import patch

from scripts.files_merging import get_webinar_filename_from_user


class TestGetWebinarFilenameFromUser(unittest.TestCase):

    def setUp(self):
        self.filename_without_ext = "filename_video"

    @patch('scripts.files_merging.input')
    def test_append_mp4_to_file(self, input_mock):
        filename_with_ext = f"{self.filename_without_ext}.mp4"
        input_mock.return_value = filename_with_ext

        result_filename = get_webinar_filename_from_user()

        self.assertEqual(result_filename, filename_with_ext)

    @patch('scripts.files_merging.input')
    def test_does_not_append_mp4_to_file(self, input_mock):
        filename_with_ext = f"{self.filename_without_ext}.mp4"
        input_mock.return_value = self.filename_without_ext

        result_filename = get_webinar_filename_from_user()

        self.assertEqual(result_filename, filename_with_ext)

    @patch('scripts.files_merging.input')
    def test_append_mp4_to_file_with_mp3_ext(self, input_mock):
        filename_with_ext = f"{self.filename_without_ext}.mp3"
        input_mock.return_value = filename_with_ext

        result_filename = get_webinar_filename_from_user()

        self.assertEqual(result_filename, f"{filename_with_ext}.mp4")


if __name__ == '__main__':
    unittest.main()
