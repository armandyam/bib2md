import unittest
from unittest.mock import patch, MagicMock
from bib2md.concatenate_bib import concatenate_reference_files

class TestConcatenateRefFiles(unittest.TestCase):

    @patch('bib2md.concatenate_bib.concatenate_bib_files')
    @patch('bib2md.rispy_handler.concatenate_ris_files')
    def test_concatenate_reference_files_both(self, mock_concatenate_ris, mock_concatenate_bib):
        # Call the function with both output files specified
        concatenate_reference_files(
            'data',
            output_bib='output/combined.bib',
            output_ris='output/combined.ris'
        )
        
        # Check that both concatenate functions were called with the correct arguments
        mock_concatenate_bib.assert_called_once_with('data', 'output/combined.bib')
        mock_concatenate_ris.assert_called_once_with('data', 'output/combined.ris')
    
    @patch('bib2md.concatenate_bib.concatenate_bib_files')
    @patch('bib2md.rispy_handler.concatenate_ris_files')
    def test_concatenate_reference_files_bib_only(self, mock_concatenate_ris, mock_concatenate_bib):
        # Call the function with only bib output specified
        concatenate_reference_files(
            'data',
            output_bib='output/combined.bib',
            output_ris=None
        )
        
        # Check that only the bib concatenate function was called
        mock_concatenate_bib.assert_called_once_with('data', 'output/combined.bib')
        mock_concatenate_ris.assert_not_called()
    
    @patch('bib2md.concatenate_bib.concatenate_bib_files')
    @patch('bib2md.rispy_handler.concatenate_ris_files')
    def test_concatenate_reference_files_ris_only(self, mock_concatenate_ris, mock_concatenate_bib):
        # Call the function with only ris output specified
        concatenate_reference_files(
            'data',
            output_bib=None,
            output_ris='output/combined.ris'
        )
        
        # Check that only the ris concatenate function was called
        mock_concatenate_bib.assert_not_called()
        mock_concatenate_ris.assert_called_once_with('data', 'output/combined.ris')
    
    @patch('bib2md.concatenate_bib.concatenate_bib_files')
    @patch('bib2md.concatenate_bib.logging.warning')
    def test_main_function_default_output(self, mock_logging, mock_concatenate_bib):
        # Test the main function with no output specified
        with patch('bib2md.concatenate_bib.argparse.ArgumentParser') as mock_argparse:
            # Setup mock for parsed arguments
            mock_args = MagicMock()
            mock_args.refpath = 'data'
            mock_args.output_bib = None
            mock_args.output_ris = None
            mock_args.output = None
            mock_args.all_to_bib = None
            
            mock_parser = MagicMock()
            mock_parser.parse_args.return_value = mock_args
            mock_argparse.return_value = mock_parser
            
            # Mock the concatenate_reference_files function to avoid actual execution
            with patch('bib2md.concatenate_bib.concatenate_reference_files') as mock_concat_ref:
                # Call the main function
                from bib2md.concatenate_bib import main
                main()
                
                # Check that a warning was logged about the default output
                mock_logging.assert_called()
                
                # Check that concatenate_reference_files was called with the correct arguments
                mock_concat_ref.assert_called_once_with('data', 'data/combined.bib', None, None)

if __name__ == '__main__':
    unittest.main() 