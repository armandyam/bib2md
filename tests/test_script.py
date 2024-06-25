import unittest
import collections
import os
import shutil
import subprocess
import jinja2
from pathlib import Path
from bib2md import setup_jinja, parse_bib_file, write_md, bib2md

class TestBibToMd(unittest.TestCase):

    def setUp(self):
        os.makedirs('output', exist_ok=True)

    def tearDown(self):
        shutil.rmtree('output')

    def test_setup_jinja(self):
        template, undeclared_variables = setup_jinja('md_template.jinja2')
        self.assertIsInstance(template, jinja2.Template)
        self.assertIsInstance(undeclared_variables, set)

    def test_parse_bib_file(self):
        bibdata = parse_bib_file('data/example.bib')
        self.assertIsInstance(bibdata, collections.defaultdict)
        self.assertTrue('journal123456' in bibdata)  # Replace 'journal123456' with an actual entry ID from the example.bib
        self.assertEqual(bibdata['journal123456']['date'], '2024-01-01')  # Test for default date

    def test_write_md(self):
        bibdata = parse_bib_file('data/example.bib')
        template, undeclared_variables = setup_jinja('md_template.jinja2')
        write_md(bibdata, template, undeclared_variables)
        # Check if markdown files are created in the 'output' folder as expected, for simplicity assume only one entry
        self.assertTrue(os.path.exists(os.path.join('output', '2024-An-Innovative-Approach-to-Synthetic-Data-Generation.md')))

    def test_bib2md(self):
        bib2md(['data/example.bib'], 'md_template.jinja2')
        # Check if markdown files are created in the 'output' folder as expected
        self.assertTrue(os.path.exists(os.path.join('output', '2024-An-Innovative-Approach-to-Synthetic-Data-Generation.md')))

    def test_command_line_tool(self):
        # Use subprocess to run the command line tool
        result = subprocess.run(
            ['bib2md', 'data/example.bib', '--template', 'md_template.jinja2', '--include_abstract'],
            capture_output=True,
            text=True
        )
        
        # Check if the command executed successfully
        self.assertEqual(result.returncode, 0)
        # Check if markdown files are created in the 'output' folder as expected
        self.assertTrue(os.path.exists(os.path.join('output', '2024-An-Innovative-Approach-to-Synthetic-Data-Generation.md')))

if __name__ == '__main__':
    unittest.main()
