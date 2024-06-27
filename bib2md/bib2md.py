import collections
import logging
import os
import argparse
from typing import Tuple, List, Set, Union
from pybtex.database import parse_file, BibliographyData
import jinja2
from jinja2 import Template, meta

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
        for field in bib_data.entries[entry].fields:
            bib_data_parsed[entry][field.lower().replace('-', '_')] = bib_data.entries[entry].fields[field]
        author_list = []
        for person in bib_data.entries[entry].persons:
            authors = bib_data.entries[entry].persons[person]
            for author in authors:
                author_first_name = ' '.join(author.first_names)
                author_last_name = ' '.join(author.last_names)
                author_list.append(author_first_name + ' ' + author_last_name)
        bib_data_parsed[entry]['authors_list'] = ', '.join(author_list)
        bib_data_parsed[entry][
            'paper_file_name'] = f"{bib_data_parsed[entry]['year']}-{bib_data_parsed[entry]['title'].replace(' ', '-')}.md"
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


def process_bib_files(bib_path: str, template_path: str, output_folder: str, include_abstract: bool) -> None:
    """
    Process .bib files and convert them to markdown files using a Jinja2 template.

    Args:
        bib_path (str): Path to a .bib file or a directory containing .bib files.
        template_path (str): The path to the Jinja2 template file.
        output_folder (str): Path to the output folder.
        include_abstract (bool): Flag to include abstract and download link in the markdown file.
    """
    if os.path.isdir(bib_path):
        bib_files = [os.path.join(bib_path, f) for f in os.listdir(bib_path) if f.endswith('.bib')]
    else:
        bib_files = [bib_path]

    convert_bib_to_md(bib_files, template_path, output_folder, include_abstract)


def main() -> None:
    """
    Main function to parse command-line arguments and convert .bib files to markdown.
    """
    parser = argparse.ArgumentParser(description='Convert .bib files to markdown using a Jinja2 template.')
    parser.add_argument('bibpath', type=str, help='Path to a .bib file or a directory containing .bib files')
    parser.add_argument('--template', type=str, required=True, help='Path to the Jinja2 template file')
    parser.add_argument('--output', type=str, required=True, help='Path to the output folder')
    parser.add_argument('--include_abstract', action='store_true', default=False,
                        help='Include abstract and download link in the markdown file')
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    logging.info(
        f"Converting .bib files from {args.bibpath} using template {args.template} and outputting to {args.output}")

    process_bib_files(args.bibpath, args.template, args.output, args.include_abstract)


if __name__ == '__main__':
    main()