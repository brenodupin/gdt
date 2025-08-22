<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github.com/brenodupin/gdt/releases/download/v1.0.0/GDT_logo_dark_mode.png">
    <source media="(prefers-color-scheme: light)" srcset="https://github.com/brenodupin/gdt/releases/download/v1.0.0/GDT_logo_light_mode.png">
    <img src="https://github.com/brenodupin/gdt/releases/download/v1.0.0/GDT_logo_light_mode.png" width="50%" alt="GDT Logo">
  </picture>

$${\color{#E0AF68}{\LARGE\textsf{🧬 Standardizing gene names across organelle genomes 🧬}}}$$  
<br>
![Build Status](https://img.shields.io/badge/tests-in_development-yellow)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Linting: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/charliermarsh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License](https://img.shields.io/badge/license-MIT-purple)](https://github.com/brenodupin/gdt/blob/master/LICENSE)
[![DOI:10.1101/2025.06.15.659783v1](https://img.shields.io/badge/biorxiv-10.1101/2025.06.15.659783-blue)](https://doi.org/10.1101/2025.06.15.659783)
</div>


# Table of Contents

- [Overview](#overview)
- [Getting Started](#getting-started)
  - [Requirements](#requirements)
  - [Installation](#installation)
- [GDICT Format](#gdict-format)
  - [tl;dr](#tldr)
    - [Quick Overview](#quick-overview)
    - [Basic Format](#basic-format)
    - [Entry Types](#entry-types)
    - [Label Convention](#label-convention)
    - [Complete Specification](#complete-specification)
  - [Creation Process](#creation-process)
- [CLI commands](#cli-commands)
  - [`filter`](#filter)
  - [`stripped`](#stripped)
  - [`standardize`](#standardize)
- [Library usage](#library-usage)
- [Project structure](#project-structure)


# Overview

GDT (Gene Dictonary Tool) is a protocol for the creation and implementation of a gene dictionary across any type of annotated genomes. This Python package offers a suite of functionalities that enables the manipulation and integration of .gdict files into other pipelines seamlessly.

# Getting Started

## Requirements

### `gdt` Library
- [Python](https://www.python.org/) `(>=3.10)`
- [pandas](https://pandas.pydata.org/) `(>=1.5.3,<3.0.0)`

### Notebooks
- [Python](https://www.python.org/) `(>=3.10)`
- [gdt](https://github.com/brenodupin/gdt) `(>=1.0.0)`
- [pandas](https://pandas.pydata.org/) `(>=1.5.3,<3.0.0)`
- [biopython](https://biopython.org) `(>=1.80)`

## Installation
### `gdt`
You can install the library with pip:
```shell
pip install gdt
```
### Notebooks
To run the Jupyter notebooks, you need to install gdt and biopython.:
```shell
pip install gdt biopython
```

## GDICT Format
### tl;dr

GDICT (`.gdict`) is a plain-text file that stores a `GeneDict` with a human-readable, easily editable, and machine-parsable structure. `.gdict` files are read by `gdt.read_gdict()` and written to by `gdt.GeneDict.to_gdict()`. A GDICT file contains gene nomenclature data (i.e., gene identifiers) and associated metadata (gene names, database cross-references and comments added by the user).

#### Quick Overview
- **File extension**: `.gdict`
- **Structure**: Header + labeled sections with gene data
- **Encoding**: UTF-8
- **Current version**: 0.0.2

#### Basic Format
```
#! version 0.0.2
#! Optional metadata lines

[LABEL]
gene description #gd SOURCE
gene-identifier #gn SOURCE1 SOURCE2
gene-identifier #dx SOURCE:GeneID
```

#### Entry Types
- **`#gd`** - Gene descriptions (names from NCBI Gene, etc.)
- **`#gn`** - Gene identifiers from genome annotations  
- **`#dx`** - Database cross-references with GeneIDs

#### Label Convention

We propose a label naming convention that is based on the [HGNC](https://www.genenames.org/) human mitochondrial gene nomenclature, but adapted to accommodate other organelles and genetic compartments. The labels are structured as `<prefix>-<symbol>`, where `<prefix>` is a three-letter code representing the genetic compartment, and `<symbol>` is the gene name or identifier.

**The GDT library will not enforce any label naming convention** (even our own!), helping you rename and remove labels with the `gdt.GeneDict.rename_labels()` and `gdt.GeneDict.remove_labels()` methods, respectively.

#### Complete Specification
You can read more about it at the [GDICT File Specification](https://github.com/brenodupin/gdt/blob/master/GDICT_FILE_SPECIFICATION.md)

### Creation Process

The process of creating a GDICT file is not fully automated because it requires extensive user input and curation. To facilitate this process, we provide two Jupyter notebooks that guide the user through the steps of creating a GDICT file from scratch or from an existing stripped GDICT file. These notebooks are designed to be run interactively, allowing the user to make decisions and curate the entries as needed.  
We provide our GDICT files (also in stripped form) for a most organelle genomes (public avaible at NCBI), which can be used as a starting point for creating new GDICT files.

A more detailed description of the process can be found in the preprint: [Protocol for GDT, Gene Dictionary Tool, to create and implement a gene dictionary across annotated genomes](https://doi.org/10.1101/2025.06.15.659783)


## CLI commands

The flags below work on all commands:

|       flag      |   description   |
|-----------------|-----------------|
| `-h`, `--help`      | Show the help message and exit. | 
| `--debug`         | Enable TRACE level in file, and DEBUG on console.<br>Default: DEBUG level on file and INFO on console. |
| `--log LOG`       | Path to the log file. If not provided, a default log file will be created. |
| `--quiet`         | Suppress console output. |
| `--version`      | Show the version of the gdt package. |

### `gdt-cli filter`
The filter command is used to filter GFF3 files that are indexed via a TSV file, it may create `AN_missing_dbxref.txt` and/or `AN_missing_gene_dict.txt` based on the provided .gdict file.

|       flag      |   description   |
|-----------------|-----------------|
| `--tsv TSV`       | TSV file with indexed GFF3 files to filter. |
| `--AN-column AN_COLUMN` | Column name for NCBI Accession Number inside the TSV. Default: AN |
| `--gdict GDICT`       | GDICT file to use for filtering. If not provided, an empty GeneDict (i.e., GDICT file) will be used. |
| `--keep-orfs`     | Keep ORFs. Default: exclude ORFs. |
| `--workers WORKERS` | Number of workers to use. Default: 0 (use all available cores) |
| `--gff-suffix GFF_SUFFIX` | Suffix for GFF files. Default: '.gff3' |
| `--query-string QUERY_STRING` | Query string that pandas filter features in GFF. Default: 'type in ('gene', 'tRNA', 'rRNA')' |

Usage example: 
```shell
gdt-cli filter --tsv fungi_mt_model2.tsv --gdict fungi_mt_model2_stripped.gdict --debug
```

### `gdt-cli stripped`
The stripped command filters out GeneGeneric (#gn) and Dbxref (#dx) entries from a GDICT file, keeping only GeneDescription (#gd) entries and their metadata.

|       flag      |   description   |
|-----------------|-----------------|
| `--gdict_in GDT_IN`, `-gin GDICT_IN` | Input GDICT file to be stripped. |
| `--gdict_out GDT_OUT`, `-gout GDICT_OUT` | New GDICT file to create. |
| `--overwrite`     | Overwrite output file, if it already exists. Default: False |

Usage example: 
```shell
gdt-cli stripped --gdict_in ../GeneDictionaries/Result/Fungi_mt.gdict --gdict_out fungi_mt_model2_stripped.gdict --overwrite
```

### `gdt-cli standardize`
The standardize command is used to standardize gene names across features in GFF3 files using a GDT file.
The command has two modes, either single GFF3 file with `--gff` or a TSV file with indexed GFF3 files with `--tsv`.

|       flag      |   description   |
|-----------------|-----------------|
| `--gff GFF`       | GFF3 file to standardize. |
|<img width=200/> |<img width=500/>|
| `--tsv TSV`       | TSV file with indexed GFF3 files to standardize. |
| `--AN-column AN_COLUMN` | Column name for NCBI Accession Number inside the TSV. Default: AN |
| `--gff-suffix GFF_SUFFIX` | Suffix for GFF files. Default: '.gff3' |
|<img width=200/> |<img width=500/>|
| `--gdict GDICT`       | GDICT file to use for standardization. |
| `--query-string QUERY_STRING` | Query string that pandas filter features in GFF. Default: 'type in ('gene', 'tRNA', 'rRNA')' |
| `--check`         | Just check for standardization issues, do not modify the GFF3 file. Default: False |
| `--second-place`  | Add gdt_tag pair to the second place in the GFF3 file, after the ID. Default: False (add to the end of the attributes field). |
| `--gdt-tag GDT_TAG` | Tag to use for the GDT key/value pair in the GFF3 file. Default: 'gdt_label='. |
| `--error-on-missing` | Raise an error if a feature is missing in the GDT file. Default: False (just log a warning and skip the feature). |
| `--save-copy`     | Save a copy of the original GFF3 file with a .original suffix. Default: False (change inplace). |

Usage example:
```shell
gdt-cli standardize --gff sandbox/fungi_mt/HE983611.1.gff3 --gdict sandbox/fungi_mt/misc/gdt/fungi_mt_pilot_07.gdict --save-copy
```
```shell
gdt-cli standardize --tsv sandbox/fungi_mt/fungi_mt.tsv --gdict sandbox/fungi_mt/misc/gdt/fungi_mt_pilot_07.gdict --second-place --debug --log test1.log
```

## Library usage
You can use the library in your own Python scripts. The main interface is the `GeneDict` class, where you can load a GDT file and use its methods to manipulate it.

Since `GeneDict` inherits from `collections.UserDict`, it behaves like a dictionary, allowing you manipulate its entries using standard dictionary methods. The metadata are stored as attributes of the `GeneDict` object, which can be accessed directly.
They are:
- `version`: The version of the GDT file. ("0.0.2")
- `header`: A list of strings containing the header lines from the GDT file.
- `info`: An instance of `GeneDictInfo` containing metadata about its entries (This information is only calculated when `update_info()` is called, or when `lazy_info` is set to `False` at start).
    
   - `labels`: The number of unique gene labels in the GDT file.
   - `total_entries`: The total number of entries in the GDT file.
   - `gene_descriptions`: The number of gene description entries (#gd) in the GDT file.
   - `gene_generics`: The number of gene generic entries (#gn) in the GDT file.
   - `dbxref_GeneIDs`: The number of dbxref entries (#dx) that contain GeneID in the GDT file.

To read a GDT file, you can use the `read_gdict()` function, which returns a `GeneDict` object. You can then manipulate it as needed and save it back to a GDT file using the `to_gdict()` method.

```python
import gdt

# Read a GDT file
gene_dict = gdt.read_gdict("path/to/your.gdict")
# Check the type of the object
print(type(gene_dict))  # <class 'gdt.gdict.GeneDict'>
# Access metadata
print(gene_dict.version)  # "0.0.2"
gene_dict.update_info()  # Update the info attribute with metadata
print(gene_dict.info.labels)  # Number of unique gene labels
print(gene_dict.info.total_entries)  # Total number of entries

# Manipulate the GeneDict as needed
# For example, you can access a specific entry by its key
print(gene_dict["gene-ATP8"])  # Access the entry for 'gene-ATP8'

# Save the GeneDict back to a GDT file
gene_dict.to_gdict("path/to/your_output.gdict", overwrite=True)
```
All GDT functions and classes are documented with docstrings, so you can use the `help()` function to get more information about them. A full documentation of the library is being built with Sphinx and can be found in the `docs` folder later on.

## Project structure

We follow a project structure inspired by [cookiecutter-bioinformatics-project](https://github.com/maxplanck-ie/cookiecutter-bioinformatics-project), with some modifications to better suit our needs. Below is an overview of the project structure:

```
├── CITATION.cff        <- Contains metadata on how the project might eventually be published. 
├── LICENSE
├── README.md           <- The top-level README for developers using this project. 
│
├── docs                <- A default Sphinx project; see sphinx-doc.org for details
│
│
├── img                 <- A place to store images associated with the project/pipeline, e.g. a 
│                         a figure of the pipeline DAG. 
│
├── notebooks           <- Jupyter or Rmd notebooks.
│
├── resources           <- Place for data.
│   ├── stripped        <- Stripped down GDICT files, from our protocol, containing only the #gd entries.
│   └── pilot           <- Complete GDICT files, containing all entries (#gd, #gn, #dx) from our protocol.
│
├── example             <- Example data.
│ 
├── sandbox             <- A place to test scripts and ideas. By default excluded from the git repository.
│ 
├── pyproject.toml      <- Makes project pip installable (pip install -e .) so src can be imported.
│
├─ src                  <- Source code for use in this project.
│  └─ gdt               <- Package containing the main library code.
│     ├── __init__.py   <- Makes src/gdt a package.
│     ├── cli.py        <- Contains the command line interface for the gdt package.
│     ├── gdt_impl.py   <- Contains the main implementation of the GeneDict class and its methods.
│     ├── gff3_utils.py <- Contains utility functions for working with GFF files.
|     └── log_setup.py  <- Contains the logger configuration for the gdt package.
│
├── tox.ini             <- tox file with settings for running tox; see tox.readthedocs.io 
|
|── ruff.toml           <- ruff configuration file for linting; see https://docs.astral.sh/ruff/configuration/
|
|── uv.lock             <- uv configuration file for versioning; see https://docs.astral.sh/uv/concepts/projects/sync/
```
