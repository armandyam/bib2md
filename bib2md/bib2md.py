import collections
import logging
import os
import argparse
from typing import Tuple, List, Set, Union, Dict, Any, Optional
from pybtex.database import parse_file, BibliographyData
import jinja2
from jinja2 import Template, meta
import glob
import re
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_jinja_template(template_path: str) -> Tuple[Template, Set[str]]:
    """
    Load Jinja2 environment and parse the template file to find undeclared variables.

    Args:
        template_path (str): The path to the Jinja2 template file.

    Returns:
        tuple: A tuple containing the Jinja2 template and a set of undeclared variables.
    """
    logging.info(f"Loading Jinja2 template from: {template_path}")

    # Set up Jinja2 environment
    template_dir = os.path.dirname(template_path)
    template_filename = os.path.basename(template_path)
    template_loader = jinja2.FileSystemLoader(searchpath=template_dir)
    template_env = jinja2.Environment(loader=template_loader)
    
    # Add custom filters
    def prepend_filter(value, prefix, default=None):
        """Filter to prepend a prefix to a value if the value exists."""
        if value:
            return f"{prefix}{value}"
        return default
    
    template_env.filters['prepend'] = prepend_filter
    
    template = template_env.get_template(template_filename)

    # Read the template content
    with open(template_path, 'r') as file:
        template_content = file.read()

    # Parse the template to find undeclared variables
    parsed_content = template_env.parse(template_content)
    undeclared_variables = meta.find_undeclared_variables(parsed_content)

    return template, undeclared_variables


def parse_bib_file(bib_file_path: str) -> collections.defaultdict:
    """
    Parse the .bib file and structure the data.

    Args:
        bib_file_path (str): The path to the .bib file.

    Returns:
        defaultdict: A nested defaultdict containing parsed bibliographic data.
    """
    logging.info(f"Parsing .bib file: {bib_file_path}")
    bib_data_parsed = collections.defaultdict(lambda: collections.defaultdict(dict))
    bib_data = parse_file(bib_file_path)
    for entry in bib_data.entries:
        # Copy all fields as is
        for field in bib_data.entries[entry].fields:
            field_key = field.lower().replace('-', '_')
            bib_data_parsed[entry][field_key] = bib_data.entries[entry].fields[field]
        
        # Keep track of the entry type
        bib_data_parsed[entry]['type'] = bib_data.entries[entry].type
        
        # Process authors - only include actual authors, not editors
        if 'author' in bib_data.entries[entry].persons:
            author_list = []
            authors = bib_data.entries[entry].persons['author']
            for author in authors:
                author_first_name = ' '.join(author.first_names)
                author_last_name = ' '.join(author.last_names)
                author_list.append(author_first_name + ' ' + author_last_name)
            bib_data_parsed[entry]['authors_list'] = ', '.join(author_list)
        
        # Special handling for arXiv
        if ('archiveprefix' in bib_data_parsed[entry] and 
            bib_data_parsed[entry]['archiveprefix'].lower() == 'arxiv'):
            bib_data_parsed[entry]['archive_prefix'] = 'arXiv'
            bib_data_parsed[entry]['is_arxiv'] = True
            # If URL is not specified but eprint is, construct the arXiv URL
            if 'url' not in bib_data_parsed[entry] and 'eprint' in bib_data_parsed[entry]:
                bib_data_parsed[entry]['url'] = f"https://arxiv.org/abs/{bib_data_parsed[entry]['eprint']}"
        
        # Create a permalink based on year and title
        bib_data_parsed[entry][
            'paper_file_name'] = f"{bib_data_parsed[entry].get('year', '2022')}-{bib_data_parsed[entry].get('title', '').replace(' ', '-')}.md"
        
        # Ensure date is set
        year = bib_data_parsed[entry].get('year', '2022')
        month = bib_data_parsed[entry].get('month', '01')
        bib_data_parsed[entry]['date'] = f"{year}-{month}-01"
    
    return bib_data_parsed


def generate_markdown_files(bib_data: collections.defaultdict, template: Template, undeclared_variables: Set[str],
                            output_folder: str, include_abstract: bool = False) -> None:
    """
    Generate markdown files using the parsed bibliographic data and Jinja2 template.

    Args:
        bib_data (defaultdict): Parsed bibliographic data.
        template (Template): Jinja2 template object.
        undeclared_variables (set): Set of undeclared variables in the template.
        output_folder (str): Path to the output folder.
        include_abstract (bool): Flag to include abstract and download link in the markdown file.
    """
    logging.info("Generating markdown files from bibliographic data")
    os.makedirs(output_folder, exist_ok=True)  # Create output folder if it doesn't exist
    for entry in bib_data:
        template_data = {}
        temp_undeclared_variables = undeclared_variables.copy()
        for value in undeclared_variables:
            if value in bib_data[entry].keys():
                template_data[value] = bib_data[entry][value]
                temp_undeclared_variables.remove(value)
        if temp_undeclared_variables:
            logging.warning(f"The following variables are not defined in the bib file: {temp_undeclared_variables}")

        template_data['permalink'] = bib_data[entry]['paper_file_name'].replace(".md", '')
        # Handle abstract and download link
        if not include_abstract:
            template_data['paperurl'] = ''
            template_data['excerpt'] = ''
        else:
            template_data['excerpt'] = template_data.get('abstract', '')
            template_data['paperurl'] = template_data.get('url', '')

        output_file = os.path.join(output_folder, bib_data[entry]['paper_file_name'])
        output_text = template.render(template_data)  # this is where to put args to the template renderer
        with open(output_file, "w") as text_file:
            text_file.write(output_text)
            logging.info(f"Markdown file written: {output_file}")


def convert_bib_to_md(bib_files: List[str], template_path: str, output_folder: str,
                      include_abstract: bool = False) -> None:
    """
    Convert .bib files to markdown files using a Jinja2 template.

    Args:
        bib_files (list): List of paths to .bib files.
        template_path (str): The path to the Jinja2 template file.
        output_folder (str): Path to the output folder.
        include_abstract (bool): Flag to include abstract and download link in the markdown file.
    """
    logging.info(f"Converting .bib files to markdown using template {template_path}")
    all_bib_data = collections.defaultdict(lambda: collections.defaultdict(dict))
    for bib_file in bib_files:
        bib_data = parse_bib_file(bib_file)
        all_bib_data.update(bib_data)
    template, undeclared_variables = load_jinja_template(template_path)
    generate_markdown_files(all_bib_data, template, undeclared_variables, output_folder, include_abstract)


def parse_ris_file(ris_file_path: str) -> collections.defaultdict:
    """
    Parse the .ris file and structure the data.

    Args:
        ris_file_path (str): The path to the .ris file.

    Returns:
        defaultdict: A nested defaultdict containing parsed bibliographic data.
    """
    try:
        from .rispy_handler import parse_ris_file as parse_ris
    except ImportError:
        # Fall back to direct import when running as script
        from bib2md.rispy_handler import parse_ris_file as parse_ris
    return parse_ris(ris_file_path)


def convert_ris_to_md(ris_files: List[str], template_path: str, output_folder: str,
                      include_abstract: bool = False) -> None:
    """
    Convert .ris files to markdown files using a Jinja2 template.

    Args:
        ris_files (list): List of paths to .ris files.
        template_path (str): The path to the Jinja2 template file.
        output_folder (str): Path to the output folder.
        include_abstract (bool): Flag to include abstract and download link in the markdown file.
    """
    logging.info(f"Converting .ris files to markdown using template {template_path}")
    all_ris_data = collections.defaultdict(lambda: collections.defaultdict(dict))
    for ris_file in ris_files:
        ris_data = parse_ris_file(ris_file)
        all_ris_data.update(ris_data)
    template, undeclared_variables = load_jinja_template(template_path)
    generate_markdown_files(all_ris_data, template, undeclared_variables, output_folder, include_abstract)


def setup_environment(template_dir: str) -> jinja2.Environment:
    """Set up the Jinja2 environment with our filters and globals.

    Args:
        template_dir (str): The directory containing the templates.

    Returns:
        jinja2.Environment: The configured Jinja2 environment.
    """
    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    
    # Add custom filter for prepending URLs
    def prepend_filter(value, prefix='', default=''):
        if value:
            return f"{prefix}{value}"
        return default
    
    env.filters['prepend'] = prepend_filter
    
    return env


def generate_html_papers_list(papers: List[Dict[str, Any]], template_path: str, output_file: str, 
                             combined_bib_path: str = None, combined_ris_path: str = None) -> None:
    """Generate an HTML list of papers.

    Args:
        papers (List[Dict[str, Any]]): List of dictionaries containing paper metadata
        template_path (str): Path to the Jinja2 template
        output_file (str): Path to the output HTML file
        combined_bib_path (str, optional): Path to the combined BibTeX file. Defaults to None.
        combined_ris_path (str, optional): Path to the combined RIS file. Defaults to None.
    """
    # Set up Jinja2 environment
    template_dir = os.path.dirname(template_path)
    template_file = os.path.basename(template_path)
    env = setup_environment(template_dir)

    # Load the template
    template = env.get_template(template_file)

    # Check if combined files exist
    combined_bib_exists = os.path.exists(combined_bib_path) if combined_bib_path else False
    combined_ris_exists = os.path.exists(combined_ris_path) if combined_ris_path else False
    
    # Get relative paths for combined files
    if combined_bib_path:
        combined_bib_rel_path = os.path.relpath(combined_bib_path, os.path.dirname(output_file))
    else:
        combined_bib_rel_path = ''
    
    if combined_ris_path:
        combined_ris_rel_path = os.path.relpath(combined_ris_path, os.path.dirname(output_file))
    else:
        combined_ris_rel_path = ''

    # Render the template
    html_content = template.render(
        papers=papers,
        combined_bib_exists=combined_bib_exists,
        combined_ris_exists=combined_ris_exists,
        combined_bib_path=combined_bib_rel_path,
        combined_ris_path=combined_ris_rel_path
    )

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Write HTML to file
    with open(output_file, 'w') as f:
        f.write(html_content)

    logging.info(f"Generated HTML paper list at {output_file}")


def process_reference_files(ref_path: str, md_template_path: str, output_folder: str, 
                           include_abstract: bool = False, html_template_path: str = None, 
                           html_output: str = None, combined_bib: str = None, combined_ris: str = None) -> None:
    """
    Process reference files (.bib and .ris) and convert them to markdown and/or HTML files.

    Args:
        ref_path (str): Path to a reference file or a directory containing reference files.
        md_template_path (str): The path to the Jinja2 markdown template file.
        output_folder (str): Path to the output folder.
        include_abstract (bool): Flag to include abstract and download link in the markdown file.
        html_template_path (str, optional): The path to the Jinja2 HTML template file.
        html_output (str, optional): Path to the output HTML file.
        combined_bib (str, optional): Path to save the combined BibTeX file (including converted RIS).
        combined_ris (str, optional): Path to save the combined RIS file.
    """
    # Determine input files
    bib_files = []
    ris_files = []
    
    if os.path.isdir(ref_path):
        bib_files = glob.glob(os.path.join(ref_path, "*.bib"))
        ris_files = glob.glob(os.path.join(ref_path, "*.ris"))
    else:
        if ref_path.endswith('.bib'):
            bib_files = [ref_path]
        elif ref_path.endswith('.ris'):
            ris_files = [ref_path]
        else:
            logging.warning(f"Unsupported file format: {ref_path}")
    
    # Convert .bib files to markdown
    if bib_files:
        convert_bib_to_md(bib_files, md_template_path, output_folder, include_abstract)
    
    # Convert .ris files to markdown
    if ris_files:
        convert_ris_to_md(ris_files, md_template_path, output_folder, include_abstract)
    
    # Generate combined BibTeX file (including converted RIS)
    if combined_bib and (bib_files or ris_files):
        try:
            from .concatenate_bib import concatenate_all_to_bib
        except ImportError:
            # Fall back to direct import when running as script
            from bib2md.concatenate_bib import concatenate_all_to_bib
        if os.path.isdir(ref_path):
            concatenate_all_to_bib(ref_path, combined_bib)
        else:
            # Handle single file case
            directory = os.path.dirname(ref_path)
            concatenate_all_to_bib(directory, combined_bib)
    
    # Generate combined RIS file
    if combined_ris and ris_files:
        try:
            from .rispy_handler import concatenate_ris_files
        except ImportError:
            # Fall back to direct import when running as script
            from bib2md.rispy_handler import concatenate_ris_files
        if os.path.isdir(ref_path):
            concatenate_ris_files(ref_path, combined_ris)
        else:
            # Handle single file case
            directory = os.path.dirname(ref_path)
            concatenate_ris_files(directory, combined_ris)
    
    # Generate HTML paper list if template is provided
    if html_template_path and html_output:
        all_ref_data = collections.defaultdict(lambda: collections.defaultdict(dict))
        
        # Parse all .bib files
        for bib_file in bib_files:
            bib_data = parse_bib_file(bib_file)
            all_ref_data.update(bib_data)
        
        # Parse all .ris files
        for ris_file in ris_files:
            ris_data = parse_ris_file(ris_file)
            all_ref_data.update(ris_data)
        
        # Generate HTML paper list
        generate_html_papers_list(list(all_ref_data.values()), html_template_path, html_output, combined_bib, combined_ris)


def ris_to_bibtex_files(input_folder: str, output_file: str) -> None:
    """
    Convert RIS files to BibTeX format.

    Args:
        input_folder (str): Path to the folder containing RIS files.
        output_file (str): Path to the output BibTeX file.
    """
    if not output_file:
        return
        
    logging.info(f"Converting RIS files in {input_folder} to BibTeX format")
    try:
        from .rispy_handler import convert_ris_folder_to_bibtex
    except ImportError:
        # Fall back to direct import when running as script
        from bib2md.rispy_handler import convert_ris_folder_to_bibtex
    
    convert_ris_folder_to_bibtex(input_folder, output_file)
    

def ris_to_markdown(ris_data: collections.defaultdict, template_path: str, output_folder: str,
                   required_variables: Set[str], include_abstract: bool = False) -> None:
    """
    Generate markdown files from parsed RIS data using a Jinja2 template.

    Args:
        ris_data (defaultdict): Parsed RIS data.
        template_path (str): Path to the Jinja2 template file.
        output_folder (str): Path to the output folder.
        required_variables (set): Set of variables required by the template.
        include_abstract (bool): Flag to include abstract and download link in the markdown file.
    """
    # Load the template
    template, _ = load_jinja_template(template_path)
    
    # Generate markdown files
    generate_markdown_files(ris_data, template, required_variables, output_folder, include_abstract)


def get_template_variables(template_path: str) -> Set[str]:
    """
    Get the variables required by a Jinja2 template.

    Args:
        template_path (str): Path to the Jinja2 template file.

    Returns:
        set: Set of variables required by the template.
    """
    _, undeclared_variables = load_jinja_template(template_path)
    return undeclared_variables


def load_bibtex_files(input_dir: str) -> collections.defaultdict:
    """
    Load all BibTeX files in a directory.

    Args:
        input_dir (str): Path to the directory containing BibTeX files.

    Returns:
        defaultdict: Dictionary containing parsed BibTeX data.
    """
    # If input_dir is a directory, find all .bib files
    if os.path.isdir(input_dir):
        bib_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.bib')]
    # If input_dir is a file, check if it's a .bib file
    elif os.path.isfile(input_dir) and input_dir.endswith('.bib'):
        bib_files = [input_dir]
    else:
        bib_files = []
    
    # Parse all BibTeX files
    all_bib_data = collections.defaultdict(lambda: collections.defaultdict(dict))
    for bib_file in bib_files:
        try:
            bib_data = parse_bib_file(bib_file)
            all_bib_data.update(bib_data)
        except Exception as e:
            logging.error(f"Error parsing BibTeX file {bib_file}: {str(e)}")
    
    return all_bib_data


def load_ris_files(input_dir: str) -> collections.defaultdict:
    """
    Load all RIS files in a directory.

    Args:
        input_dir (str): Path to the directory containing RIS files.

    Returns:
        defaultdict: Dictionary containing parsed RIS data.
    """
    # If input_dir is a directory, find all .ris files
    if os.path.isdir(input_dir):
        ris_files = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith('.ris')]
    # If input_dir is a file, check if it's a .ris file
    elif os.path.isfile(input_dir) and input_dir.endswith('.ris'):
        ris_files = [input_dir]
    else:
        ris_files = []
    
    # Parse all RIS files
    all_ris_data = collections.defaultdict(lambda: collections.defaultdict(dict))
    for ris_file in ris_files:
        try:
            ris_data = parse_ris_file(ris_file)
            all_ris_data.update(ris_data)
        except Exception as e:
            logging.error(f"Error parsing RIS file {ris_file}: {str(e)}")
    
    return all_ris_data


def normalize_bibtex_entries(bibtex_data: collections.defaultdict) -> collections.defaultdict:
    """
    Normalize BibTeX entries to ensure consistent structure.

    Args:
        bibtex_data (defaultdict): Dictionary containing parsed BibTeX data.

    Returns:
        defaultdict: Dictionary containing normalized BibTeX data.
    """
    # Ensure all entries have common fields
    for entry_id, entry in bibtex_data.items():
        # Ensure year is present
        if 'year' not in entry:
            entry['year'] = '2022'
        
        # Ensure title is present
        if 'title' not in entry:
            entry['title'] = f"Untitled Entry {entry_id}"
        
        # Ensure date is present
        if 'date' not in entry:
            year = entry.get('year', '2022')
            month = entry.get('month', '01')
            entry['date'] = f"{year}-{month}-01"
        
        # Ensure paper_file_name is present
        if 'paper_file_name' not in entry:
            title = entry.get('title', 'Untitled').replace(' ', '-')
            entry['paper_file_name'] = f"{entry.get('year', '2022')}-{title}.md"
    
    return bibtex_data


def main() -> None:
    """
    Main function to parse command-line arguments and convert reference files to markdown.
    """
    parser = argparse.ArgumentParser(description='Convert .bib and/or .ris files to markdown using a Jinja2 template.')
    parser.add_argument('refpath', type=str, help='Path to a .bib/.ris file or a directory containing reference files')
    parser.add_argument('--template', type=str, required=True, help='Path to the Jinja2 markdown template file')
    parser.add_argument('--output', type=str, required=True, help='Path to the output folder for markdown files')
    parser.add_argument('--include_abstract', action='store_true', default=False,
                        help='Include abstract and download link in the markdown file')
    parser.add_argument('--html_template', type=str, help='Path to the Jinja2 HTML template file for paper list')
    parser.add_argument('--html_output', type=str, help='Path to the output HTML file for paper list')
    parser.add_argument('--combined_bib', type=str, help='Path to save the combined BibTeX file (including converted RIS)')
    parser.add_argument('--combined_ris', type=str, help='Path to save the combined RIS file')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logging.info(
        f"Converting reference files from {args.refpath} using template {args.template} and outputting to {args.output}")

    process_reference_files(args.refpath, args.template, args.output, args.include_abstract, 
                           args.html_template, args.html_output, args.combined_bib, args.combined_ris)


if __name__ == '__main__':
    main()