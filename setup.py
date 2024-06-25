from setuptools import setup, find_packages

setup(
    name='bib2md',
    version='0.1',
    include_package_data=True,
    package_data={
        'bib2md': ['templates/*.jinja2'],
    },
    packages=find_packages(),
    install_requires=[
        'pybtex',
        'jinja2',
        'importlib',
        # List any third-party packages required by your package here
    ],
)
