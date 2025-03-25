import collections
import logging
import os
import rispy
from pathlib import Path
from pybtex.database import BibliographyData, Entry

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_ris_file(ris_file_path: str) -> collections.defaultdict:
    """
    Parse the .ris file and structure the data.

    Args:
        ris_file_path (str): The path to the .ris file.

    Returns:
        defaultdict: A nested defaultdict containing parsed bibliographic data.
    """
    logging.info(f"Parsing .ris file: {ris_file_path}")
    ris_data_parsed = collections.defaultdict(lambda: collections.defaultdict(dict))
    
    # Use rispy to parse the RIS file
    entries = rispy.load(Path(ris_file_path), encoding='utf-8')
    
    for entry in entries:
        # Generate a unique entry ID based on title or ID if available
        entry_id = entry.get('id', '').strip()
        if not entry_id:
            # Create a simple ID from title or use a counter if no title
            entry_id = entry.get('primary_title', f"ris_entry_{len(ris_data_parsed)}")
            entry_id = entry_id.lower().replace(' ', '_')[:50]
        
        # Map RIS fields to our internal representation
        # Basic fields - try different possible title fields
        ris_data_parsed[entry_id]['title'] = entry.get('primary_title', '')
        if not ris_data_parsed[entry_id]['title'] and 'title' in entry:
            ris_data_parsed[entry_id]['title'] = entry['title']
        if not ris_data_parsed[entry_id]['title'] and 'TI' in entry:
            ris_data_parsed[entry_id]['title'] = entry['TI']
            
        if not ris_data_parsed[entry_id]['title']:
            logging.warning(f"No title found for RIS entry with ID: {entry_id}")
        
        # Store the type of reference
        ris_type = entry.get('type_of_reference', '').upper()
        ris_data_parsed[entry_id]['type_of_reference'] = ris_type
        
        # Publication info
        # Journal can be in 'secondary_title', 'JO', 'journal', 'journal_name', or 'J1'/'JF'
        journal = entry.get('secondary_title', '')
        if not journal and 'journal_name' in entry:
            journal = entry['journal_name']
        if not journal and 'journal' in entry:
            journal = entry['journal']
        if not journal and 'JO' in entry:
            journal = entry['JO']
        if not journal and 'JF' in entry:
            journal = entry['JF']
        if not journal and 'J1' in entry:
            journal = entry['J1']
            
        ris_data_parsed[entry_id]['journal'] = journal
        ris_data_parsed[entry_id]['secondary_title'] = entry.get('secondary_title', '')
        ris_data_parsed[entry_id]['booktitle'] = entry.get('secondary_title', '')
        ris_data_parsed[entry_id]['year'] = entry.get('year', '')
        ris_data_parsed[entry_id]['month'] = str(entry.get('month', '01')).zfill(2)
        ris_data_parsed[entry_id]['volume'] = entry.get('volume', '')
        ris_data_parsed[entry_id]['number'] = entry.get('number', '') or entry.get('issue', '')
        ris_data_parsed[entry_id]['pages'] = entry.get('pages', '') or entry.get('start_page', '')
        
        # Thesis specific fields
        if ris_type == 'THES':
            ris_data_parsed[entry_id]['school'] = entry.get('publisher', '')
            ris_data_parsed[entry_id]['address'] = entry.get('place_published', '')
            
            # Determine if PhD or Masters thesis
            thesis_type = entry.get('thesis_type', '').lower()
            if 'phd' in thesis_type or 'doct' in thesis_type or 'dissertation' in thesis_type:
                ris_data_parsed[entry_id]['type'] = 'phdthesis'
            else:
                ris_data_parsed[entry_id]['type'] = 'mastersthesis'
        
        # URLs and DOIs
        ris_data_parsed[entry_id]['url'] = entry.get('url', '')
        ris_data_parsed[entry_id]['doi'] = entry.get('doi', '')
        
        # Create DOI URL if DOI exists but URL doesn't
        if not ris_data_parsed[entry_id]['url'] and ris_data_parsed[entry_id]['doi']:
            ris_data_parsed[entry_id]['url'] = f"https://doi.org/{ris_data_parsed[entry_id]['doi']}"
        
        # Abstract
        ris_data_parsed[entry_id]['abstract'] = entry.get('abstract', '')
        
        # Authors
        author_list = []
        if 'authors' in entry:
            author_list = entry['authors']
        elif 'first_authors' in entry:
            author_list = entry['first_authors']
            
        # Convert author names to standard format
        converted_authors = []
        for author in author_list:
            if ',' in author:
                # Convert "last name, first name middle" format to "first name middle last name"
                parts = [part.strip() for part in author.split(',', 1)]
                last_name = parts[0]
                first_and_middle = parts[1]
                converted_authors.append(f"{first_and_middle} {last_name}")
            else:
                converted_authors.append(author.strip())
                
        ris_data_parsed[entry_id]['authors_list'] = ', '.join(converted_authors)
        
        # Create permalink and paper filename
        title = ris_data_parsed[entry_id]['title'] or 'Untitled'
        ris_data_parsed[entry_id]['paper_file_name'] = f"{ris_data_parsed[entry_id]['year']}-{title.replace(' ', '-')}.md"
        
        # Ensure date is set
        year = ris_data_parsed[entry_id].get('year', '2022')
        month = ris_data_parsed[entry_id].get('month', '01')
        ris_data_parsed[entry_id]['date'] = f"{year}-{month}-01"
    
    return ris_data_parsed


def convert_ris_to_bibtex(ris_data: dict) -> str:
    """
    Convert parsed RIS data to BibTeX format.

    Args:
        ris_data (dict): Parsed RIS data.

    Returns:
        str: BibTeX formatted string.
    """
    logging.info("Converting RIS data to BibTeX...")
    bibtex_entries = []
    
    for entry_id, entry_data in ris_data.items():
        # Determine entry type based on RIS type
        ref_type = entry_data.get('type_of_reference', '').upper()
        
        if ref_type == 'JOUR':
            bib_type = 'article'
        elif ref_type == 'BOOK':
            bib_type = 'book'
        elif ref_type == 'CHAP':
            bib_type = 'inbook'
        elif ref_type == 'CONF':
            bib_type = 'inproceedings'
        elif ref_type == 'THES':
            # Use the specific thesis type if available, otherwise default to phdthesis
            bib_type = entry_data.get('type', 'phdthesis')
        elif ref_type == 'RPRT':
            bib_type = 'techreport'
        else:
            bib_type = 'misc'
        
        # Start building BibTeX entry
        bibtex_entry = [f"@{bib_type}{{{entry_id},"]
        
        # Add title (preserve LaTeX formatting by not escaping)
        title = entry_data.get('title', '')
        if title:
            bibtex_entry.append(f'  title = {{{title}}},')
        
        # Add authors
        authors = entry_data.get('authors_list', '')
        if authors:
            bibtex_entry.append(f'  author = {{{authors}}},')
        
        # Add journal if applicable
        journal = entry_data.get('journal', '')
        if journal and bib_type == 'article':
            bibtex_entry.append(f'  journal = {{{journal}}},')
        
        # Add book title if it's a chapter or proceedings
        booktitle = entry_data.get('booktitle', '')
        if booktitle and bib_type in ['inbook', 'inproceedings']:
            bibtex_entry.append(f'  booktitle = {{{booktitle}}},')
        
        # Add year
        year = entry_data.get('year', '')
        if year:
            bibtex_entry.append(f'  year = {{{year}}},')
        
        # Add volume
        volume = entry_data.get('volume', '')
        if volume:
            bibtex_entry.append(f'  volume = {{{volume}}},')
        
        # Add number/issue
        number = entry_data.get('number', '')
        if number:
            bibtex_entry.append(f'  number = {{{number}}},')
        
        # Add pages
        pages = entry_data.get('pages', '')
        if pages:
            bibtex_entry.append(f'  pages = {{{pages}}},')
        
        # Add URL
        url = entry_data.get('url', '')
        if url:
            bibtex_entry.append(f'  url = {{{url}}},')
        
        # Add DOI
        doi = entry_data.get('doi', '')
        if doi:
            bibtex_entry.append(f'  doi = {{{doi}}},')
        
        # Add abstract
        abstract = entry_data.get('abstract', '')
        if abstract:
            bibtex_entry.append(f'  abstract = {{{abstract}}},')
        
        # Add thesis specific fields
        if bib_type in ['phdthesis', 'mastersthesis']:
            school = entry_data.get('school', '')
            if school:
                bibtex_entry.append(f'  school = {{{school}}},')
            
            address = entry_data.get('address', '')
            if address:
                bibtex_entry.append(f'  address = {{{address}}},')
            
            # For thesis, add type field to specify PhD or Masters
            if bib_type == 'phdthesis':
                bibtex_entry.append('  type = {{PhD Thesis}},')
            elif bib_type == 'mastersthesis':
                bibtex_entry.append('  type = {{Master\\\'s Thesis}},')
        
        # Close the entry
        bibtex_entry.append('}')
        
        # Add the complete entry to the list
        bibtex_entries.append('\n'.join(bibtex_entry))
    
    # Join all entries with a newline and return
    return '\n\n'.join(bibtex_entries)


def convert_ris_file_to_bibtex(ris_file_path: str) -> str:
    """
    Convert RIS file to BibTeX format.

    Args:
        ris_file_path (str): Path to the RIS file.

    Returns:
        str: BibTeX formatted string.
    """
    try:
        ris_data = parse_ris_file(ris_file_path)
        return convert_ris_to_bibtex(ris_data)
    except Exception as e:
        logging.error(f"Error converting RIS file {ris_file_path}: {str(e)}")
        return ""


def convert_ris_folder_to_bibtex(folder_path: str, output_file: str) -> None:
    """
    Convert all RIS files in a folder to a single BibTeX file.

    Args:
        folder_path (str): Path to the folder containing RIS files.
        output_file (str): Path to the output BibTeX file.
    """
    logging.info(f"Converting all RIS files in {folder_path} to BibTeX")
    
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir) and output_dir:
        os.makedirs(output_dir)
        logging.info(f"Created output directory {output_dir}")
    
    # Find all RIS files in the folder
    ris_files = [f for f in os.listdir(folder_path) if f.endswith('.ris')]
    
    if not ris_files:
        logging.info(f"No RIS files found in {folder_path}")
        # Create an empty BibTeX file if no RIS files found
        with open(output_file, 'w') as f:
            pass
        return
    
    # Combined BibTeX content
    combined_bibtex = ""
    
    # Process each RIS file
    for ris_file in ris_files:
        file_path = os.path.join(folder_path, ris_file)
        try:
            # Convert RIS to BibTeX
            bibtex_content = convert_ris_file_to_bibtex(file_path)
            if bibtex_content:
                combined_bibtex += bibtex_content + "\n\n"
        except Exception as e:
            logging.error(f"Error converting {file_path}: {str(e)}")
    
    # Write combined BibTeX content to output file
    with open(output_file, 'w') as f:
        f.write(combined_bibtex)
    logging.info(f"Converted RIS files to BibTeX and saved to {output_file}")


def concatenate_ris_files(folder_path: str, output_file: str) -> None:
    """
    Concatenate all .ris files in the specified folder into a single .ris file.

    Args:
        folder_path (str): Path to the folder containing .ris files.
        output_file (str): Path to the output .ris file.
    """
    # Ensure the output directory exists
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir) and output_dir:
        os.makedirs(output_dir)
        logging.info(f"Created output directory {output_dir}")

    # List all .ris files in the folder
    ris_files = [f for f in os.listdir(folder_path) if f.endswith('.ris')]

    # Open the output file
    with open(output_file, 'w') as outfile:
        # Iterate over each .ris file
        for ris_file in ris_files:
            file_path = os.path.join(folder_path, ris_file)
            with open(file_path, 'r') as infile:
                # Read the content of the current .ris file and write it to the output file
                content = infile.read()
                outfile.write(content)
                if not content.endswith('\n'):
                    outfile.write('\n')
                if not content.strip().endswith('ER  -'):
                    outfile.write('ER  -\n')
                outfile.write('\n')  # Ensure there is a new line between entries

    logging.info(f"All .ris files have been concatenated into {output_file}") 