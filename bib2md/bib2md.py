import collections
import logging
import os
import argparse
from typing import Tuple, List, Set, Union
from pybtex.database import parse_file, BibliographyData
import jinja2
from jinja2 import Template, meta
import importlib.resources as resources

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def setup_jinja(templatefile: str) -> Tuple[Template, Set[str]]:
    """
    Setup Jinja2 environment and parse the template file to find undeclared variables.

    Args:
        templatefile (str): The path to the Jinja2 template file.

    Returns:
        tuple: A tuple containing the Jinja2 template and a set of undeclared variables.
    """
    logging.info(f"Setting up Jinja2 environment for template: {templatefile}")
    # Load the template from the package resources
    with resources.path('bib2md.templates', templatefile) as template_path:
        templateLoader = jinja2.FileSystemLoader(searchpath=template_path.parent)
        templateEnv = jinja2.Environment(loader=templateLoader)
        template = templateEnv.get_template(templatefile)
        with open(template_path) as f:
            template_source = f.read()
        parsed_content = templateEnv.parse(template_source)
        undeclared_variables = meta.find_undeclared_variables(parsed_content)
        return template, undeclared_variables

def parse_bib_file(bibdata: str) -> collections.defaultdict:
    """
    Parse the .bib file and structure the data.
    
    Args:
        bibdata (str): The path to the .bib file.
    
    Returns:
        defaultdict: A nested defaultdict containing parsed bibliographic data.
    """
    logging.info(f"Parsing .bib file: {bibdata}")
    bibdata_parsed = collections.defaultdict(lambda: collections.defaultdict(dict))
    bib_data = parse_file(bibdata)
    for entry in bib_data.entries:
        for field in bib_data.entries[entry].fields:
            bibdata_parsed[entry][field.lower().replace('-', '_')] = bib_data.entries[entry].fields[field]
        author_list = []
        for person in bib_data.entries[entry].persons:
            authors = bib_data.entries[entry].persons[person]
            for author in authors:
                author_first_name = ' '.join(author.first_names)
                author_last_name = ' '.join(author.last_names)
                author_list.append(author_first_name + ' ' + author_last_name)
        bibdata_parsed[entry]['authors_list'] = ', '.join(author_list)
        bibdata_parsed[entry]['paper_file_name'] = bibdata_parsed[entry]['year'] + '-' + bibdata_parsed[entry]['title'].replace(' ', '-') + '.md'
        # Ensure date is set
        year = bibdata_parsed[entry].get('year', '2022')
        month = bibdata_parsed[entry].get('month', '01')
        bibdata_parsed[entry]['date'] = f"{year}-{month}-01"
    return bibdata_parsed

def write_md(bibdata: collections.defaultdict, template: Template, undeclared_variables: Set[str], include_abstract: bool = False) -> None:
    """
    Write markdown files using the parsed bibliographic data and Jinja2 template.
    
    Args:
        bibdata (defaultdict): Parsed bibliographic data.
        template (Template): Jinja2 template object.
        undeclared_variables (set): Set of undeclared variables in the template.
        include_abstract (bool): Flag to include abstract and download link in the markdown file.
    """
    logging.info("Writing markdown files from bibliographic data")
    output_folder = 'output'
    os.makedirs(output_folder, exist_ok=True)  # Create 'output' folder if it doesn't exist
    for entry in bibdata:
        template_data = {}
        temp_undeclared_variables = undeclared_variables.copy()
        for value in undeclared_variables:
            if value in bibdata[entry].keys():
                template_data[value] = bibdata[entry][value]
                temp_undeclared_variables.remove(value)
        if len(temp_undeclared_variables) > 0:
            logging.warning(f"The following variables are not defined in the bib file: {temp_undeclared_variables}")
        
        template_data['permalink'] = bibdata[entry]['paper_file_name'].replace(".md", '')
        # Handle abstract and download link
        if not include_abstract:
            template_data['paperurl'] = ''
            template_data['excerpt'] = ''
        else:
            template_data['excerpt'] = template_data.get('abstract', '')
            template_data['paperurl'] = template_data.get('url', '')
        
        output_file = os.path.join(output_folder, bibdata[entry]['paper_file_name'])
        outputText = template.render(template_data)  # this is where to put args to the template renderer
        with open(output_file, "w") as text_file:
            text_file.write(outputText)
            logging.info(f"Markdown file written: {output_file}")

def bib2md(bibfiles: List[str], templatefile: str, include_abstract: bool = False) -> None:
    """
    Convert .bib files to markdown files using a Jinja2 template.
    
    Args:
        bibfiles (list): List of paths to .bib files.
        templatefile (str): The path to the Jinja2 template file.
        include_abstract (bool): Flag to include abstract and download link in the markdown file.
    """
    logging.info(f"Converting .bib files to markdown using template {templatefile}")
    all_bibdata = collections.defaultdict(lambda: collections.defaultdict(dict))
    for bibfile in bibfiles:
        bibdata = parse_bib_file(bibfile)
        all_bibdata.update(bibdata)
    template, undeclared_variables = setup_jinja(templatefile)
    write_md(all_bibdata, template, undeclared_variables, include_abstract)

def main() -> None:
    parser = argparse.ArgumentParser(description='Convert .bib files to markdown using a Jinja2 template.')
    parser.add_argument('bibpath', type=str, help='Path to a .bib file or a directory containing .bib files')
    parser.add_argument('--template', type=str, default='md_template.jinja2', help='Path to the Jinja2 template file')
    parser.add_argument('--include_abstract', action='store_true', default=False, help='Include abstract and download link in the markdown file')
    args = parser.parse_args()

    if os.path.isdir(args.bibpath):
        bibfiles = [os.path.join(args.bibpath, f) for f in os.listdir(args.bibpath) if f.endswith('.bib')]
    else:
        bibfiles = [args.bibpath]

    bib2md(bibfiles, args.template, args.include_abstract)

if __name__ == '__main__':
    main()
