from setuptools import setup, find_packages

setup(
    name='bib2md',
    version='0.21',
    packages=find_packages(),
    install_requires=[
        'pybtex',
        'Jinja2',
    ],
    entry_points={
        'console_scripts': [
            'bib2md=bib2md.bib2md:main', 'bib2md=bib2md.concatenate_bib:main'
        ],
    },
)
