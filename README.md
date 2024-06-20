# BibTeX to Markdown Converter

This repository contains a script that converts .bib files to markdown files using a Jinja2 template. This is useful
for generating sheets for personal website that uses [Academic pages](https://github.com/academicpages/academicpages.github.io).

## Installation

1. Clone the repository:
    ```
    git clone https://github.com/armandyam/bib2md.git
    cd bib2md
    ```

2. Install the required packages:
    ```
    pip install -r requirements.txt
    ```

## Usage

### Converting a Single .bib File to Markdown

To convert a single .bib file to markdown:

    ```
    python bib2md.py path/to/your.bib
    ```

### Converting All .bib Files in a Directory to Markdown

To convert all .bib files in a directory:

    ```
    python bib2md.py path/to/your/directory
    ```

### Including Abstracts and Download Links

To include abstracts and download links in the markdown files, add the `--include_abstract` flag:

    ```
    python bib2md.py path/to/your.bib --include_abstract
    ```

### Example Command

    ```
    python bib2md.py data/example.bib --template md_template.jinja2 --include_abstract
    ```

Ensure you have the .bib file(s) in the `data` directory and the Jinja2 template (optional argument) in the `templates` directory. Markdown files will be generated in the `output` folder.

## Workflow for Academic Pages

To use this script for your academic pages website:

1. Generate the markdown files using the script as described above.
2. Move the generated markdown files from the `output` folder to your academic pages content folder (_publications).
3. Commit and push the changes to your repository.
4. Your academic pages website will now render the new publications based on the converted markdown files.
