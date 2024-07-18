import unittest
from unittest.mock import patch, ANY

from scripts.download import mkdir_if_not_exists


class TestMkdirIfNotExists(unittest.TestCase):

    def setUp(self):
        self.filename = 'test_filename.mp4'

    @patch(target=r'scripts.download.os.path.exists')
    @patch(target=r'scripts.download.os.mkdir')
    def test_directory_must_be_created(self, os_mkdir_mock, os_path_exists_mock):
        os_path_exists_mock.return_value = False

        mkdir_if_not_exists(filename=self.filename)

        os_mkdir_mock.assert_called_once_with(path=ANY)

    @patch(target=r'scripts.download.os.path.exists')
    @patch(target=r'scripts.download.os.mkdir')
    def test_directory_must_not_be_created(self, os_mkdir_mock, os_path_exists_mock):
        os_path_exists_mock.return_value = True

        mkdir_if_not_exists(filename=self.filename)

        os_mkdir_mock.assert_not_called()


if __name__ == '__main__':
    unittest.main()
