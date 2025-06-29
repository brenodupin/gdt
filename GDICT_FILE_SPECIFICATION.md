# GDICT File Format Specification

Authors: Breno Dupin and Matheus Sanita Lima  
Date: 24 June 2025  
Version: 0.0.2

## Introduction

GDICT (`.gdict`) is a plain-text file that stores a `gdt.GeneDict` with a human-readable, easily editable, and machine-parsable structure. `.gdict` files are read by `gdt.read_gdict()` and written to by `gdt.GeneDict.to_gdict()`. A GDICT file contains gene nomenclature data (i.e., gene identifiers) and associated metadata (gene names, database cross-references and comments added by the user).

## File Structure

A GDICT file consists of three main components:
1. Header section (mandatory).
2. Label definitions.
3. Data entries.

### Header Section

The header section is **mandatory** and consists of lines beginning with `#!`. The header appears only at the start of the file and ends when the first line not starting with `#!` is encountered.

#### Header Format

```
#! version <version_number>
#! <metadata_information>
```

#### Header Fields

- **version** (mandatory): Must be the first line and specify the GDICT format version (currently `0.0.2`).
- **metadata_information** (recommended): Additional metadata lines containing free-form information such as:
  - File name or identifier.
  - Creation/modification timestamps.
  - Processing history.

#### Header Example

```
#! version 0.0.2
#! Fungi_mit
#! 2025-04-09 17:54 - Conversion from v1 gdt to gdt version 0.0.2
#! 2025-06-05 18:11 - Stripped GDICT version from original GDICT file Fungi_mit.gdict
#! 2025-06-11 20:37 - Data added from TEMP 01
#! 2025-06-11 20:50 - Data added from TEMP Symbol 01
#! 2025-06-14 16:00 - Data added from 'Automated insertion of gene_ids with known features from features_info.tsv'
#! 2025-06-14 16:02 - Data added from 'AN_missing_dbxref_GeneID matching 'child + parent' best feature pair'
```

### Label Structure

GDICT files are organized into labeled sections, where each label represents a genome feature (a gene, most times). Labels are defined by headers enclosed in square brackets. All data entries that follow a label header belong to that label until a new label is encountered.

#### Label Header Format

```
[<LABEL>]
```

The `LABEL` should be a unique identifier for the genome feature. We do recommend using a consistent naming convention, with a prefix, as shown in the example below. Read more about it in [Label Naming Conventions](#label-naming-conventions).

### Data Entries

Each labeled section contains data entries that describe various aspects of the genome feature. There are three types of data entries, each with its own specific format. Although most entries are automaticaly generated, manually created (and curated) entries are also allowed.

#### 1. 'Gene Description' Entry (#gd)

'Gene descriptions' are names that describe the given genome feature. These entries mostly come from NCBI Gene (`Gene description` field). These descriptors are not actually encountered in the GFF file (since gene identifiers tend to appear as `ID=gene-<gene_name>`), but are used to provide additional context and information about the gene when querying NCBI Gene.

**Format:**
```
<descriptor> #gd <source> [#c <comment>]
```

- `descriptor`: The gene name or description.
- `source`: The source of the information (e.g., `MANUAL`, `NCBI`).
- `comment` (optional): Additional information marked with `#c`.

**Example:**
```
[MIT-ATP6]
...
ATP6 #gd MANUAL
atp6 #gd NCBI
ATP synthase subunit 6 #gd NCBI #c automated insertion
...
```

The parser `gdt.read_gdict()` will convert this into a `GeneDict` object with the same structure as the following Python code:

```python
import gdt
  
gene_dict = gdt.GeneDict()
gene_dict['ATP6'] = gdt.GeneDescription(label='MIT-ATP6', source='MANUAL')
gene_dict['atp6'] = gdt.GeneDescription(label='MIT-ATP6', source='NCBI')
gene_dict['ATP synthase subunit 6'] = gdt.GeneDescription(label='MIT-ATP6', source='NCBI', c='automated insertion')
```

#### 2. 'Gene Generic' Entry (#gn)

'Gene generic' entries are gene identifiers that can come from multiple genome annotations. These identifiers do not have a direct link to any external database (such as via dbxref GeneID).

**Format:**
```
<gene_identifier> #gn [<source1> <source2> ...] [#c <comment>]
```

- `gene_identifier`: The gene identifier, comes from `ID=<gene_identifier>` in the GFF attributes field.
- `source1`, `source2`, etc.: Zero or more source accession numbers (e.g., `JQ346808.1`, `KX657746.1`).
- `comment` (optional): Additional information marked with `#c`.

**Example:**
```
[MIT-ATP6]
...
gene-AFUA_m0110 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping
gene-atp6 #gn HE983611.1 KX657746.1 #c multiple sources available
gene-AtP6 #gn #c no sources available
...
```
The parser `gdt.read_gdict()` will convert this into a `GeneDict` object with the same structure as the following Python code:

```python
import gdt
  
gene_dict = gdt.GeneDict()
gene_dict['gene-AFUA_m0110'] = gdt.GeneGeneric(label='MIT-ATP6', an_sources=['JQ346808.1'], c='insertion from missing_dbxref_GeneID feature mapping')
gene_dict['gene-atp6'] = gdt.GeneGeneric(label='MIT-ATP6', an_sources=['HE983611.1', 'KX657746.1'], c='multiple sources available')
gene_dict['gene-AtP6'] = gdt.GeneGeneric(label='MIT-ATP6', an_sources=[], c='no sources available')
```

#### 3. 'Database Cross-reference' (dbxref) Entries (#dx)

Database cross-reference entries link to external database entries with specific GeneIDs. In the current version (0.0.2), only NCBI GeneIDs are supported.

**Format:**
```
<gene_identifier> #dx <source>:<GeneID> [#c <comment>]
```

- `gene_identifier`: The gene identifier, comes from `ID=<gene_identifier>` in the GFF attributes field.
- `source`: Source accession number (e.g., `NC_042229.1`, `NC_066216.1`).
- `GeneID`: Numeric gene ID in the database (e.g., `40135497`).
- `comment` (optional): Additional information marked with `#c`. Some conventions are used for comments:
     - `gff_gene: <value>` indicates the `gene=<value>` attribute found in the GFF file.
     - `ncbi_desc: <value>` indicates the `Gene description` field, found when querying the NCBI Gene database using the `GeneID`.
     - `ncbi_symbol: <value>` indicates the `Gene symbol` field, found when querying the NCBI Gene database using the `GeneID`.

**Example:**
```
[MIT-RNRL]
...
gene-ICI09_mgr02 #dx NC_050344.1:58907350 #c ncbi_desc: large subunit ribosomal RNA
gene-N4M62_mgr01 #dx NC_066216.1:74863499 #c gff_gene: rnl
rna-FDY65_mgr02 #dx NC_042229.1:40135507 #c ncbi_desc: large subunit ribosomal RNA
...
```

The parser `gdt.read_gdict()` will convert this into a `GeneDict` object with the same structure as the following Python code:

```python
import gdt
  
gene_dict = gdt.GeneDict()
gene_dict['gene-ICI09_mgr02'] = gdt.DbxrefGeneID(label='MIT-RNRL', an_source='NC_050344.1', GeneID=58907350, c='ncbi_desc: large subunit ribosomal RNA')
gene_dict['gene-N4M62_mgr01'] = gdt.DbxrefGeneID(label='MIT-RNRL', an_source='NC_066216.1', GeneID=74863499, c='gff_gene: rnl')
gene_dict['rna-FDY65_mgr02'] = gdt.DbxrefGeneID(label='MIT-RNRL', an_source='NC_042229.1', GeneID=40135507, c='ncbi_desc: large subunit ribosomal RNA')
```

## Formatting Rules

### Line Structure
- Each data entry occupies a single line.
- Fields are separated by single spaces.
- Lines beginning with `#!` are header lines.
- Lines beginning with `[` and ending with `]` are label headers.
- Empty lines are ignored but recommended between labeled sections for readability.

### Character Encoding
- Files should use UTF-8 encoding.
- `#c`, `#gd`, `#gn`, and `#dx` are used as type markers and should not be used in descriptors or identifiers.
- As `#` is the defining character for type markers, the use of `#` outside of markers should be avoided at all costs.

### Case Sensitivity
Everything in the GDICT file **is** case-sensitive, including labels, gene identifiers, and sources.

### Ordering Conventions
Whereas not mandatory, the following ordering of data entries in a given label is recommended (and implemented in `gdt.GeneDict().to_gdict()`) for clarity:
1. 'Gene description' (`#gd`) entries first.
2. 'Gene generic' (`#gn`) entries second.
3. 'Database cross-reference' (`#dx`) entries last.
4. Within each type, entries should be naturally ordered by their identifiers (gdt provides a `natual_sort()` method to help with this).

## Parsing logic of `gdt.read_gdict()`

### Header Processing
1. The first line must be `#! version 0.0.2`.
2. Continue reading header lines until a line not starting with `#!` is encountered.
3. All header information after `#!` is treated as free-form metadata.

### Data Processing
1. Lines starting with `[` and ending with `]` define the current label.
2. Data entries are processed only when a current label is defined, otherwise they are skipped.
3. Comments are extracted by splitting on `#c` and trimming whitespace.
4. Lines are only considered valid if, and only if, they contain one type marker (`#gd`, `#gn`, or `#dx`).
5. Each data entry is parsed according to its type, extracting the relevant fields and storing them in the `GeneDict` object.

#### Gene Description (#gd)
- Split line on `#gd` to separate descriptor and source.
- Source is everything after `#gd` (trimmed).
- Descriptor is everything before `#gd` (trimmed).

#### Gene Generic (#gn)
- Split line on `#gn` to get sources and identifier.
- Identifier is everything before `#gn` (trimmed).
- Sources are space-separated after `#gn`.
- Multiple sources are supported.
- 'No sources' is allowed (empty after `#gn`).

#### Database Cross-reference (#dx)
- Split line on `#dx` to get accession:geneID and indentifier.
- Identifier is everything before `#dx` (trimmed).
- Split the result on `:` to separate accession and numeric GeneID.
- GeneID must be convertible to integer.

## File Extension

GDICT files should use the `.gdict` file extension.

## Label Naming Conventions

> [!NOTE]  
> Even though our naming conventions were created for internal use, we aimed to create a system to facilitate the large-adoption of GDT and the standardization of (organelle) gene names. The proposed label naming conventions are not mandatory when using GDT, but are highly recommended. The user have total autonomy to change/adapt the labels, as the user sees fit.

The official HGNC ([HUGO Gene Nomenclature Committee](https://www.genenames.org/)) nomenclature for human mitochondrial genes was adopted as a base for our convention. But to achieve a balance between consistency, interoperability, and scope, we have made some changes:

- All labels follow the format `<prefix>-<symbol>`, where `<prefix>` is a three-letter code representing the genetic compartment, and `<symbol>` is the gene name or identifier.

- We have changed the HGNC `MT` prefix to `MIT`, so the labels could account for more cytoplasmic compartments as in:
 - `MIT` for mitochondria;
 - `KNP` for kinetoplast;
 - `PLT` for plastid;
 - `NUC` for nucleus;
 - `API` for apicoplast;
 - `NMP` for nucleomorph.

- We kept the HGNC-approved symbols (but with the changed prefix) for the human mitochondrial protein-coding and tRNA genes.

- The HGNC symbols for rRNA genes (`MT-RNR1` for the 12S rRNA and `MT-RNR2` for the 16S rRNA) were changed to `<prefix>-RNRS` and `<prefix>-RNRL`, respectively.

- For all other genes, we kept the gene labels as close as possible to the gene name (or any piece of identifying information) found in the respective genome annotation. That means that, for most times, we did not lump overlapping naming conventions (e.g., ATPA with ATP1).

- **When** the rRNA gene annotation had information on the rRNA sedimentation coefficient other than 12S and 16s (e.g., 18S, 21S, etc), we labeled it as `<prefix>-RNR##`, wherein ## refers to the respective sedimentation coefficient found in the annotation (e.g., `MT-RNR18` for the 18S rRNA gene).

- Feel free to adapt the labels to your needs, by combining, renaming, removing, or adding new labels.
  
## Complete GDCIT Example File

```
#! version 0.0.2
#! Fungi_mt
#! 2025-04-09 17:54 - Conversion from gdt to gdt2
#! 2025-06-05 18:11 - Stripped GDT version from original GDT file Fungi_mt.gdt
#! 2025-06-11 20:37 - Data added from TEMP 01
#! 2025-06-11 20:50 - Data added from TEMP Symbol 01
#! 2025-06-14 16:00 - Data added from 'Automated insertion of gene_ids with known features from features_info.tsv'
#! 2025-06-14 16:02 - Data added from 'AN_missing_dbxref_GeneID matching 'child + parent' best feature pair'

[MIT-ATP6]
ATP6 #gd MANUAL
atp6 #gd NCBI
Atp6 #gd NCBI
ATP6 protein #gd NCBI
Atp6p #gd NCBI
ATP synthase 6 #gd NCBI
ATP synthase A chain subunit 6 #gd NCBI
ATP synthase F0 subunit 6 #gd NCBI
ATP synthase F0 subunit a #gd NCBI
ATP synthase FO subunit 6 #gd NCBI
ATP synthase protein 6 #gd NCBI
ATP Synthase subunit 6 #gd NCBI
ATP Synthase Subunit 6 #gd NCBI
ATP synthase subunit 6 #gd NCBI
ATP synthase subunit a #gd NCBI
ATPase6 #gd NCBI
ATPase complex subunit 6 #gd NCBI
ATPase subunit 6 #gd NCBI
CnAATP6 #gd NCBI
F1F0 ATP synthase subunit a #gd NCBI
FAMI006Wp #gd NCBI
H(+)-transporting ATPase, F0 subunit 6 #gd NCBI
mitochondrially encoded ATP synthase 6 #gd NCBI
putative ATP synthase, subunit 6 #gd NCBI
gene-AFUA_m0110 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: ATP synthase subunit 6 | type: CDS
gene-atp6 #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-KX657746.1:43686..44465 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgp14 #dx NC_042229.1:40135497 #c gff_gene: atp6
gene-ICI09_mgp12 #dx NC_050344.1:58907367 #c gff_gene: atp6
gene-N4M62_mgp09 #dx NC_066216.1:74863486 #c gff_gene: atp6
gene-Q0085 #dx NC_001224.1:854601 #c gff_gene: ATP6

[MIT-ATP8]
AT8 gene #gd MANUAL
ATP8 #gd NCBI
atp8 #gd NCBI
Atp8 #gd NCBI
ATP8 protein #gd NCBI
Atp8p #gd NCBI
ATP synthase 8 #gd NCBI
ATP synthase A chain subunit 8 #gd NCBI
ATP synthase F0 subunit 8 #gd NCBI
ATP synthase F0 subunit 8 CDS #gd MANUAL
ATP synthase F0 subunit b #gd NCBI
ATP synthase FO subunit 8 #gd NCBI
ATP synthase protein 8 #gd NCBI
ATP Synthase Subunit 8 #gd NCBI
ATP synthase subunit 8 #gd NCBI
ATP synthesase subunit 8 #gd NCBI
ATPase 8 #gd NCBI
ATPase complex subunit 8 #gd NCBI
ATPase subunit 8 #gd MANUAL
ATPase subunit 8 CDS #gd MANUAL
CnAATP8 #gd NCBI
F1F0 ATP synthase subunit 8 #gd NCBI
FAMI005Wp #gd NCBI
H(+)-transporting ATPase, F0 subunit 8 #gd NCBI
mitochondrially encoded ATP synthase 8 #gd NCBI
putative ATP synthase, subunit 8 #gd NCBI
gene-AFUA_m0090 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: ATP synthase subunit 8 | type: CDS
gene-atp8 #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-KX657746.1:43243..43389 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgp07 #dx NC_042229.1:40135532 #c gff_gene: atp8
gene-ICI09_mgp11 #dx NC_050344.1:58907340 #c gff_gene: atp8
gene-N4M62_mgp10 #dx NC_066216.1:74863485 #c gff_gene: atp8
gene-Q0080 #dx NC_001224.1:854600 #c gff_gene: ATP8

[MIT-ATP9]
atp9 #gd NCBI
Atp9 #gd NCBI
ATP9 #gd NCBI
ATP9 protein #gd NCBI
Atp9p #gd NCBI
ATP synthase 9 #gd NCBI
ATP synthase A chain subunit 9 #gd NCBI
ATP synthase F0 subunit 9 #gd NCBI
ATP synthase F0 subunit 9/c #gd NCBI
ATP synthase F0 subunit c #gd NCBI
ATP synthase FO subunit 9 #gd NCBI
ATP Synthase Membrane Subunit 9 #gd NCBI
ATP synthase protein 9 #gd NCBI
ATP synthase sububnit 9 #gd NCBI
ATP synthase subunit 9 #gd NCBI
ATP synthase subunit 9%2C mitochondrial #gd NCBI
ATP synthesase subunit 9 #gd NCBI
ATP synthetase subunit 9 #gd NCBI
ATPase 9 #gd NCBI
ATPase complex subunit 9 #gd NCBI
ATPase subunit 9 #gd NCBI
CnAATP9 #gd NCBI
F0 ATP synthase subunit c #gd NCBI
F-type H+-transporting ATPase subunit c #gd NCBI
FAMI007Wp #gd NCBI
H(+)-transporting ATPase, F0 subunit 9 #gd NCBI
mitochondrially encoded ATP synthase 9 #gd NCBI
OLI1 #gd NCBI
putative ATP synthase, subunit 9 #gd NCBI
gene-AFUA_m0460 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: ATP synthase subunit 9 | type: CDS
gene-atp9 #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-KX657746.1:60840..61070 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgp01 #dx NC_042229.1:40135511 #c gff_gene: atp9
gene-ICI09_mgp07 #dx NC_050344.1:58907344 #c gff_gene: atp9
gene-N4M62_mgp03 #dx NC_066216.1:74863516 #c gff_gene: atp9
gene-Q0130 #dx NC_001224.1:854584 #c ncbi_symbol: OLI1 | ncbi_desc: F0 ATP synthase subunit c

[MIT-CO1]
CnACOX1 #gd NCBI
CO1 #gd MANUAL
cox1 #gd NCBI
Cox1 #gd NCBI
COX1 #gd NCBI
Cox1p #gd NCBI
COXI #gd NCBI
cytochrome c oxidase 1 #gd NCBI
Cytochrome c oxidase subunit 1 #gd NCBI
cytochrome c oxidase subunit 1 #gd NCBI
cytochrome c oxidase subunit I #gd NCBI
cytochrome c oxidase subunit I CDS #gd MANUAL
cytochrome c oxidase subunit I;intron-encoded LAGLIDADG endonuclease #gd NCBI
cytochrome c oxidase subunits 1 and 2 polyprotein #gd NCBI
cytochrome oxidase subunit 1 #gd MANUAL
cytochrome oxidase subunit 1 CDS #gd MANUAL
cytochrome oxidase subunit 1;intron-encoded LAGLIDADG endonuclease #gd NCBI
cytochrome oxidase subunit I #gd NCBI
cytochrome-c oxidase subunit I #gd NCBI
FAMI002Wp #gd NCBI
mitochondrially encoded cytochrome c oxidase I #gd NCBI
putative cytochrome c oxidase, subunit 1 #gd NCBI
putative cytochrome c oxydase, subunit 1 #gd NCBI
gene-AFUA_m0420 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: cytochrome oxidase subunit 1 | type: CDS
gene-cox1 #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-KX657746.1:33527..42029 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgp06 #dx NC_042229.1:40135538 #c gff_gene: cox1
gene-ICI09_mgp05 #dx NC_050344.1:58907346 #c gff_gene: cox1
gene-N4M62_mgp05 #dx NC_066216.1:74863513 #c gff_gene: cox1
gene-Q0045 #dx NC_001224.1:854598 #c gff_gene: COX1

[MIT-CO1-2]
cytochrome c oxidase subunit 1/2 #gd NCBI

[MIT-CO2]
CnACOX2 #gd NCBI
CO2 #gd MANUAL
COX2 #gd MANUAL
cox2 #gd NCBI
Cox2 #gd NCBI
COX2 protein #gd NCBI
Cox2p #gd NCBI
COXII #gd NCBI
cytochrome c oxidase 2 #gd NCBI
Cytochrome c oxidase subunit 2 #gd NCBI
cytochrome c oxidase subunit 2 #gd NCBI
cytochrome c oxidase subunit II #gd NCBI
cytochrome c oxidase subunit II CDS #gd MANUAL
cytochrome coxidase subunit II #gd NCBI
cytochrome oxidase subunit 2 #gd MANUAL
cytochrome oxidase subunit 2 CDS #gd MANUAL
cytochrome oxidase subunit II #gd NCBI
cytochrome-c oxidase subunit 2 #gd NCBI
cytochrome-c oxidase subunit II #gd NCBI
FAMI001Wp #gd NCBI
mitochondrially encoded cytochrome c oxidase II #gd NCBI
putative cytochrome c oxidase, subunit 2 #gd NCBI
putative cytochrome c oxydase, subunit 2 #gd NCBI
gene-AFUA_m0490 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: cytochrome oxidase subunit 2 | type: CDS
gene-cox2 #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-KX657746.1:13835..14590 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgp26 #dx NC_042229.1:40135485 #c gff_gene: cox2
gene-ICI09_mgp14 #dx NC_050344.1:58907349 #c gff_gene: cox2
gene-N4M62_mgp02 #dx NC_066216.1:74863473 #c gff_gene: cox2
gene-Q0250 #dx NC_001224.1:854622 #c gff_gene: COX2

[MIT-CO3]
CnACOX3 #gd NCBI
CO3 #gd NCBI
COX3 #gd MANUAL
cox3 #gd NCBI
Cox3 #gd NCBI
COX3 protein #gd NCBI
Cox3p #gd NCBI
COXIII #gd NCBI
cytochrome c oxidase III #gd NCBI
Cytochrome c oxidase subunit 3 #gd NCBI
cytochrome c oxidase subunit 3 #gd NCBI
Cytochrome c oxidase subunit III #gd NCBI
cytochrome c oxidase subunit III #gd NCBI
cytochrome c oxidase subunit III CDS #gd MANUAL
cytochrome coxidase subunit III #gd NCBI
cytochrome oxidase subunit 3 #gd MANUAL
cytochrome oxidase subunit III #gd NCBI
cytochrome-c oxidase subunit 3 #gd NCBI
cytochrome-c oxidase subunit III #gd NCBI
FAMI003Wp #gd NCBI
mitochondrially encoded cytochrome c oxidase III #gd NCBI
putative cytochrome c oxidase, subunit 3 #gd NCBI
putative cytochrome c oxydase, subunit 3 #gd NCBI
gene-AFUA_m0150 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: cytochrome oxidase subunit 3 | type: CDS
gene-cox3 #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-KX657746.1:19927..20736 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgp12 #dx NC_042229.1:40135527 #c gff_gene: cox3
gene-ICI09_mgp06 #dx NC_050344.1:58907374 #c gff_gene: cox3
gene-N4M62_mgp07 #dx NC_066216.1:74863490 #c gff_gene: cox3
gene-Q0275 #dx NC_001224.1:854627 #c gff_gene: COX3

[MIT-COB]
apocytochrome b #gd NCBI
CnACOB1 #gd NCBI
COB #gd NCBI
cob #gd NCBI
Cob #gd NCBI
COB protein #gd NCBI
Cobp #gd NCBI
CytBp #gd NCBI
cytochrome b/b6 #gd NCBI
FAMI008Wp #gd NCBI
mitochondrially encoded cytochrome b #gd NCBI
putative apocytochrome b #gd NCBI
ubiquinol cytochrome c oxidoreductase apocytochrome b #gd NCBI
ubiquinone:cytochrome c oxidoreductase apocytochrome b #gd NCBI
gene-cob #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-KX657746.1:50911..56402 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgp32 #dx NC_042229.1:40135479 #c gff_gene: cob
gene-ICI09_mgp08 #dx NC_050344.1:58907343 #c gff_gene: cob
gene-N4M62_mgp13 #dx NC_066216.1:74863478 #c gff_gene: cob
gene-Q0105 #dx NC_001224.1:854583 #c gff_gene: COB

[MIT-CYB]
cytb #gd MANUAL
CYTB #gd MANUAL
Cytb #gd NCBI
cytochrome b #gd NCBI
cytochrome b CDS #gd MANUAL
cytochrome-b #gd NCBI
gene-AFUA_m0010 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: cytochrome b | type: CDS

[MIT-DPO]
DNA polymerase #gd NCBI
dpo #gd gff_gene
plasmid related DNA polymerase #gd NCBI
gene-FDY65_mgp16 #dx NC_042229.1:40135495 #c gff_gene: dpo
gene-FDY65_mgp17 #dx NC_042229.1:40135494 #c gff_gene: dpo

[MIT-DPOB]
DNA polymerase B #gd NCBI
DNA polymerase B%2C partial #gd NCBI
DNA polymerase family B #gd NCBI
DNA polymerase type B #gd NCBI
DNA polymerase type B2 #gd NCBI
DNA polymerase type B domain-containing protein #gd NCBI
DNA-directed DNA polymerase #gd NCBI
DpoBap #gd NCBI
DpoBbp #gd NCBI

[MIT-END]
SCEI #gd gff_gene
gene-Q0160 #dx NC_001224.1:854590 #c gff_gene: SCEI

[MIT-MAT]
BI2 #gd NCBI
BI3 #gd NCBI
BI4 #gd NCBI
gene-Q0110 #dx NC_001224.1:854604 #c ncbi_symbol: BI2 | ncbi_desc: cytochrome b mRNA maturase bI2
gene-Q0115 #dx NC_001224.1:854605 #c ncbi_symbol: BI3 | ncbi_desc: cytochrome b mRNA maturase bI3
gene-Q0120 #dx NC_001224.1:854582 #c ncbi_symbol: BI4 | ncbi_desc: intron-encoded RNA maturase bI4

[MIT-NAT2]
N-acetyl-transferase #gd NCBI

[MIT-ND1]
CnANAD1 #gd NCBI
mitochondrially encoded NADH dehydrogenase 1 #gd NCBI
NAD1 #gd NCBI
nad1 #gd NCBI
Nad1 #gd NCBI
Nad1p #gd NCBI
NADH dehydrogenase subunit 1 #gd NCBI
NADH dehydrogenase subunit 1 CDS #gd MANUAL
NADH dehydrogenase, subunit 1 #gd NCBI
NADH-ubiquinone oxidoreductase chain 1 #gd NCBI
NADH-ubiquinone oxidoreductase subunit 1 #gd NCBI
NADH:ubiquinone oxidoreductase subunit 1 #gd NCBI
ND1 #gd MANUAL
ND1 protein #gd NCBI
gene-AFUA_m0040 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: NADH dehydrogenase subunit 1 | type: CDS
gene-FDY65_mgp35 #dx NC_042229.1:40135523 #c gff_gene: nad1
gene-ICI09_mgp01 #dx NC_050344.1:58907377 #c gff_gene: nad1
gene-N4M62_mgp12 #dx NC_066216.1:74863480 #c gff_gene: nad1

[MIT-ND2]
CnANAD2 #gd NCBI
mitochondrially encoded NADH dehydrogenase 2 #gd NCBI
Nad2 #gd NCBI
NAD2 #gd NCBI
nad2 #gd NCBI
Nad2p #gd NCBI
NADH dehydrogenase subunit 2 #gd NCBI
NADH dehydrogenase subunit 2 CDS #gd MANUAL
NADH dehydrogenase, subunit 2 #gd NCBI
NADH-ubiquinone oxidoreductase chain 2 #gd NCBI
NADH-ubiquinone oxidoreductase subunit 2 #gd NCBI
NADH:ubiquinone oxidoreductase subunit 2 #gd NCBI
ND2 #gd MANUAL
ND2 protein #gd NCBI
gene-AFUA_m0530 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: NADH dehydrogenase subunit 2 | type: CDS
gene-FDY65_mgp23 #dx NC_042229.1:40135488 #c gff_gene: nad2
gene-ICI09_mgp10 #dx NC_050344.1:58907370 #c gff_gene: nad2
gene-N4M62_mgp14 #dx NC_066216.1:74863477 #c gff_gene: nad2

[MIT-ND3]
CnANAD3 #gd NCBI
mitochondrially encoded NADH dehydrogenase 3 #gd NCBI
nad3 #gd NCBI
Nad3 #gd NCBI
NAD3 #gd NCBI
Nad3p #gd NCBI
NADH dehydrogenase subunit 3 #gd NCBI
NADH dehydrogenase subunit 3 CDS #gd MANUAL
NADH dehydrogenase, subunit 3 #gd NCBI
NADH-ubiquinone oxidoreductase chain 3 #gd NCBI
NADH-ubiquinone oxidoreductase subunit 3 #gd NCBI
NADH:ubiquinone oxidoreductase subunit 3 #gd NCBI
ND3 #gd MANUAL
ND3 protein #gd NCBI
gene-AFUA_m0480 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: NADH dehydrogenase subunit 3 | type: CDS
gene-FDY65_mgp22 #dx NC_042229.1:40135489 #c gff_gene: nad3
gene-ICI09_mgp09 #dx NC_050344.1:58907342 #c gff_gene: nad3
gene-N4M62_mgp01 #dx NC_066216.1:74863514 #c gff_gene: nad3

[MIT-ND4]
CnANAD4 #gd NCBI
mitochondrially encoded NADH dehydrogenase 4 #gd NCBI
nad4 #gd NCBI
Nad4 #gd NCBI
NAD4 #gd NCBI
Nad4p #gd NCBI
NADH dehydrogenase subunit 4 #gd NCBI
NADH dehydrogenase subunit 4 CDS #gd MANUAL
NADH dehydrogenase, subunit 4 #gd NCBI
NADH-ubiquinone oxidoreductase chain 4 #gd NCBI
NADH-ubiquinone oxidoreductase subunit 4 #gd NCBI
NADH:ubiquinone oxidoreductase chain 4 #gd NCBI
NADH:ubiquinone oxidoreductase subunit 4 #gd NCBI
ND4 #gd MANUAL
ND4 protein #gd NCBI
gene-AFUA_m0060 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: NADH dehydrogenase subunit 4 | type: CDS
gene-FDY65_mgp40 #dx NC_042229.1:40135513 #c gff_gene: nad4
gene-ICI09_mgp13 #dx NC_050344.1:58907351 #c gff_gene: nad4
gene-N4M62_mgp11 #dx NC_066216.1:74863482 #c gff_gene: nad4

[MIT-ND4L]
Nad4L #gd NCBI
Nad4l #gd NCBI
NAD4L #gd NCBI
nad4L #gd NCBI
Nad4Lp #gd NCBI
NADH dehydrogenase 4L #gd NCBI
NADH dehydrogenase subunit 4L #gd NCBI
NADH dehydrogenase subunit 4L CDS #gd MANUAL
NADH dehydrogenase subunit H dehydrogenase subunit 4 #gd NCBI
NADH dehydrogenase, subunit 4L #gd NCBI
NADH-ubiquinone oxidoreductase chain 4L #gd NCBI
NADH-ubiquinone oxidoreductase subunit 4L #gd NCBI
NADH:ubiquinone oxidoreductase subunit 4L #gd NCBI
ND4L #gd MANUAL
ND4L protein #gd NCBI
gene-AFUA_m0510 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: NADH dehydrogenase subunit 4L | type: CDS
gene-FDY65_mgp39 #dx NC_042229.1:40135472 #c gff_gene: nad4L
gene-ICI09_mgp04 #dx NC_050344.1:58907376 #c gff_gene: nad4L
gene-N4M62_mgp16 #dx NC_066216.1:74863475 #c gff_gene: nad4L

[MIT-ND5]
CnANAD5 #gd NCBI
mitochondrially encoded NADH dehydrogenase 5 #gd NCBI
nad5 #gd NCBI
Nad5 #gd NCBI
NAD5 #gd NCBI
Nad5p #gd NCBI
NADH dehydrogenase subunit 5 #gd NCBI
NADH dehydrogenase subunit 5;putative LAGLI-DADG endonuclease #gd NCBI
NADH dehydrogenase subunit H dehydrogenase subunit 5 #gd NCBI
NADH dehydrogenase, subunit 5 #gd NCBI
NADH-ubiquinone oxidoreductase chain 5 #gd NCBI
NADH-ubiquinone oxidoreductase subunit 5 #gd NCBI
NADH:ubiquinone oxidoreductase chain 5 #gd NCBI
NADH:ubiquinone oxidoreductase subunit 5 #gd NCBI
NAHD dehydrogenase subunit 5 #gd NCBI
ND5 #gd NCBI
ND5 protein #gd NCBI
gene-AFUA_m0520 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: NADH dehydrogenase subunit 5 | type: CDS
gene-FDY65_mgp38 #dx NC_042229.1:40135473 #c gff_gene: nad5
gene-ICI09_mgp03 #dx NC_050344.1:58907348 #c gff_gene: nad5
gene-N4M62_mgp15 #dx NC_066216.1:74863476 #c gff_gene: nad5

[MIT-ND6]
CnANAD6 #gd NCBI
mitochondrially encoded NADH dehydrogenase 6 #gd NCBI
NAD6 #gd NCBI
nad6 #gd NCBI
Nad6 #gd NCBI
Nad6p #gd NCBI
NAD(P)H-quinone oxidoreductase subunit 6 #gd NCBI
NADH dehydrogenase subunit 6 #gd NCBI
NADH dehydrogenase, subunit 6 #gd NCBI
NADH-ubiquinone oxidoreductase chain 6 #gd NCBI
NADH-ubiquinone oxidoreductase subunit 6 #gd NCBI
NADH:ubiquinone oxidoreductase chain 6 #gd NCBI
NADH:ubiquinone oxidoreductase subunit 6 #gd NCBI
ND6 #gd MANUAL
ND6 protein #gd NCBI
subunit 6 of NADH dehydrogenase #gd NCBI
gene-AFUA_m0140 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: NADH dehydrogenase subunit 6 | type: CDS
gene-FDY65_mgp19 #dx NC_042229.1:40135492 #c gff_gene: nad6
gene-ICI09_mgp02 #dx NC_050344.1:58907336 #c gff_gene: nad6
gene-N4M62_mgp08 #dx NC_066216.1:74863489 #c gff_gene: nad6

[MIT-RNR1]
12S ribosomal RNA #gd NCBI
12S RNA #gd NCBI
12S rRNA #gd MANUAL
16S small subunit ribosomal RNA #gd NCBI
gene-12S rRNA #gd MANUAL #c maybe encoding problem
mitochondrially encoded 12S RNA #gd NCBI
rns #gd NCBI
rRNA small subunit #gd NCBI
rrnS #gd NCBI
s-rRNA #gd NCBI
small ribosomal RNA #gd NCBI
small ribosomal RNA subunit #gd NCBI
small subunit ribosomal RNA #gd NCBI
ssu #gd MANUAL #c Manual from missing_dbxref_names_raw
gene-AFUA_m0120 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: small subunit ribosomal RNA | type: rRNA
gene-KX657746.1:69794..71405 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-ssu #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0120 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-KX657746.1:69794..71405 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-ssu #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgr01 #dx NC_042229.1:40135501 #c ncbi_desc: small subunit ribosomal RNA
gene-ICI09_mgr01 #dx NC_050344.1:58907359 #c ncbi_desc: small subunit ribosomal RNA
gene-N4M62_mgr02 #dx NC_066216.1:74863487 #c gff_gene: rns
rna-FDY65_mgr01 #dx NC_042229.1:40135501 #c ncbi_desc: small subunit ribosomal RNA
rna-ICI09_mgr01 #dx NC_050344.1:58907359 #c ncbi_desc: small subunit ribosomal RNA
rna-N4M62_mgr02 #dx NC_066216.1:74863487 #c gff_gene: rns

[MIT-RNR2]
16S ribosomal RNA #gd NCBI
16S RNA #gd NCBI
16S rRNA #gd MANUAL
23S large subunit ribosomal RNA #gd NCBI
gene-16S rRNA #gd MANUAL #c maybe encoding problem
l-rRNA #gd NCBI
large ribosomal RNA #gd NCBI
large subunit ribosomal RNA #gd NCBI
lsu #gd MANUAL #c Manual from missing_dbxref_names_raw
mitochondrially encoded 16S RNA #gd NCBI
rnl #gd NCBI
rRNA large subunit #gd NCBI
rrnL #gd NCBI
gene-AFUA_m0250 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: large subunit ribosomal RNA | type: rRNA
gene-KX657746.1:1..3338 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-lsu #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0250 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-KX657746.1:1..3338 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-lsu #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgr02 #dx NC_042229.1:40135507 #c ncbi_desc: large subunit ribosomal RNA
gene-ICI09_mgr02 #dx NC_050344.1:58907350 #c ncbi_desc: large subunit ribosomal RNA
gene-N4M62_mgr01 #dx NC_066216.1:74863499 #c gff_gene: rnl
rna-FDY65_mgr02 #dx NC_042229.1:40135507 #c ncbi_desc: large subunit ribosomal RNA
rna-ICI09_mgr02 #dx NC_050344.1:58907350 #c ncbi_desc: large subunit ribosomal RNA
rna-N4M62_mgr01 #dx NC_066216.1:74863499 #c gff_gene: rnl

[MIT-RNR15]
15S ribosomal RNA #gd NCBI
15S_RRNA #gd gff_gene
gene-Q0020 #dx NC_001224.1:9164990 #c gff_gene: 15S_RRNA
rna-Q0020 #dx NC_001224.1:9164990 #c gff_gene: 15S_RRNA

[MIT-RNR18]
18S ribosomal RNA #gd NCBI

[MIT-RNR21]
21S ribosomal RNA #gd NCBI
21S rRNA #gd NCBI
21S_RRNA #gd gff_gene
gene-Q0158 #dx NC_001224.1:9164988 #c gff_gene: 21S_RRNA
rna-Q0158 #dx NC_001224.1:9164988 #c gff_gene: 21S_RRNA

[MIT-RNR23]
23S ribosomal RNA #gd NCBI

[MIT-RPM1]
ribonuclease P RNA #gd NCBI
RNA subunit of the RNaseP #gd GENEIOUS
RNase P RNA #gd NCBI
rnpB #gd MANUAL #c Manual from missing_dbxref_names_raw
RPM1 #gd gff_gene
rpm1 #gd MANUAL #c Manual from missing_dbxref_names_raw
rpm1 gene #gd GENEIOUS
rpm1 rRNA #gd GENEIOUS
gene-KX657746.1:31383..31807 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-rpm1 #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-rpm1 #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-Q0285 #dx NC_001224.1:9164989 #c gff_gene: RPM1

[MIT-RPO]
DNA-dependent RNA polymerase #gd NCBI
DNA-directed RNA polymerase #gd NCBI
RNA polymerase #gd NCBI
rpo #gd NCBI
gene-FDY65_mgp11 #dx NC_042229.1:40135500 #c gff_gene: rpo
gene-FDY65_mgp20 #dx NC_042229.1:40135491 #c gff_gene: rpo
gene-FDY65_mgp21 #dx NC_042229.1:40135490 #c gff_gene: rpo

[MIT-RPS3]
CnAMRP3 #gd NCBI
putative ribosomal protein S3 #gd NCBI
ribosomal protein 3 #gd NCBI
ribosomal protein S3 #gd NCBI
Ribosomal protein S3%2C mitochondrial #gd NCBI
ribosomal protein S3-like protein #gd NCBI
ribosomal protein subunit 3 #gd NCBI
rps3 #gd NCBI
Rps3 #gd NCBI
RPS3 #gd NCBI
Rps3p #gd NCBI
small ribosomal protein 3 #gd NCBI
small ribosomal protein subunit 3 #gd NCBI
small subunit ribosomal protein 3 #gd NCBI
small subunit ribosomal protein S3 #gd NCBI
gene-KX657746.1:64298..65467 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgp24 #dx NC_042229.1:40135487 #c gff_gene: rps3

[MIT-RPS5]
mitochondrial ribosomal protein S5 #gd NCBI
ribosomal protein S5 #gd NCBI
ribosomal protein S5%2C mitochondrial #gd NCBI
rps5 #gd NCBI
gene-AFUA_m0260 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: ribosomal protein S5 | type: CDS
gene-N4M62_mgp06 #dx NC_066216.1:74863500 #c gff_gene: rps5

[MIT-TA]
trnA #gd NCBI
trnA tRNA #gd MANUAL
trnA(agc) #gd NCBI
trnA(TGC) #gd MANUAL
trnA(tgc) #gd NCBI
tRNA-Ala #gd MANUAL
trnA-TGC #gd gff_gene
trnA-UGC #gd NCBI
gene-AFUA_m0330 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Ala | type: tRNA
gene-AFUA_m0470 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Ala | type: tRNA
gene-KX657746.1:11127..11199 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-tRNA-Ala #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0330 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0470 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-KX657746.1:11127..11199 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-tRNA-Ala #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgt24 #dx NC_042229.1:40135536 #c ncbi_desc: tRNA-Ala
gene-ICI09_mgt02 #dx NC_050344.1:58907338 #c ncbi_desc: tRNA-Ala
gene-N4M62_mgt21 #dx NC_066216.1:74863507 #c gff_gene: trnA-TGC
gene-tA(UGC)Q #dx NC_001224.1:854617 #c ncbi_desc: tRNA-Ala
rna-FDY65_mgt24 #dx NC_042229.1:40135536 #c ncbi_desc: tRNA-Ala
rna-ICI09_mgt02 #dx NC_050344.1:58907338 #c ncbi_desc: tRNA-Ala
rna-N4M62_mgt21 #dx NC_066216.1:74863507 #c gff_gene: trnA-TGC
rna-tA(UGC)Q #dx NC_001224.1:854617 #c ncbi_desc: tRNA-Ala

[MIT-TASX]
tRNA-Asx #gd NCBI

[MIT-TC]
tRNA-Cys #gd MANUAL
trnC #gd NCBI
trnC tRNA #gd MANUAL
trnC(gca) #gd NCBI
trnC(GCA) tRNA #gd MANUAL
trnC-GCA #gd NCBI
gene-AFUA_m0020 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Cys | type: tRNA
gene-KX657746.1:5392..5464 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-tRNA-Cys #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0020 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-KX657746.1:5392..5464 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-tRNA-Cys #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgt19 #dx NC_042229.1:40135531 #c ncbi_desc: tRNA-Cys
gene-ICI09_mgt19 #dx NC_050344.1:58907368 #c ncbi_desc: tRNA-Cys
gene-N4M62_mgt02 #dx NC_066216.1:74863479 #c gff_gene: trnC-GCA
gene-tC(GCA)Q #dx NC_001224.1:854606 #c ncbi_desc: tRNA-Cys
rna-FDY65_mgt19 #dx NC_042229.1:40135531 #c ncbi_desc: tRNA-Cys
rna-ICI09_mgt19 #dx NC_050344.1:58907368 #c ncbi_desc: tRNA-Cys
rna-N4M62_mgt02 #dx NC_066216.1:74863479 #c gff_gene: trnC-GCA
rna-tC(GCA)Q #dx NC_001224.1:854606 #c ncbi_desc: tRNA-Cys

[MIT-TD]
tRNA-Asp #gd MANUAL
tRNA-Asp(GTC) #gd NCBI
trnD #gd NCBI
trnD tRNA #gd MANUAL
trnD(gtc) #gd NCBI
trnD(GTC) tRNA #gd MANUAL
trnD-GTC #gd gff_gene
trnD-GUC #gd NCBI
gene-AFUA_m0190 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Asp | type: tRNA
gene-KX657746.1:9037..9108 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-tRNA-Asp #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0190 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-KX657746.1:9037..9108 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-tRNA-Asp #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgt04 #dx NC_042229.1:40135515 #c ncbi_desc: tRNA-Asp
gene-ICI09_mgt06 #dx NC_050344.1:58907354 #c ncbi_desc: tRNA-Asp
gene-N4M62_mgt10 #dx NC_066216.1:74863494 #c gff_gene: trnD-GTC
gene-tD(GUC)Q #dx NC_001224.1:854614 #c ncbi_desc: tRNA-Asp
rna-FDY65_mgt04 #dx NC_042229.1:40135515 #c ncbi_desc: tRNA-Asp
rna-ICI09_mgt06 #dx NC_050344.1:58907354 #c ncbi_desc: tRNA-Asp
rna-N4M62_mgt10 #dx NC_066216.1:74863494 #c gff_gene: trnD-GTC
rna-tD(GUC)Q #dx NC_001224.1:854614 #c ncbi_desc: tRNA-Asp

[MIT-TE]
tRNA-Glu #gd MANUAL
tRNA-Glu(TTC) #gd NCBI
trnE #gd NCBI
trnE tRNA #gd MANUAL
trnE(ttc) #gd NCBI
trnE(TTC) tRNA #gd MANUAL
trnE-TTC #gd gff_gene
trnE-UUC #gd NCBI
gene-AFUA_m0280 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Glu | type: tRNA
gene-KX657746.1:49884..49955 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-tRNA-Glu #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0280 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-KX657746.1:49884..49955 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-tRNA-Glu #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgt14 #dx NC_042229.1:40135525 #c ncbi_desc: tRNA-Glu
gene-ICI09_mgt17 #dx NC_050344.1:58907366 #c ncbi_desc: tRNA-Glu
gene-N4M62_mgt16 #dx NC_066216.1:74863502 #c gff_gene: trnE-TTC
gene-tE(UUC)Q #dx NC_001224.1:854603 #c ncbi_desc: tRNA-Glu
rna-FDY65_mgt14 #dx NC_042229.1:40135525 #c ncbi_desc: tRNA-Glu
rna-ICI09_mgt17 #dx NC_050344.1:58907366 #c ncbi_desc: tRNA-Glu
rna-N4M62_mgt16 #dx NC_066216.1:74863502 #c gff_gene: trnE-TTC
rna-tE(UUC)Q #dx NC_001224.1:854603 #c ncbi_desc: tRNA-Glu

[MIT-TF]
tRNA-Phe #gd MANUAL
tRNA-Phe(GAA) #gd NCBI
trnF #gd NCBI
trnF(gaa) #gd NCBI
trnF-GAA #gd NCBI
gene-AFUA_m0340 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Phe | type: tRNA
gene-KX657746.1:17753..17824 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-tRNA-Phe #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0340 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-KX657746.1:17753..17824 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-tRNA-Phe #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgt11 #dx NC_042229.1:40135522 #c ncbi_desc: tRNA-Phe
gene-ICI09_mgt23 #dx NC_050344.1:58907372 #c ncbi_desc: tRNA-Phe
gene-N4M62_mgt22 #dx NC_066216.1:74863508 #c gff_gene: trnF-GAA
gene-tF(GAA)Q #dx NC_001224.1:854624 #c ncbi_desc: tRNA-Phe
rna-FDY65_mgt11 #dx NC_042229.1:40135522 #c ncbi_desc: tRNA-Phe
rna-ICI09_mgt23 #dx NC_050344.1:58907372 #c ncbi_desc: tRNA-Phe
rna-N4M62_mgt22 #dx NC_066216.1:74863508 #c gff_gene: trnF-GAA
rna-tF(GAA)Q #dx NC_001224.1:854624 #c ncbi_desc: tRNA-Phe

[MIT-TG]
tRNA- Gly #gd MANUAL
tRNA-Gly #gd MANUAL
tRNA-Gly(TCC) #gd NCBI
trnG #gd NCBI
trnG(acc) #gd NCBI
trnG(tcc) #gd NCBI
trnG-ACC #gd gff_gene
trnG-TCC #gd gff_gene
trnG-UCC #gd NCBI
gene-AFUA_m0170 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Gly | type: tRNA
gene-AFUA_m0180 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Gly | type: tRNA
gene-KX657746.1:7877..7948 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-tRNA-Gly #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0170 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0180 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-KX657746.1:7877..7948 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-tRNA-Gly #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgt08 #dx NC_042229.1:40135519 #c ncbi_desc: tRNA-Gly
gene-ICI09_mgt20 #dx NC_050344.1:58907369 #c ncbi_desc: tRNA-Gly
gene-N4M62_mgt08 #dx NC_066216.1:74863492 #c gff_gene: trnG-ACC
gene-N4M62_mgt09 #dx NC_066216.1:74863493 #c gff_gene: trnG-TCC
gene-tG(UCC)Q #dx NC_001224.1:854613 #c ncbi_desc: tRNA-Gly
rna-FDY65_mgt08 #dx NC_042229.1:40135519 #c ncbi_desc: tRNA-Gly
rna-ICI09_mgt20 #dx NC_050344.1:58907369 #c ncbi_desc: tRNA-Gly
rna-N4M62_mgt08 #dx NC_066216.1:74863492 #c gff_gene: trnG-ACC
rna-N4M62_mgt09 #dx NC_066216.1:74863493 #c gff_gene: trnG-TCC
rna-tG(UCC)Q #dx NC_001224.1:854613 #c ncbi_desc: tRNA-Gly

[MIT-TH]
tRNA-His #gd MANUAL
tRNA-His(GTG) #gd NCBI
trnH #gd NCBI
trnH tRNA #gd MANUAL
trnH(gtg) #gd NCBI
trnH(GTG) tRNA #gd MANUAL
trnH-GTG #gd gff_gene
trnH-GUG #gd NCBI
gene-AFUA_m0410 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-His | type: tRNA
gene-KX657746.1:5503..5573 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-tRNA-His #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0410 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-KX657746.1:5503..5573 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-tRNA-His #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgt22 #dx NC_042229.1:40135534 #c ncbi_desc: tRNA-His
gene-ICI09_mgt14 #dx NC_050344.1:58907363 #c ncbi_desc: tRNA-His
gene-N4M62_mgt26 #dx NC_066216.1:74863512 #c gff_gene: trnH-GTG
gene-tH(GUG)Q #dx NC_001224.1:854607 #c ncbi_desc: tRNA-His
rna-FDY65_mgt22 #dx NC_042229.1:40135534 #c ncbi_desc: tRNA-His
rna-ICI09_mgt14 #dx NC_050344.1:58907363 #c ncbi_desc: tRNA-His
rna-N4M62_mgt26 #dx NC_066216.1:74863512 #c gff_gene: trnH-GTG
rna-tH(GUG)Q #dx NC_001224.1:854607 #c ncbi_desc: tRNA-His

[MIT-TI]
tRNA-Ile #gd MANUAL
tRNA-Ile(GAT) #gd NCBI
trnI #gd NCBI
trnI tRNA #gd MANUAL
trnI(gat) #gd NCBI
trnI-GAT #gd gff_gene
trnI-GAU #gd NCBI
gene-AFUA_m0050 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Ile | type: tRNA
gene-AFUA_m0100 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Ile | type: tRNA
gene-AFUA_m0220 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Ile | type: tRNA
gene-AFUA_m0380 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Ile | type: tRNA
gene-KX657746.1:11325..11397 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-tRNA-Ile #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0050 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0100 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0220 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0380 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-KX657746.1:11325..11397 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-tRNA-Ile #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgt06 #dx NC_042229.1:40135517 #c ncbi_desc: tRNA-Ile
gene-ICI09_mgt11 #dx NC_050344.1:58907360 #c ncbi_desc: tRNA-Ile
gene-N4M62_mgt12 #dx NC_066216.1:74863496 #c gff_gene: trnI-GAT
gene-tI(GAU)Q #dx NC_001224.1:854618 #c ncbi_desc: tRNA-Ile
rna-FDY65_mgt06 #dx NC_042229.1:40135517 #c ncbi_desc: tRNA-Ile
rna-ICI09_mgt11 #dx NC_050344.1:58907360 #c ncbi_desc: tRNA-Ile
rna-N4M62_mgt12 #dx NC_066216.1:74863496 #c gff_gene: trnI-GAT
rna-tI(GAU)Q #dx NC_001224.1:854618 #c ncbi_desc: tRNA-Ile

[MIT-TK]
tRNA-Lys #gd MANUAL
tRNA-Lys(TTT) #gd NCBI
trnK #gd NCBI
trnK tRNA #gd MANUAL
trnK(ctt) #gd NCBI
trnK(ttt) #gd NCBI
trnK(TTT) tRNA #gd MANUAL
trnK-TTT #gd gff_gene
trnK-UUU #gd NCBI
gene-AFUA_m0160 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Lys | type: tRNA
gene-KX657746.1:7294..7365 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-tRNA-Lys #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0160 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-KX657746.1:7294..7365 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-tRNA-Lys #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgt15 #dx NC_042229.1:40135526 #c ncbi_desc: tRNA-Lys
gene-ICI09_mgt24 #dx NC_050344.1:58907373 #c ncbi_desc: tRNA-Lys
gene-N4M62_mgt07 #dx NC_066216.1:74863491 #c gff_gene: trnK-TTT
gene-tK(UUU)Q #dx NC_001224.1:854611 #c ncbi_desc: tRNA-Lys
rna-FDY65_mgt15 #dx NC_042229.1:40135526 #c ncbi_desc: tRNA-Lys
rna-ICI09_mgt24 #dx NC_050344.1:58907373 #c ncbi_desc: tRNA-Lys
rna-N4M62_mgt07 #dx NC_066216.1:74863491 #c gff_gene: trnK-TTT
rna-tK(UUU)Q #dx NC_001224.1:854611 #c ncbi_desc: tRNA-Lys

[MIT-TL1|2]
tRNA-Leu #gd MANUAL
tRNA-Leu(TAA) #gd NCBI
trnL #gd NCBI
trnL(aag) #gd NCBI
trnL(cag) #gd NCBI
trnL(cta) #gd NCBI
trnL(taa) #gd NCBI
trnL(TAA) tRNA #gd MANUAL
trnL(tag) #gd NCBI
trnL-TAA #gd gff_gene
trnL-TAG #gd gff_gene
trnL-UAA #gd NCBI
trnL-UAG #gd NCBI
gene-AFUA_m0320 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Leu | type: tRNA
gene-AFUA_m0350 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Leu | type: tRNA
gene-KX657746.1:6326..6407 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-tRNA-Leu #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-tRNA-Leu-2 #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0320 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0350 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-KX657746.1:6326..6407 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-tRNA-Leu #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-tRNA-Leu-2 #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgt12 #dx NC_042229.1:40135499 #c ncbi_desc: tRNA-Leu
gene-FDY65_mgt17 #dx NC_042229.1:40135529 #c ncbi_desc: tRNA-Leu
gene-ICI09_mgt12 #dx NC_050344.1:58907361 #c ncbi_desc: tRNA-Leu
gene-N4M62_mgt20 #dx NC_066216.1:74863506 #c gff_gene: trnL-TAA
gene-N4M62_mgt23 #dx NC_066216.1:74863509 #c gff_gene: trnL-TAG
gene-tL(UAA)Q #dx NC_001224.1:854609 #c ncbi_desc: tRNA-Leu
rna-FDY65_mgt12 #dx NC_042229.1:40135499 #c ncbi_desc: tRNA-Leu
rna-FDY65_mgt17 #dx NC_042229.1:40135529 #c ncbi_desc: tRNA-Leu
rna-ICI09_mgt12 #dx NC_050344.1:58907361 #c ncbi_desc: tRNA-Leu
rna-N4M62_mgt20 #dx NC_066216.1:74863506 #c gff_gene: trnL-TAA
rna-N4M62_mgt23 #dx NC_066216.1:74863509 #c gff_gene: trnL-TAG
rna-tL(UAA)Q #dx NC_001224.1:854609 #c ncbi_desc: tRNA-Leu

[MIT-TM]
tRNA-Met #gd MANUAL
tRNA-Met(CAT) #gd NCBI
trnfM #gd NCBI
trnM #gd NCBI
trnM(cat) #gd NCBI
trnM-CAT #gd gff_gene
trnM-CAU #gd NCBI
gene-AFUA_m0300 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Met | type: tRNA
gene-AFUA_m0310 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Met | type: tRNA
gene-AFUA_m0370 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Met | type: tRNA
gene-KX657746.1:13018..13091 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-KX657746.1:30593..30665 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-tRNA-Met #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-tRNA-Met-2 #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0300 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0310 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0370 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-KX657746.1:13018..13091 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-KX657746.1:30593..30665 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-tRNA-Met #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-tRNA-Met-2 #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgt20 #dx NC_042229.1:40135506 #c ncbi_desc: tRNA-Met
gene-FDY65_mgt23 #dx NC_042229.1:40135535 #c ncbi_desc: tRNA-Met
gene-ICI09_mgt09 #dx NC_050344.1:58907357 #c ncbi_desc: tRNA-Met
gene-ICI09_mgt10 #dx NC_050344.1:58907358 #c ncbi_desc: tRNA-Met
gene-ICI09_mgt15 #dx NC_050344.1:58907364 #c ncbi_desc: tRNA-Met
gene-N4M62_mgt18 #dx NC_066216.1:74863504 #c gff_gene: trnM-CAT
gene-N4M62_mgt19 #dx NC_066216.1:74863505 #c gff_gene: trnM-CAT
gene-N4M62_mgt25 #dx NC_066216.1:74863511 #c gff_gene: trnM-CAT
gene-tM(CAU)Q1 #dx NC_001224.1:854621 #c ncbi_desc: tRNA-Met
gene-tM(CAU)Q2 #dx NC_001224.1:854628 #c ncbi_desc: tRNA-Met
rna-FDY65_mgt20 #dx NC_042229.1:40135506 #c ncbi_desc: tRNA-Met
rna-FDY65_mgt23 #dx NC_042229.1:40135535 #c ncbi_desc: tRNA-Met
rna-ICI09_mgt09 #dx NC_050344.1:58907357 #c ncbi_desc: tRNA-Met
rna-ICI09_mgt10 #dx NC_050344.1:58907358 #c ncbi_desc: tRNA-Met
rna-ICI09_mgt15 #dx NC_050344.1:58907364 #c ncbi_desc: tRNA-Met
rna-N4M62_mgt18 #dx NC_066216.1:74863504 #c gff_gene: trnM-CAT
rna-N4M62_mgt19 #dx NC_066216.1:74863505 #c gff_gene: trnM-CAT
rna-N4M62_mgt25 #dx NC_066216.1:74863511 #c gff_gene: trnM-CAT
rna-tM(CAU)Q1 #dx NC_001224.1:854621 #c ncbi_desc: tRNA-Met
rna-tM(CAU)Q2 #dx NC_001224.1:854628 #c ncbi_desc: tRNA-Met

[MIT-TN]
gene-tRNA-Asn /product%3D'transfer RNA-Asn #gd MANUAL #c maybe encoding problem
tRNA-Asn #gd MANUAL
tRNA-Asn(GTT) #gd NCBI
trnN #gd NCBI
trnN tRNA #gd MANUAL
trnN(gtt) #gd NCBI
trnN(GTT) tRNA #gd MANUAL
trnN-ATT #gd gff_gene
trnN-GTT #gd gff_gene
trnN-GUU #gd NCBI
gene-AFUA_m0030 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Asn | type: tRNA
gene-AFUA_m0080 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Asn | type: tRNA
gene-KX657746.1:12478..12549 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-tRNA-Asn #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0030 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0080 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-KX657746.1:12478..12549 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-tRNA-Asn #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgt03 #dx NC_042229.1:40135514 #c ncbi_desc: tRNA-Asn
gene-FDY65_mgt13 #dx NC_042229.1:40135524 #c ncbi_desc: tRNA-Asn
gene-ICI09_mgt01 #dx NC_050344.1:58907337 #c ncbi_desc: tRNA-Asn
gene-ICI09_mgt25 #dx NC_050344.1:58907347 #c ncbi_desc: tRNA-Asn
gene-N4M62_mgt03 #dx NC_066216.1:74863481 #c gff_gene: trnN-ATT
gene-N4M62_mgt05 #dx NC_066216.1:74863484 #c gff_gene: trnN-GTT
gene-tN(GUU)Q #dx NC_001224.1:854620 #c ncbi_desc: tRNA-Asn
rna-FDY65_mgt03 #dx NC_042229.1:40135514 #c ncbi_desc: tRNA-Asn
rna-FDY65_mgt13 #dx NC_042229.1:40135524 #c ncbi_desc: tRNA-Asn
rna-ICI09_mgt01 #dx NC_050344.1:58907337 #c ncbi_desc: tRNA-Asn
rna-ICI09_mgt25 #dx NC_050344.1:58907347 #c ncbi_desc: tRNA-Asn
rna-N4M62_mgt03 #dx NC_066216.1:74863481 #c gff_gene: trnN-ATT
rna-N4M62_mgt05 #dx NC_066216.1:74863484 #c gff_gene: trnN-GTT
rna-tN(GUU)Q #dx NC_001224.1:854620 #c ncbi_desc: tRNA-Asn

[MIT-TP]
tRNA-Pro #gd MANUAL
trnP #gd NCBI
trnP tRNA #gd MANUAL
trnP(tgg) #gd NCBI
trnP(TGG) tRNA #gd MANUAL
trnP-TGG #gd gff_gene
trnP-UGG #gd NCBI
gene-AFUA_m0240 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Pro | type: tRNA
gene-KX657746.1:32002..32073 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-tRNA-Pro #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0240 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-KX657746.1:32002..32073 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-tRNA-Pro #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgt02 #dx NC_042229.1:40135476 #c ncbi_desc: tRNA-Pro
gene-ICI09_mgt18 #dx NC_050344.1:58907341 #c ncbi_desc: tRNA-Pro
gene-N4M62_mgt14 #dx NC_066216.1:74863498 #c gff_gene: trnP-TGG
gene-tP(UGG)Q #dx NC_001224.1:854578 #c ncbi_desc: tRNA-Pro
rna-FDY65_mgt02 #dx NC_042229.1:40135476 #c ncbi_desc: tRNA-Pro
rna-ICI09_mgt18 #dx NC_050344.1:58907341 #c ncbi_desc: tRNA-Pro
rna-N4M62_mgt14 #dx NC_066216.1:74863498 #c gff_gene: trnP-TGG
rna-tP(UGG)Q #dx NC_001224.1:854578 #c ncbi_desc: tRNA-Pro

[MIT-TQ]
gene-tRNA-Gln /product%3D'transfer RNA-Gln #gd MANUAL #c maybe encoding problem
tRNA-Gln #gd MANUAL
tRNA-Gln(TTG) #gd NCBI
trnQ #gd NCBI
trnQ(ttg) #gd NCBI
trnQ-TTG #gd gff_gene
trnQ-UUG #gd NCBI
gene-AFUA_m0360 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Gln | type: tRNA
gene-KX657746.1:6429..6501 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-tRNA-Gln #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0360 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-KX657746.1:6429..6501 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-tRNA-Gln #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgt10 #dx NC_042229.1:40135521 #c ncbi_desc: tRNA-Gln
gene-ICI09_mgt05 #dx NC_050344.1:58907353 #c ncbi_desc: tRNA-Gln
gene-N4M62_mgt24 #dx NC_066216.1:74863510 #c gff_gene: trnQ-TTG
gene-tQ(UUG)Q #dx NC_001224.1:854610 #c ncbi_desc: tRNA-Gln
rna-FDY65_mgt10 #dx NC_042229.1:40135521 #c ncbi_desc: tRNA-Gln
rna-ICI09_mgt05 #dx NC_050344.1:58907353 #c ncbi_desc: tRNA-Gln
rna-N4M62_mgt24 #dx NC_066216.1:74863510 #c gff_gene: trnQ-TTG
rna-tQ(UUG)Q #dx NC_001224.1:854610 #c ncbi_desc: tRNA-Gln

[MIT-TR]
tRNA-Arg #gd MANUAL
tRNA-Arg(TCG) #gd NCBI
tRNA-Arg(TCT) #gd NCBI
trnR #gd NCBI
trnR1 #gd NCBI
trnR2 #gd NCBI
trnR(acg) #gd NCBI
trnR(tcg) #gd NCBI
trnR(tct) #gd NCBI
trnR-ACG #gd NCBI
trnR-TCT #gd gff_gene
trnR-UCU #gd NCBI
gene-AFUA_m0070 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Arg | type: tRNA
gene-AFUA_m0500 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Arg | type: tRNA
gene-KX657746.1:7667..7739 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-KX657746.1:10202..10272 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-tRNA-Arg #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-tRNA-Arg-2 #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0070 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0500 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-KX657746.1:7667..7739 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-KX657746.1:10202..10272 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-tRNA-Arg #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-tRNA-Arg-2 #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgt07 #dx NC_042229.1:40135518 #c ncbi_desc: tRNA-Arg
gene-FDY65_mgt18 #dx NC_042229.1:40135530 #c ncbi_desc: tRNA-Arg
gene-ICI09_mgt08 #dx NC_050344.1:58907356 #c ncbi_desc: tRNA-Arg
gene-ICI09_mgt26 #dx NC_050344.1:58907375 #c ncbi_desc: tRNA-Arg
gene-N4M62_mgt01 #dx NC_066216.1:74863474 #c gff_gene: trnR-ACG
gene-N4M62_mgt04 #dx NC_066216.1:74863483 #c gff_gene: trnR-TCT
gene-tR(ACG)Q2 #dx NC_001224.1:854616 #c ncbi_desc: tRNA-Arg
gene-tR(UCU)Q1 #dx NC_001224.1:854612 #c ncbi_desc: tRNA-Arg
rna-FDY65_mgt07 #dx NC_042229.1:40135518 #c ncbi_desc: tRNA-Arg
rna-FDY65_mgt18 #dx NC_042229.1:40135530 #c ncbi_desc: tRNA-Arg
rna-ICI09_mgt08 #dx NC_050344.1:58907356 #c ncbi_desc: tRNA-Arg
rna-ICI09_mgt26 #dx NC_050344.1:58907375 #c ncbi_desc: tRNA-Arg
rna-N4M62_mgt01 #dx NC_066216.1:74863474 #c gff_gene: trnR-ACG
rna-N4M62_mgt04 #dx NC_066216.1:74863483 #c gff_gene: trnR-TCT
rna-tR(ACG)Q2 #dx NC_001224.1:854616 #c ncbi_desc: tRNA-Arg
rna-tR(UCU)Q1 #dx NC_001224.1:854612 #c ncbi_desc: tRNA-Arg

[MIT-TS1|2]
gene-tRNA-Ser /product%3D'transfer RNA-Ser #gd MANUAL #c maybe encoding problem
tRNA-Ser #gd MANUAL
tRNA-Ser(TGA) #gd NCBI
trnS #gd NCBI
trnS1 #gd NCBI
trnS2 #gd NCBI
trnS2 tRNA #gd MANUAL
trnS tRNA #gd MANUAL
trnS(gct) #gd NCBI
trnS(tga) #gd NCBI
trnS(TGA) tRNA #gd MANUAL
trnS(UCN) tRNA #gd MANUAL
trnS-GCT #gd gff_gene
trnS-TGA #gd gff_gene
trnS-UGA #gd NCBI
gene-AFUA_m0200 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Ser | type: tRNA
gene-AFUA_m0230 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Ser | type: tRNA
gene-KX657746.1:10110..10192 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-KX657746.1:62808..62894 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-tRNA-Ser #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-tRNA-Ser-2 #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0200 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0230 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-KX657746.1:10110..10192 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-KX657746.1:62808..62894 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-tRNA-Ser #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-tRNA-Ser-2 #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgt21 #dx NC_042229.1:40135533 #c ncbi_desc: tRNA-Ser
gene-FDY65_mgt25 #dx NC_042229.1:40135537 #c ncbi_desc: tRNA-Ser
gene-ICI09_mgt04 #dx NC_050344.1:58907352 #c ncbi_desc: tRNA-Ser
gene-ICI09_mgt07 #dx NC_050344.1:58907355 #c ncbi_desc: tRNA-Ser
gene-N4M62_mgt11 #dx NC_066216.1:74863495 #c gff_gene: trnS-GCT
gene-N4M62_mgt13 #dx NC_066216.1:74863497 #c gff_gene: trnS-TGA
gene-tS(GCU)Q1 #dx NC_001224.1:854615 #c ncbi_desc: tRNA-Ser
gene-tS(UGA)Q2 #dx NC_001224.1:854585 #c ncbi_desc: tRNA-Ser
rna-FDY65_mgt21 #dx NC_042229.1:40135533 #c ncbi_desc: tRNA-Ser
rna-FDY65_mgt25 #dx NC_042229.1:40135537 #c ncbi_desc: tRNA-Ser
rna-ICI09_mgt04 #dx NC_050344.1:58907352 #c ncbi_desc: tRNA-Ser
rna-ICI09_mgt07 #dx NC_050344.1:58907355 #c ncbi_desc: tRNA-Ser
rna-N4M62_mgt11 #dx NC_066216.1:74863495 #c gff_gene: trnS-GCT
rna-N4M62_mgt13 #dx NC_066216.1:74863497 #c gff_gene: trnS-TGA
rna-tS(GCU)Q1 #dx NC_001224.1:854615 #c ncbi_desc: tRNA-Ser
rna-tS(UGA)Q2 #dx NC_001224.1:854585 #c ncbi_desc: tRNA-Ser

[MIT-TSEC]
trn-Sec gene #gd GENEIOUS
trn-Sec tRNA #gd GENEIOUS
tRNA-Sec #gd NCBI
gene-AFUA_m0210 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Sec | type: tRNA
rna-AFUA_m0210 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature

[MIT-TT]
tRNA-Thr #gd MANUAL
tRNA-Thr(TGT) #gd NCBI
trnT #gd NCBI
trnT1 #gd NCBI
trnT2 #gd NCBI
trnT tRNA #gd MANUAL
trnT(TGT )tRNA #gd MANUAL
trnT(tgt) #gd NCBI
trnT(TGT) tRNA #gd MANUAL
trnT-TGT #gd gff_gene
trnT-UGU #gd NCBI
gene-AFUA_m0270 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Thr | type: tRNA
gene-KX657746.1:4702..4774 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-KX657746.1:18120..18191 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-tRNA-Thr #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0270 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-KX657746.1:4702..4774 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-KX657746.1:18120..18191 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-tRNA-Thr #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgt09 #dx NC_042229.1:40135520 #c ncbi_desc: tRNA-Thr
gene-ICI09_mgt03 #dx NC_050344.1:58907339 #c ncbi_desc: tRNA-Thr
gene-ICI09_mgt16 #dx NC_050344.1:58907365 #c ncbi_desc: tRNA-Thr
gene-N4M62_mgt15 #dx NC_066216.1:74863501 #c gff_gene: trnT-TGT
gene-tT(UAG)Q2 #dx NC_001224.1:854625 #c ncbi_desc: tRNA-Thr
gene-tT(UGU)Q1 #dx NC_001224.1:854591 #c ncbi_desc: tRNA-Thr
rna-FDY65_mgt09 #dx NC_042229.1:40135520 #c ncbi_desc: tRNA-Thr
rna-ICI09_mgt03 #dx NC_050344.1:58907339 #c ncbi_desc: tRNA-Thr
rna-ICI09_mgt16 #dx NC_050344.1:58907365 #c ncbi_desc: tRNA-Thr
rna-N4M62_mgt15 #dx NC_066216.1:74863501 #c gff_gene: trnT-TGT
rna-tT(UAG)Q2 #dx NC_001224.1:854625 #c ncbi_desc: tRNA-Thr
rna-tT(UGU)Q1 #dx NC_001224.1:854591 #c ncbi_desc: tRNA-Thr

[MIT-TV]
tRNA-Val #gd MANUAL
tRNA-Val(TAC) #gd NCBI
trnV #gd NCBI
trnV tRNA #gd MANUAL
trnV(tac) #gd NCBI
trnV-TAC #gd gff_gene
gene-AFUA_m0290 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Val | type: tRNA
gene-KX657746.1:19056..19128 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-tRNA-Val #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0290 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-KX657746.1:19056..19128 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-tRNA-Val #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgt16 #dx NC_042229.1:40135505 #c ncbi_desc: tRNA-Val
gene-ICI09_mgt21 #dx NC_050344.1:58907345 #c ncbi_desc: tRNA-Val
gene-N4M62_mgt17 #dx NC_066216.1:74863503 #c gff_gene: trnV-TAC
gene-tV(UAC)Q #dx NC_001224.1:854626 #c ncbi_desc: tRNA-Val
rna-FDY65_mgt16 #dx NC_042229.1:40135505 #c ncbi_desc: tRNA-Val
rna-ICI09_mgt21 #dx NC_050344.1:58907345 #c ncbi_desc: tRNA-Val
rna-N4M62_mgt17 #dx NC_066216.1:74863503 #c gff_gene: trnV-TAC
rna-tV(UAC)Q #dx NC_001224.1:854626 #c ncbi_desc: tRNA-Val

[MIT-TW]
tRNA-Trp #gd MANUAL
trnW #gd NCBI
trnW tRNA #gd MANUAL
trnW(cca) #gd NCBI
trnW(tca) #gd NCBI
trnW(TCA) tRNA #gd MANUAL
trnW-UCA #gd NCBI
gene-KX657746.1:68113..68183 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-tRNA-Trp #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-KX657746.1:68113..68183 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-tRNA-Trp #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgt05 #dx NC_042229.1:40135516 #c ncbi_desc: tRNA-Trp
gene-ICI09_mgt22 #dx NC_050344.1:58907371 #c ncbi_desc: tRNA-Trp
gene-tW(UCA)Q #dx NC_001224.1:854581 #c ncbi_desc: tRNA-Trp
rna-FDY65_mgt05 #dx NC_042229.1:40135516 #c ncbi_desc: tRNA-Trp
rna-ICI09_mgt22 #dx NC_050344.1:58907371 #c ncbi_desc: tRNA-Trp
rna-tW(UCA)Q #dx NC_001224.1:854581 #c ncbi_desc: tRNA-Trp

[MIT-TXLE]
tRNA-Xle #gd NCBI

[MIT-TY]
tRNA-Tyr #gd MANUAL
trnY #gd NCBI
trnY tRNA #gd MANUAL
trnY(ata) #gd NCBI
trnY(gta) #gd NCBI
trnY(GTA) tRNA #gd MANUAL
trnY-GTA #gd gff_gene
trnY-GUA #gd NCBI
gene-AFUA_m0130 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: tRNA-Tyr | type: tRNA
gene-KX657746.1:11879..11963 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-tRNA-Tyr #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-AFUA_m0130 #gn JQ346808.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-KX657746.1:11879..11963 #gn KX657746.1 #c automated insertion from missing_dbxref_GeneID best feature
rna-tRNA-Tyr #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-FDY65_mgt01 #dx NC_042229.1:40135471 #c ncbi_desc: tRNA-Tyr
gene-ICI09_mgt13 #dx NC_050344.1:58907362 #c ncbi_desc: tRNA-Tyr
gene-N4M62_mgt06 #dx NC_066216.1:74863488 #c gff_gene: trnY-GTA
gene-tY(GUA)Q #dx NC_001224.1:854619 #c ncbi_desc: tRNA-Tyr
rna-FDY65_mgt01 #dx NC_042229.1:40135471 #c ncbi_desc: tRNA-Tyr
rna-ICI09_mgt13 #dx NC_050344.1:58907362 #c ncbi_desc: tRNA-Tyr
rna-N4M62_mgt06 #dx NC_066216.1:74863488 #c gff_gene: trnY-GTA
rna-tY(GUA)Q #dx NC_001224.1:854619 #c ncbi_desc: tRNA-Tyr

[MIT-V-ATPASE]
V-ATPase proteolipid subunit C-like domain #gd NCBI

[MIT-VAR1]
mitochondrial 37S ribosomal protein VAR1 #gd NCBI
mitochondrial ribosomal protein VAR1 #gd NCBI
mitochondrial ribosomal protein VAR1/RPS3 #gd NCBI
mitochondrial ribosomal protein Var1/Rps3 #gd NCBI
putative mitochondrial ribosomal protein VAR1 #gd NCBI
putative ribosomal protein var1 #gd NCBI
ribosomal protein VAR1 #gd NCBI
ribosomal protein VAR1, mitochondrial #gd NCBI
VAR1 #gd gff_gene
var1 #gd MANUAL #c Manual from missing_dbxref_names_raw
VAR1 protein #gd NCBI
var1 ribosomal protein #gd NCBI
gene-var1 #gn HE983611.1 #c automated insertion from missing_dbxref_GeneID best feature
gene-Q0140 #dx NC_001224.1:854586 #c gff_gene: VAR1

[MIT-TEMP-1]
gene-AFUA_m0400 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: hypothetical protein | type: CDS
gene-AFUA_m0440 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: hypothetical protein | type: CDS
gene-AFUA_m0450 #gn JQ346808.1 #c insertion from missing_dbxref_GeneID feature mapping, source: hypothetical protein | type: CDS
gene-KX657746.1:36814..38126 #gn KX657746.1 #c insertion from missing_dbxref_GeneID feature mapping, source: hypothetical protein | type: CDS
gene-KX657746.1:54192..55251 #gn KX657746.1 #c insertion from missing_dbxref_GeneID feature mapping, source: hypothetical protein | type: CDS

[MIT-TEMP-4]
gene-KX657746.1:33769..34810 #gn KX657746.1 #c insertion from missing_dbxref_GeneID feature mapping, source: maturase/DNA endonuclease | type: CDS
gene-KX657746.1:39156..40082 #gn KX657746.1 #c insertion from missing_dbxref_GeneID feature mapping, source: maturase/DNA endonuclease | type: CDS

```

## Version History

- **0.0.2**: Current specification version
- Earlier version was a prototype and not released.