import collections
import logging
import os
from pybtex.database import parse_file
import jinja2
from jinja2 import meta

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_jinja(templatefile):
    """
    Setup Jinja2 environment and parse the template file to find undeclared variables.
    
    Args:
        templatefile (str): The path to the Jinja2 template file.
    
    Returns:
        tuple: A tuple containing the Jinja2 template and a set of undeclared variables.
    """
    logging.info(f"Setting up Jinja2 environment for template: {templatefile}")
    templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(templatefile)
    template_source = templateEnv.loader.get_source(templateEnv, templatefile)
    parsed_content = templateEnv.parse(template_source)
    undeclared_variables = meta.find_undeclared_variables(parsed_content)
    return template, undeclared_variables

def parse_bib_file(bibdata):
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
        bibdata_parsed[entry]['paper_file_name'] = bibdata_parsed[entry]['year']+'-'+bibdata_parsed[entry]['title'].replace(' ', '-')+'.md'
        bibdata_parsed[entry]['date'] = bibdata_parsed[entry]['year']
    return bibdata_parsed

def write_md(bibdata, template, undeclared_variables):
    """
    Write markdown files using the parsed bibliographic data and Jinja2 template.
    
    Args:
        bibdata (defaultdict): Parsed bibliographic data.
        template (Template): Jinja2 template object.
        undeclared_variables (set): Set of undeclared variables in the template.
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
        output_file = os.path.join(output_folder, bibdata[entry]['paper_file_name'])
        outputText = template.render(template_data)  # this is where to put args to the template renderer
        with open(output_file, "w") as text_file:
            text_file.write(outputText)
            logging.info(f"Markdown file written: {output_file}")

def bib2md(bibfile, templatefile):
    """
    Convert a .bib file to markdown files using a Jinja2 template.
    
    Args:
        bibfile (str): The path to the .bib file.
        templatefile (str): The path to the Jinja2 template file.
    """
    logging.info(f"Converting .bib file {bibfile} to markdown using template {templatefile}")
    bibdata = parse_bib_file(bibfile)
    print(bibdata)
    template, undeclared_variables = setup_jinja(templatefile)
    write_md(bibdata, template, undeclared_variables)

def main():
    bib2md(os.path.join('data', 'example.bib'), 'md_template.jinja2')

if __name__ == '__main__':
    main()
