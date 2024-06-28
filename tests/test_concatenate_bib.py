import os
import unittest
from unittest.mock import patch, mock_open, call
from io import StringIO
from bib2md.concatenate_bib import concatenate_bib_files

class TestConcatenateBibFiles(unittest.TestCase):

    @patch("os.listdir")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_concatenate_multiple_files(self, mock_makedirs, mock_exists, mock_open_func, mock_listdir):
        # Setup mocks
        mock_listdir.return_value = ['file1.bib', 'file2.bib']
        mock_exists.return_value = True
        mock_open_func.side_effect = [
            mock_open(read_data='@article{sample1, ...}').return_value,
            mock_open(read_data='@article{sample2, ...}').return_value,
            mock_open().return_value
        ]

        # Call the function
        concatenate_bib_files("some/folder", "output/combined.bib")

        # Assertions
        mock_open_func.assert_has_calls([
            call('some/folder/file1.bib', 'r'),
            call('some/folder/file2.bib', 'r'),
            call('output/combined.bib', 'w')
        ], any_order=True)



    @patch("os.listdir")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_empty_directory(self, mock_makedirs, mock_exists, mock_open_func, mock_listdir):
        # Setup mocks
        mock_listdir.return_value = []
        mock_exists.return_value = True

        # Call the function
        concatenate_bib_files("some/empty_folder", "output/combined.bib")

        # Assertions
        mock_open_func.assert_called_once_with('output/combined.bib', 'w')
        mock_open_func().write.assert_not_called()

    @patch("os.listdir")
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists")
    @patch("os.makedirs")
    def test_create_output_directory(self, mock_makedirs, mock_exists, mock_open_func, mock_listdir):
        # Setup mocks
        mock_listdir.return_value = ['file1.bib']
        mock_exists.side_effect = [True, False]  # Folder exists check, output directory check
        mock_open_func.side_effect = [
            mock_open(read_data='@article{sample1, ...}').return_value,
            mock_open().return_value
        ]

        # Call the function
        concatenate_bib_files("some/folder", "output/newdir/combined.bib")

        # Assertions
        mock_open_func.assert_has_calls([
            call('some/folder/file1.bib', 'r'),
            call('output/newdir/combined.bib', 'w')
        ], any_order=True)



if __name__ == '__main__':
    unittest.main()
