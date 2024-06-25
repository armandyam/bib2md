from setuptools import setup, find_packages

setup(
    name='bib2md',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'bib2md': ['templates/*.jinja2'],
    },
    install_requires=[
        'pybtex'
        'Jinja2',
    ],
)
