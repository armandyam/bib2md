import unittest
import os
import shutil
import collections
from unittest.mock import patch, mock_open, MagicMock
from bib2md.bib2md import generate_html_paper_list, process_reference_files

class TestHtmlGeneration(unittest.TestCase):

    def setUp(self):
        os.makedirs('output', exist_ok=True)
        
    def tearDown(self):
        shutil.rmtree('output', ignore_errors=True)
    
    @patch('bib2md.bib2md.load_jinja_template')
    @patch('os.path.dirname')
    @patch('os.listdir')
    @patch('os.makedirs')
    @patch('builtins.open', new_callable=mock_open)
    def test_generate_html_paper_list(self, mock_open_func, mock_makedirs, mock_listdir, mock_dirname, mock_load_template):
        # Setup mocks
        mock_template = MagicMock()
        mock_template.render.return_value = "<html>Test HTML content</html>"
        mock_load_template.return_value = (mock_template, set())
        mock_dirname.return_value = 'output'
        mock_listdir.return_value = ['paper1.bib', 'paper2.ris']
        
        # Sample reference data
        ref_data = {
            'entry1': {
                'title': 'Paper Title 1',
                'authors_list': 'Author1, Author2',
                'year': '2023',
                'journal': 'Journal Name',
                'volume': '5',
                'number': '2',
                'doi': '10.1234/example',
                'url': 'https://example.com/paper1'
            },
            'entry2': {
                'title': 'Paper Title 2',
                'authors_list': 'Author3, Author4',
                'year': '2022',
                'booktitle': 'Conference Name',
                'doi': '10.1234/example2',
                'url': 'https://example.com/paper2'
            }
        }
        
        # Call the function
        generate_html_paper_list(ref_data, 'templates/html_papers_list.jinja2', 'output/papers.html')
        
        # Check that the template was loaded and rendered
        mock_load_template.assert_called_once_with('templates/html_papers_list.jinja2')
        mock_template.render.assert_called_once()
        
        # Check that the output file was created
        mock_open_func.assert_called_with('output/papers.html', 'w')
        mock_open_func().write.assert_called_once_with("<html>Test HTML content</html>")
        
        # Check that the papers were sorted by year
        render_args = mock_template.render.call_args[1]
        self.assertIn('papers', render_args)
        self.assertEqual(len(render_args['papers']), 2)
        # First paper should be the one with year 2023 (newest first)
        self.assertEqual(render_args['papers'][0]['year'], '2023')
    
    @patch('bib2md.bib2md.parse_bib_file')
    @patch('bib2md.bib2md.parse_ris_file')
    @patch('bib2md.bib2md.convert_bib_to_md')
    @patch('bib2md.bib2md.convert_ris_to_md')
    @patch('bib2md.bib2md.generate_html_paper_list')
    @patch('glob.glob')
    @patch('os.path.isdir')
    def test_process_reference_files_with_html(self, mock_isdir, mock_glob, mock_generate_html, 
                                             mock_convert_ris, mock_convert_bib, 
                                             mock_parse_ris, mock_parse_bib):
        # Setup mocks
        mock_isdir.return_value = True
        mock_glob.side_effect = lambda path: {
            'data/*.bib': ['data/file1.bib', 'data/file2.bib'],
            'data/*.ris': ['data/file1.ris']
        }[path]
        
        mock_parse_bib.return_value = {'entry1': {'title': 'BibTeX Paper'}}
        mock_parse_ris.return_value = {'entry2': {'title': 'RIS Paper'}}
        
        # Expected combined ref data
        expected_combined_data = {'entry1': {'title': 'BibTeX Paper'}, 'entry2': {'title': 'RIS Paper'}}
        
        # Call the function
        process_reference_files(
            'data', 
            'templates/md_template.jinja2', 
            'output',
            include_abstract=True,
            html_template_path='templates/html_papers_list.jinja2',
            html_output='output/papers.html'
        )
        
        # Check that the functions were called with the correct arguments
        mock_convert_bib.assert_called_once_with(
            ['data/file1.bib', 'data/file2.bib'], 
            'templates/md_template.jinja2', 
            'output', 
            True
        )
        
        mock_convert_ris.assert_called_once_with(
            ['data/file1.ris'], 
            'templates/md_template.jinja2', 
            'output', 
            True
        )
        
        # Check that parse functions were called for each file
        self.assertEqual(mock_parse_bib.call_count, 2)
        self.assertEqual(mock_parse_ris.call_count, 1)
        
        # Check that generate_html_paper_list was called with the combined data
        mock_generate_html.assert_called_once()
        # The first argument should be a dictionary containing both entries
        self.assertEqual(len(mock_generate_html.call_args[0][0]), 2)

if __name__ == '__main__':
    unittest.main() 