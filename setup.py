from setuptools import setup, find_packages

setup(
    name='bib2md',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pybtex'
        'jinja2'
        # List any third-party packages required by your package here
    ],
)
