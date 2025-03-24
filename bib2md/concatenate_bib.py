import os
import argparse
import logging
from pybtex.database import parse_file, BibliographyData

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def concatenate_bib_files(folder_path: str, output_file: str) -> None:
    """
    Concatenate all .bib files in the specified folder into a single .bib file.

    Args:
        folder_path (str): Path to the folder containing .bib files.
        output_file (str): Path to the output .bib file.
    """
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir) and output_dir:
        os.makedirs(output_dir)
        logging.info(f"Created output directory {output_dir}")

    # List all .bib files in the folder
    bib_files = [f for f in os.listdir(folder_path) if f.endswith('.bib')]

    # Open the output file
    with open(output_file, 'w') as outfile:
        # Iterate over each .bib file
        for bib_file in bib_files:
            file_path = os.path.join(folder_path, bib_file)
            with open(file_path, 'r') as infile:
                # Read the content of the current .bib file and write it to the output file
                content = infile.read()
                outfile.write(content)
                outfile.write('\n\n')  # Ensure there is a new line between entries

    logging.info(f"All .bib files have been concatenated into {output_file}")

def concatenate_all_to_bib(folder_path: str, output_file: str) -> None:
    """
    Convert RIS files to BibTeX format and concatenate with all .bib files 
    in the specified folder into a single .bib file.

    Args:
        folder_path (str): Path to the folder containing .bib and .ris files.
        output_file (str): Path to the output .bib file.
    """
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir) and output_dir:
        os.makedirs(output_dir)
        logging.info(f"Created output directory {output_dir}")

    # List all .bib and .ris files in the folder
    bib_files = [f for f in os.listdir(folder_path) if f.endswith('.bib')]
    ris_files = [f for f in os.listdir(folder_path) if f.endswith('.ris')]

    # Combined BibTeX content
    combined_bibtex = ""

    # Process BibTeX files
    for bib_file in bib_files:
        file_path = os.path.join(folder_path, bib_file)
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                combined_bibtex += content + "\n\n"
        except Exception as e:
            logging.error(f"Error processing BibTeX file {file_path}: {str(e)}")

    # Process RIS files
    if ris_files:
        try:
            from .rispy_handler import convert_ris_file_to_bibtex
        except ImportError:
            # Fall back to direct import when running as script
            from bib2md.rispy_handler import convert_ris_file_to_bibtex
            
        for ris_file in ris_files:
            file_path = os.path.join(folder_path, ris_file)
            try:
                # Convert RIS to BibTeX
                bibtex_content = convert_ris_file_to_bibtex(file_path)
                if bibtex_content:
                    combined_bibtex += bibtex_content + "\n\n"
            except Exception as e:
                logging.error(f"Error converting RIS file {file_path}: {str(e)}")

    # Write the combined content to the output file
    with open(output_file, 'w') as f:
        f.write(combined_bibtex)
    logging.info(f"All reference files have been combined into {output_file}")

def concatenate_reference_files(folder_path: str, output_bib: str = None, output_ris: str = None, all_to_bib: str = None) -> None:
    """
    Concatenate all reference files in the specified folder into output files.

    Args:
        folder_path (str): Path to the folder containing reference files.
        output_bib (str, optional): Path to the output .bib file for BIB only concatenation.
        output_ris (str, optional): Path to the output .ris file for RIS only concatenation.
        all_to_bib (str, optional): Path to the combined output BIB file with both BIB and RIS files.
    """
    if output_bib:
        concatenate_bib_files(folder_path, output_bib)
    
    if output_ris:
        from .rispy_handler import concatenate_ris_files
        concatenate_ris_files(folder_path, output_ris)
        
    if all_to_bib:
        concatenate_all_to_bib(folder_path, all_to_bib)

def main() -> None:
    """
    Main function to parse command-line arguments and concatenate reference files.
    """
    parser = argparse.ArgumentParser(description='Concatenate reference files into output files.')
    parser.add_argument('refpath', type=str, help='Path to a directory containing reference files')
    parser.add_argument('--output_bib', type=str, help='Path to the output .bib file (BIB only)')
    parser.add_argument('--output_ris', type=str, help='Path to the output .ris file (RIS only)')
    parser.add_argument('--all_to_bib', type=str, help='Path to the output .bib file (both BIB and RIS files)')
    parser.add_argument('--output', type=str, help='Path to the output file (for backward compatibility, .bib format)')
    args = parser.parse_args()

    # Set output_bib to args.output for backward compatibility
    output_bib = args.output_bib or args.output
    output_ris = args.output_ris
    all_to_bib = args.all_to_bib
    
    # Ensure at least one output is specified
    if not output_bib and not output_ris and not all_to_bib:
        if args.output:
            output_bib = args.output
        else:
            output_bib = os.path.join(args.refpath, 'combined.bib')
            logging.warning(f"No output file specified, defaulting to {output_bib}")
    
    # Concatenate reference files
    concatenate_reference_files(args.refpath, output_bib, output_ris, all_to_bib)

if __name__ == '__main__':
    main()
