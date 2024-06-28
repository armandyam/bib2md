import os
import argparse
import logging

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

def main() -> None:
    """
    Main function to parse command-line arguments and concatenate .bib files.
    """
    parser = argparse.ArgumentParser(description='Concatenate .bib files into a single .bib file.')
    parser.add_argument('bibpath', type=str, help='Path to a directory containing .bib files')
    parser.add_argument('--output', type=str, required=True, help='Path to the output file')
    args = parser.parse_args()

    # Concatenate .bib files
    concatenate_bib_files(args.bibpath, args.output)

if __name__ == '__main__':
    main()
