from setuptools import setup, find_packages

setup(
    name='bib2md',
    version='0.23',
    packages=find_packages(),
    install_requires=[
        'pybtex',
        'Jinja2',
    ],
    entry_points={
        'console_scripts': [
            'bib2md=bib2md.bib2md:main', 'concatenate_bib=bib2md.concatenate_bib:main'
        ],
    },
)
