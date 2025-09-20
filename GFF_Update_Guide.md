# GFF Version Update Guide

This guide explains how to update a GeneDict when a new version of a GFF file is released (e.g., AB568599.1 → AB568599.2). The process involves two main steps: removing annotations from the old version and adding annotations from the new version.

As of now, this process is not fully automated, so it requires some manual curation. We are working on improving this in future releases, and will update this guide accordingly. Any suggestions for improvement are welcome!

## Overview

When a new version of a GFF file is released, you need to:
1. **Remove old annotations** using `Auxiliary_processes.ipynb`.
2. **Add new annotations** using the standard GDT creation process.

This ensures the GeneDict stays current without accumulating outdated entries.

## Prerequisites

- Access to both the old GFF file (for reference) and the new GFF file.
- The current GeneDict file that contains annotations from the old version.
- `Auxiliary_processes.ipynb` notebook.
- GDT creation notebooks (`AN_missing_dbxref_GeneID.ipynb` and/or `AN_missing_gene_dict.ipynb`).

## Step 1: Remove Old GFF Annotations

### 1.1 Setup the Removal Process

Open `Auxiliary_processes.ipynb` and navigate to the **"Removal of an GFF's file annotations from a GeneDict"** section.

Configure the variables in section **Setup A** and the logger settings in section **Setup B**.
**Important**: Use the **old GFF file** path here, not the new one.

```python
# Path to the current gdict file
gdict_path = "/path/to/current/gdict/file.gdict"

# Path to the OLD GFF file (the version being replaced)
gff_path = "/path/to/old/version/AB568599.1.gff3"

# Same options used when the gdict was originally created
global_query_string = gdt.QS_GENE_TRNA_RRNA
remove_orfs = True

# Recommended settings for version updates
remove_uniques = True
```

### 1.2 Run the Automated Removal

In the Section **Gathering gene IDs from the GFF file**, execute cells **A** through **D** in sequence. This will:

- Load the current GeneDict.
- Identify all gene IDs from the old GFF file.
- Automatically remove entries that are unique to the old file.
- Create a `keys_to_check.txt` file for manual review.
- Generate a new gdict file with suffix `_removed_uniques.gdict`.

### 1.3 Manual Curation

Review the generated `keys_to_check.txt` file and create a `keys_to_remove.txt` file following these guidelines:

**Remove (file-specific entries):**
- Keys containing the old sequence ID: `rna-AB568599.1:5348..5420`.
- Keys with unique identifiers: `gene-A8G35_gp044`, `gene-A8V06_gp062`.

**Keep (standard nomenclature):**
- Standard gene/trna/rrna names: `gene-nad2`, `gene-TRNA-Trp`, `gene-rrn18`.
- Universal identifiers that might be shared across files.

### 1.4 Finalize Removal

Execute the cells in the **"Keys to remove from GeneDict"** section to:
- Process the `keys_to_remove.txt` file.
- Remove the specified entries from the GeneDict.
- Generate the final cleaned gdict file with suffix `_removed_manual.gdict`.

## Step 2: Add New GFF Annotations

### 2.1 Prepare the New GFF File

Ensure your new GFF file (e.g., `AB568599.2.gff3`) is in the correct location and accessible;
don't forget to update the TSV as well.

Change the suffix of the GDICT `<>_removed_manual.gdict` to either `<>_stripped.gdict` or `<>_pilot_##.gdict` (## is a number),
as the GDT process needs these suffixes to run properly.

### 2.2 Run Standard GDT Process

Run the process again in your dataset (with the new GFF file) in the same way you would create a new GeneDict.

Since all the other GFF files remained unchanged (and therefore their annotations are already in the GDICT), only the new GFF annotations will contribute to an updated GeneDict, you may not even need to run the whole process. [See the GDT creation guide for details](README.md#creation-process).