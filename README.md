# BibTeX to Markdown Converter

This repository contains a script that converts .bib files to markdown files using a Jinja2 template. This is useful
for generating sheets for personal website that uses [Academic pages](https://github.com/academicpages/academicpages.github.io).

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/armandyam/bib2md.git
    cd bib2md
    ```

2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To convert a .bib file to markdown:

```bash
python bib2md.py
```