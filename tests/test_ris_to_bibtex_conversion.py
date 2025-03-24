import unittest
import os
import shutil
import tempfile
from unittest.mock import patch, mock_open, MagicMock
from bib2md.rispy_handler import convert_ris_to_bibtex, convert_ris_folder_to_bibtex
from bib2md.concatenate_bib import concatenate_all_to_bib
from pybtex.database import BibliographyData, Entry

class TestRisToBibtexConversion(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Sample RIS content
        self.sample_ris_content = """TY  - JOUR
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
        # Create a test RIS file
        self.ris_file_path = os.path.join(self.test_dir, 'example.ris')
        with open(self.ris_file_path, 'w') as f:
            f.write(self.sample_ris_content)
        
        # Sample BibTeX content
        self.sample_bib_content = """@article{smith2023example,
  title = {A BibTeX Example Paper},
  author = {Smith, John and Johnson, Robert},
  journal = {Journal of BibTeX Examples},
  year = {2023},
  volume = {10},
  number = {3},
  pages = {45--67},
  doi = {10.5678/bibtex.2023}
}
"""
        # Create a test BibTeX file
        self.bib_file_path = os.path.join(self.test_dir, 'example.bib')
        with open(self.bib_file_path, 'w') as f:
            f.write(self.sample_bib_content)
    
    def tearDown(self):
        # Remove the temporary directory
        shutil.rmtree(self.test_dir)

    @patch('rispy.load')
    def test_convert_ris_to_bibtex(self, mock_rispy_load):
        # Mock the rispy.load function to return a sample RIS entry
        mock_rispy_load.return_value = [{
            'type_of_reference': 'JOUR',
            'authors': ['Smith, John', 'Doe, Jane'],
            'primary_title': 'An Example RIS Paper Title',
            'secondary_title': 'Journal of Examples',
            'year': '2023',
            'volume': '5',
            'number': '2',
            'start_page': '123',
            'end_page': '145',
            'abstract': 'This is an example abstract for a RIS format paper.',
            'doi': '10.1234/example.2023',
            'url': 'https://example.com/paper'
        }]

        # Test convert_ris_to_bibtex function
        bib_data = convert_ris_to_bibtex(self.ris_file_path)
        
        # Check that the function was called with the correct path
        mock_rispy_load.assert_called_once()
        
        # Check that a BibliographyData object is returned
        self.assertIsInstance(bib_data, BibliographyData)
        
        # Check that there is one entry in the bibliography
        self.assertEqual(len(bib_data.entries), 1)
        
        # Get the first entry key
        entry_key = next(iter(bib_data.entries))
        entry = bib_data.entries[entry_key]
        
        # Check that the entry is of type 'article'
        self.assertEqual(entry.type, 'article')
        
        # Check the entry fields
        self.assertEqual(entry.fields['title'], 'An Example RIS Paper Title')
        self.assertEqual(entry.fields['journal'], 'Journal of Examples')
        self.assertEqual(entry.fields['year'], '2023')
        self.assertEqual(entry.fields['volume'], '5')
        self.assertEqual(entry.fields['number'], '2')
        self.assertEqual(entry.fields['pages'], '123--145')
        self.assertEqual(entry.fields['doi'], '10.1234/example.2023')
        self.assertEqual(entry.fields['url'], 'https://example.com/paper')
        self.assertEqual(entry.fields['abstract'], 'This is an example abstract for a RIS format paper.')
        self.assertEqual(entry.fields['author'], 'Smith, John and Doe, Jane')

    @patch('bib2md.rispy_handler.convert_ris_to_bibtex')
    @patch('os.listdir')
    def test_convert_ris_folder_to_bibtex(self, mock_listdir, mock_convert_ris):
        # Setup mocks
        mock_listdir.return_value = ['file1.ris', 'file2.ris', 'not_a_ris.txt']
        
        # Create mock BibliographyData objects
        mock_bib_data1 = BibliographyData()
        entry1 = Entry('article')
        entry1.fields['title'] = 'Paper 1'
        entry1.fields['author'] = 'Author 1'
        mock_bib_data1.entries['paper1'] = entry1
        
        mock_bib_data2 = BibliographyData()
        entry2 = Entry('article')
        entry2.fields['title'] = 'Paper 2'
        entry2.fields['author'] = 'Author 2'
        mock_bib_data2.entries['paper2'] = entry2
        
        mock_convert_ris.side_effect = [mock_bib_data1, mock_bib_data2]
        
        # Test convert_ris_folder_to_bibtex function
        output_file = os.path.join(self.test_dir, 'combined.bib')
        convert_ris_folder_to_bibtex(self.test_dir, output_file)
        
        # Check that convert_ris_to_bibtex was called for each RIS file
        self.assertEqual(mock_convert_ris.call_count, 2)
        
        # Check that the output file exists
        self.assertTrue(os.path.exists(output_file))

    def test_concatenate_all_to_bib(self):
        # Create output file path
        output_file = os.path.join(self.test_dir, 'all_combined.bib')
        
        # Test concatenate_all_to_bib function
        concatenate_all_to_bib(self.test_dir, output_file)
        
        # Check that the output file exists
        self.assertTrue(os.path.exists(output_file))
        
        # Read the output file and check its content
        with open(output_file, 'r') as f:
            content = f.read()
            
        # Check that the BibTeX content is present
        self.assertIn('A BibTeX Example Paper', content)
        self.assertIn('Smith, John and Johnson, Robert', content)
        
        # Check that the RIS content has been converted to BibTeX and is present
        self.assertIn('An Example RIS Paper Title', content)
        # Note: The exact format might vary, so we're just checking for key parts

if __name__ == '__main__':
    unittest.main() 