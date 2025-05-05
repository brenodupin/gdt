from setuptools import setup, find_packages

setup(
    name="gdt",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "pandas"
    ],
    author="",
    author_email="",
    python_requires=">=3.10",
    entry_points={
        'console_scripts': [
        'geneDict=gdt.cli:cli_run'],
    },
)