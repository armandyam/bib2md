
# BibTeX to Markdown Converter

This repository contains a script that converts .bib files to markdown files using a Jinja2 template. This is useful for generating sheets for personal websites that use [Academic pages](https://github.com/academicpages/academicpages.github.io).

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

### Converting a Single .bib File to Markdown

To convert a single .bib file to markdown:

```
bib2md path/to/your.bib --template path/to/md_template.jinja2 --output path/to/output
```

### Converting All .bib Files in a Directory to Markdown

To convert all .bib files in a directory:

```
bib2md path/to/your/directory --template path/to/md_template.jinja2 --output path/to/output
```

### Including Abstracts and Download Links

To include abstracts and download links in the markdown files, add the `--include_abstract` flag:

```
bib2md path/to/your.bib --template path/to/md_template.jinja2 --output path/to/output --include_abstract
```

### Example Command

```
bib2md data/example.bib --template templates/md_template.jinja2 --output output --include_abstract
```

Ensure you have the `.bib` file(s) in the `data` directory and the Jinja2 template (optional argument) in the `templates` directory. Markdown files will be generated in the `output` folder.

### Concatenating Multiple .bib Files

To concatenate all `.bib` files in a directory into a single `.bib` file:

```
concatbib path/to/your/directory --output path/to/output/combined.bib
```

### Example Command

```
concatbib data/bib_files --output output/combined.bib
```

Ensure you have the `.bib` files in the `data/bib_files` directory. The combined `.bib` file will be generated at the specified output path.

## Workflow for Academic Pages

To use this package for your academic pages website:

1. Generate the markdown files using the package as described above.
2. Move the generated markdown files from the `output` folder to your academic pages content folder (_publications).
3. Commit and push the changes to your repository.
4. Your academic pages website will now render the new publications based on the converted markdown files.

## Programmatic Usage

You can also use this package programmatically within your Python code:

```python
from bib2md.bib2md import process_bib_files

process_bib_files("/path/to/your.bib", "/path/to/jinja/template/md_template.jinja2", "path/to/output", include_abstract=True)
```

## Running Tests

To run the unit tests, use the following command:

```bash
python -m unittest discover tests
```

## Concatenate .bib Files Programmatically

You can also concatenate `.bib` files programmatically within your Python code:

```python
from bib2md.concatbib import concatenate_bib_files

concatenate_bib_files("/path/to/your/directory", "/path/to/output/combined.bib")
```
