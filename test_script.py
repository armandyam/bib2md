import unittest
import collections
import os
import jinja2
from bib2md import setup_jinja, parse_bib_file, write_md, bib2md

class TestBibToMd(unittest.TestCase):

    def test_setup_jinja(self):
        template, undeclared_variables = setup_jinja('md_template.jinja2')
        self.assertIsInstance(template, jinja2.Template)
        self.assertIsInstance(undeclared_variables, set)

    def test_parse_bib_file(self):
        bibdata = parse_bib_file('data/example.bib')
        self.assertIsInstance(bibdata, collections.defaultdict)
        self.assertTrue('metalindustry' in bibdata)  # Replace 'some_entry' with an actual entry ID from the example.bib

    def test_write_md(self):
        bibdata = parse_bib_file('data/example.bib')
        template, undeclared_variables = setup_jinja('md_template.jinja2')
        write_md(bibdata, template, undeclared_variables)
        # Check if markdown files are created in the 'output' folder as expected, for simplicity assume only one entry
        self.assertTrue(os.path.exists(os.path.join('output', '2015-Aslkjg-asklk-sadfkljls-alskdlkj.md')))  # Replace '2022-Sample-Title.md' with the actual expected file name

    def test_bib2md(self):
        bib2md('data/example.bib', 'md_template.jinja2')
        # Check if markdown files are created in the 'output' folder as expected
        self.assertTrue(os.path.exists(os.path.join('output', '2015-Aslkjg-asklk-sadfkljls-alskdlkj.md')))  # Replace '2022-Sample-Title.md' with the actual expected file name

if __name__ == '__main__':
    unittest.main()
