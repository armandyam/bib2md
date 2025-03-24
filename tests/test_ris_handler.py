import unittest
import os
import shutil
import collections
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from bib2md.rispy_handler import parse_ris_file, concatenate_ris_files

class TestRisHandler(unittest.TestCase):

    def setUp(self):
        os.makedirs('output', exist_ok=True)
        # Create a sample RIS content
        self.sample_ris_content = """
TY  - JOUR
AU  - Smith, John
AU  - Doe, Jane
TI  - An Example RIS Paper Title
JO  - Journal of Examples
PY  - 2023
VL  - 5
IS  - 2
SP  - 123
EP  - 145
AB  - This is an example abstract for a RIS format paper.
DO  - 10.1234/example.2023
UR  - https://example.com/paper
ER  - 
"""
        
    def tearDown(self):
        shutil.rmtree('output', ignore_errors=True)

    @patch('rispy.load')
    def test_parse_ris_file(self, mock_rispy_load):
        # Mock the rispy.load function to return a sample RIS entry
        mock_rispy_load.return_value = [{
            'type_of_reference': 'JOUR',
            'authors': ['Smith, John', 'Doe, Jane'],
            'primary_title': 'An Example RIS Paper Title',
            'secondary_title': 'Journal of Examples',
            'year': '2023',
            'volume': '5',
            'number': '2',
            'abstract': 'This is an example abstract for a RIS format paper.',
            'doi': '10.1234/example.2023',
            'url': 'https://example.com/paper'
        }]

        # Test parse_ris_file function
        ris_data = parse_ris_file('data/example.ris')
        
        # Check that the function was called with the correct path
        mock_rispy_load.assert_called_once()
        
        # Check the parsed data
        self.assertIsInstance(ris_data, collections.defaultdict)
        
        # Get the first entry (using the generated ID)
        entry_id = next(iter(ris_data))
        self.assertEqual(ris_data[entry_id]['title'], 'An Example RIS Paper Title')
        self.assertEqual(ris_data[entry_id]['journal'], 'Journal of Examples')
        self.assertEqual(ris_data[entry_id]['year'], '2023')
        self.assertEqual(ris_data[entry_id]['authors_list'], 'Smith, John, Doe, Jane')
        self.assertEqual(ris_data[entry_id]['paper_file_name'], '2023-An-Example-RIS-Paper-Title.md')

    @patch('os.path.exists')
    @patch('os.makedirs')
    @patch('os.listdir')
    @patch('builtins.open', new_callable=mock_open)
    def test_concatenate_ris_files(self, mock_open_func, mock_listdir, mock_makedirs, mock_exists):
        # Setup mocks
        mock_listdir.return_value = ['file1.ris', 'file2.ris', 'not_a_ris.txt']
        mock_exists.return_value = True
        
        # Setup mock open to handle multiple files
        handle1 = mock_open(read_data='TY  - JOUR\nER  - ').return_value
        handle2 = mock_open(read_data='TY  - BOOK\nER  - ').return_value
        handle3 = mock_open().return_value
        
        mock_open_func.side_effect = lambda f, m: {
            'some/folder/file1.ris': handle1,
            'some/folder/file2.ris': handle2,
            'output/combined.ris': handle3
        }.get(f, mock_open().return_value)
        
        # Call the function
        concatenate_ris_files('some/folder', 'output/combined.ris')
        
        # Assertions
        self.assertEqual(mock_open_func.call_count, 3)  # 2 input files + 1 output file
        # Check that the output file was opened for writing
        mock_open_func.assert_any_call('output/combined.ris', 'w')
        
        # Check that content from each file was written to the output
        calls = handle3.write.call_args_list
        self.assertEqual(len(calls), 6)  # 3 writes per file (content, newline check, newline between entries)

if __name__ == '__main__':
    unittest.main() 