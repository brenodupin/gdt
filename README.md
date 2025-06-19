<div align="center">
  <img src="img/gdt_no_background.png" width="50%">

$${\color{#E0AF68}{\LARGE\textsf{🧬 Standardizing gene names across organelle genomes 🧬}}}$$  
![Build Status](https://img.shields.io/badge/tests-in_development-yellow)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License](https://img.shields.io/badge/license-MIT-purple)](https://github.com/brenodupin/gdt/blob/master/LICENSE)
[![DOI:10.1101/2025.06.15.659783v1](https://img.shields.io/badge/biorxiv-10.1101/2025.06.15.659783-blue)](https://doi.org/10.1101/2025.06.15.659783)
</div>

# Table of Contents
place_holder

# Overview

GDT (Gene Dictonary Tool) is a protocol for the creation and implementation of a gene dictionary across any type of annotated genomes. This Python library offers a suite of functionalities that enables the manipulation and integration of .gdt files into other pipelines seamlessly.

# Getting Started

## Requirements

- [Python](https://www.python.org/) `(>=3.10)`
- [pandas](https://pandas.pydata.org/) `(>=1.5.3,<3.0.0)`

## Installation
You can install the library with pip:
```shell
pip install gdt
```
> [!NOTE]  
> [biopython](https://biopython.org) `(>=1.80)` is necessary for `AN_missing_gene_dict.ipynb`, and can be installed `with pip install biopython`

## CLI commands

The flags above work on all commands:

|       flag      |   description   |
|-----------------|-----------------|
| `-h`, `--help`      | Show the help message and exit. | 
| `--debug`         | Enable TRACE level in file, and DEBUG on console.<br>Default: DEBUG level on file and INFO on console. |
| `--log LOG`       | Path to the log file. If not provided, a default log file will be created. |
| `--quiet`         | Suppress console output. Default: console output enabled. |
| `--version`      | Show the version of the gdt package. |

### `gdt-cli filter`
The filter command is used to filter GFF3 files that are indexed via a TSV file, creating `AN_missing_dbxref.txt` and/or `AN_missing_gene_dict.txt` based on the provided .gdt file.

|       flag      |   description   |
|-----------------|-----------------|
| `--tsv TSV`       | TSV file with indexed GFF3 files to filter. |
| `--AN-column AN_COLUMN` | Column name for NCBI Accession Number inside the TSV. Default: AN |
| `--gdt GDT`       | GDT file to use for filtering. If not provided, an empty GeneDict (i.e., GDT file) will be used. |
| `--keep-orfs`     | Keep ORFs. Default: exclude ORFs. |
| `--workers WORKERS` | Number of workers to use. Default: 0 (use all available cores) |
| `--gff-suffix GFF_SUFFIX` | Suffix for GFF files. Default: '.gff3' |
| `--query-string QUERY_STRING` | Query string that pandas filter features in GFF. Default: 'type in ('gene', 'tRNA', 'rRNA')' |

Usage example: 
```shell
gdt-cli filter --tsv fungi_mt_model2.tsv --gdt fungi_mt_model2_stripped.gdt --debug
```

### `gdt-cli stripped`
The stripped command filters out GeneGeneric (#gn) and Dbxref (#dx) entries from a GDT file, keeping only GeneDescription (#gd) entries and their metadata.

|       flag      |   description   |
|-----------------|-----------------|
| `--gdt_in GDT_IN`, `-gin GDT_IN` | Input GDT file to be stripped. |
| `--gdt_out GDT_OUT`, `-gout GDT_OUT` | New GDT file to create. |
| `--overwrite`     | Overwrite output file, if it already exists. Default: False |

Usage example: 
```shell
gdt-cli stripped --gdt_in ../GeneDictionaries/Result/Fungi_mt.gdt --gdt_out fungi_mt_model2_stripped.gdt --overwrite
```

### `gdt-cli standardize`
The standardize command is used to standardize gene names across features in GFF3 files using a GDT file.
The command has two modes, either single GFF3 file with `--gff` or with a TSV file with indexed GFF3 files with `--tsv`.

|       flag      |   description   |
|-----------------|-----------------|
| `--gff GFF`       | GFF3 file to standardize. |
|<img width=200/> |<img width=500/>|
| `--tsv TSV`       | TSV file with indexed GFF3 files to standardize. |
| `--AN-column AN_COLUMN` | Column name for NCBI Accession Number inside the TSV. Default: AN |
| `--gff-suffix GFF_SUFFIX` | Suffix for GFF files. Default: '.gff3' |
|<img width=200/> |<img width=500/>|
| `--gdt GDT`       | GDT file to use for standardization. |
| `--query-string QUERY_STRING` | Query string that pandas filter features in GFF. Default: 'type in ('gene', 'tRNA', 'rRNA')' |
| `--check`         | Just check for standardization issues, do not modify the GFF3 file. Default: False |
| `--second-place`  | Add gdt-tag pair to the second place in the GFF3 file, after the ID. Default: False (add to the end of the attributes field). |
| `--gdt-tag GDT_TAG` | Tag to use for the GDT key/value pair in the GFF3 file. Default: 'gdt_label='. |
| `--error-on-missing` | Raise an error if a feature is missing in the GDT file. Default: False (just log a warning and skip the feature). |
| `--save-copy`     | Save a copy of the original GFF3 file with a .original suffix. Default: False (change inplace). |

Usage example:
```shell
gdt-cli standardize --gff sandbox/fungi_mt/HE983611.1.gff3 --gdt sandbox/fungi_mt/misc/gdt/fungi_mt_pilot_07.gdt --save-copy
```
```shell
gdt-cli gdt-cli standardize --tsv sandbox/fungi_mt/fungi_mt.tsv --gdt sandbox/fungi_mt/misc/gdt/fungi_mt_pilot_07.gdt
--second --debug --log test1.log
```

## Library usage
You can use the library in your own Python scripts. The main interface is the `GeneDict` class, where you can load a GDT file and use its methods to manipulate it.
```python
from gdt import GeneDict

gene_dict = gdt.create_gene_dict("path/to/gdt_file.gdt")
type(gene_dict)
# <class 'gdt.gene_dict.GeneDict'>
# GeneDict object with methods to manipulate the GDT file
```

work in progress
```
├── CITATION.cff       <- Contains metadata on how the project might eventually be published. 
├── LICENSE
├── Makefile           <- Makefile with commands like `make data` or `make train`
├── README.md          <- The top-level README for developers using this project.
├── config             <- Configuration options for the analysis. 
|   ├── config.yaml    <- Snakemake config file. 
|   └── samples.tsv    <- A metadata table for all the samples run in the analysis.  
│
├── docs               <- A default Sphinx project; see sphinx-doc.org for details
│
├── environment.yaml   <- The requirements file for reproducing the analysis environment, e.g.
│                         generated with `conda env export > environment.yaml`
│
├── img                <- A place to store images associated with the project/pipeline, e.g. a 
│                         a figure of the pipeline DAG. 
│
├── notebooks          <- Jupyter or Rmd notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
│
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
│
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
│
├── resources          <- Place for data. By default excluded from the git repository. 
│   ├── external       <- Data from third party sources.
│   └── raw_data       <- The original, immutable data dump.
│
├── results            <- Final output of the data processing pipeline. By default excluded from the git repository.
│ 
├── sandbox            <- A place to test scripts and ideas. By default excluded from the git repository.
│ 
├── scripts            <- A place for short shell or python scripts.
│ 
├── setup.py           <- Makes project pip installable (pip install -e .) so src can be importe
│
├── src                <- Source code for use in this project.
│   ├── __init__.py    <- Makes src a Python module
├── tox.ini            <- tox file with settings for running tox; see tox.readthedocs.io
│
├── workflow           <- Place to store the main pipeline for rerunning all the analysis. 
│   ├── envs           <- Contains different conda environments in .yaml format for running the pipeline. 
│   ├── rules          <- Contains .smk files that are included by the main Snakefile, including common.smk for functions. 
│   ├── scripts        <- Contains different R or python scripts used by the script: directive in Snakemake.
│   ├── Snakefile      <- Contains the main entrypoint to the pipeline.
│ 
├── workspace          <- Space for intermediate results in the pipeline. By default excluded from the git repository.  
```

<p><small>Project inspired by the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>
