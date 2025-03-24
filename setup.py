from setuptools import setup, find_packages

setup(
    name='bib2md',
    version='0.24',
    packages=find_packages(),
    install_requires=[
        'pybtex',
        'Jinja2',
        'rispy',
    ],
    entry_points={
        'console_scripts': [
            'bib2md=bib2md.bib2md:main',
            'concatbib=bib2md.concatenate_bib:main'
        ],
    },
)
