# BibTeX to Markdown Converter

[![bib2md](https://github.com/armandyam/bib2md/actions/workflows/python-app.yml/badge.svg)](https://github.com/armandyam/bib2md/actions/workflows/python-app.yml)

This repository contains a script that converts .bib and .ris files to markdown files using a Jinja2 template. This is useful for generating sheets for personal websites that use [Academic pages](https://github.com/academicpages/academicpages.github.io). It can also generate an HTML list of all publications from reference files.

## Installation

1. Clone the repository:
    ```
    git clone https://github.com/armandyam/bib2md.git
    cd bib2md
    ```

2. Install the required packages and the package itself:
    ```
    pip install -r requirements.txt
    pip install .
    ```

## Usage

### Converting Reference Files to Markdown

To convert reference files (.bib or .ris) to markdown:

```
bib2md path/to/your_file --template path/to/md_template.jinja2 --output path/to/output
```

### Converting All Reference Files in a Directory to Markdown

To convert all reference files (.bib and .ris) in a directory:

```
bib2md path/to/your/directory --template path/to/md_template.jinja2 --output path/to/output
```

### Including Abstracts and Download Links

To include abstracts and download links in the markdown files, add the `--include_abstract` flag:

```
bib2md path/to/your_file --template path/to/md_template.jinja2 --output path/to/output --include_abstract
```

### Generating an HTML List of Papers

To generate an HTML file containing a list of all papers from the reference files:

```
bib2md path/to/your/directory --template path/to/md_template.jinja2 --output path/to/output --html_template path/to/html_template.jinja2 --html_output path/to/output/papers.html
```

### Creating a Combined BibTeX File (Including Converted RIS Files)

To convert all RIS files to BibTeX format and combine them with BibTeX files into a single BibTeX file:

```
bib2md path/to/your/directory --template path/to/md_template.jinja2 --output path/to/output --combined_bib path/to/output/publications.bib
```

### Complete Example Command

```
bib2md data/ --template templates/md_template.jinja2 --output output/ --include_abstract --html_template templates/html_papers_list.jinja2 --html_output output/papers.html --combined_bib output/publications.bib --combined_ris output/publications.ris
```

This command will:
1. Convert all BIB and RIS files in the 'data/' directory to markdown files in the 'output/' directory
2. Include abstracts and download links in the markdown files
3. Generate an HTML list of papers at 'output/papers.html'
4. Create a combined BibTeX file (with converted RIS entries) at 'output/publications.bib'
5. Create a combined RIS file at 'output/publications.ris'

Ensure you have the reference file(s) (.bib and/or .ris) in the specified path and the Jinja2 templates in their respective paths.

### Concatenating Multiple Reference Files

There are several options for concatenating reference files:

```
# BibTeX only (original files)
concatbib data/ --output_bib output/combined.bib

# RIS only (original files)
concatbib data/ --output_ris output/combined.ris

# Both formats (original files)
concatbib data/ --output_bib output/combined.bib --output_ris output/combined.ris

# Convert RIS to BibTeX and combine all into a single BibTeX file
concatbib data/ --all_to_bib output/publications.bib
```

For backward compatibility, the following is also supported:

```
concatbib data/ --output output/combined.bib
```

### Example Command

```
concatbib data/ --output_bib output/combined.bib --output_ris output/combined.ris
```

Ensure you have the reference files in the specified directory. The combined files will be generated at the specified output paths.

## Workflow for Academic Pages

To use this package for your academic pages website:

1. Generate the markdown files using the package as described above.
2. Move the generated markdown files from the `output` folder to your academic pages content folder (_publications).
3. Commit and push the changes to your repository.
4. Your academic pages website will now render the new publications based on the converted markdown files.

## Programmatic Usage

You can also use this package programmatically within your Python code:

```python
from bib2md.bib2md import process_reference_files

# Basic usage to convert reference files to markdown
process_reference_files(
    "/path/to/your/directory", 
    "/path/to/jinja/template/md_template.jinja2", 
    "path/to/output", 
    include_abstract=True
)

# Generate markdown files and an HTML paper list
process_reference_files(
    "/path/to/your/directory", 
    "/path/to/jinja/template/md_template.jinja2", 
    "path/to/output", 
    include_abstract=True,
    html_template_path="/path/to/jinja/template/html_papers_list.jinja2",
    html_output="path/to/output/papers.html"
)

# Generate markdown files, HTML paper list, and combined BibTeX file
process_reference_files(
    "/path/to/your/directory", 
    "/path/to/jinja/template/md_template.jinja2", 
    "path/to/output", 
    include_abstract=True,
    html_template_path="/path/to/jinja/template/html_papers_list.jinja2",
    html_output="path/to/output/papers.html",
    combined_bib="path/to/output/publications.bib",
    combined_ris="path/to/output/publications.ris"
)
```

## Concatenate Reference Files Programmatically

You can also concatenate reference files programmatically within your Python code:

```python
from bib2md.concatenate_bib import concatenate_reference_files

# Concatenate both BibTeX and RIS files (separate files)
concatenate_reference_files(
    "/path/to/your/directory", 
    output_bib="/path/to/output/combined.bib",
    output_ris="/path/to/output/combined.ris"
)

# Concatenate BibTeX files only
concatenate_reference_files(
    "/path/to/your/directory", 
    output_bib="/path/to/output/combined.bib"
)

# Concatenate RIS files only
concatenate_reference_files(
    "/path/to/your/directory", 
    output_ris="/path/to/output/combined.ris"
)

# Convert RIS to BibTeX and combine all in one BibTeX file
concatenate_reference_files(
    "/path/to/your/directory", 
    all_to_bib="/path/to/output/publications.bib"
)
```

## Running Tests

To run the unit tests, use the following command:

```bash
python -m unittest discover tests
```

## Contributions

[Jeyashree Krishnan](https://github.com/krishnanj) contributed to this repository.

