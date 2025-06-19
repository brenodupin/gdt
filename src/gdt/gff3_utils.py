# -*- coding: utf-8 -*-
"""Utilities for working with GFF3 files in the GDT package."""

import concurrent.futures
import os
import re
import shutil
from pathlib import Path
from typing import Final, Optional, Union, cast

import pandas as pd

from . import gdt_impl, logger_setup

GFF3_COLUMNS: tuple[str, ...] = (
    "seqid",
    "source",
    "type",
    "start",
    "end",
    "score",
    "strand",
    "phase",
    "attributes",
)
QS_GENE = "type == 'gene'"
QS_GENE_TRNA_RRNA = "type in ('gene', 'tRNA', 'rRNA')"

RE_ID = re.compile(r"ID=([^;]+)")
RE_dbxref_GeneID = re.compile(r"Dbxref=.*GeneID:")


def load_gff3(
    filename: Union[str, Path],
    sep: str = "\t",
    comment: str = "#",
    header: Optional[int] = None,
    names: tuple[str, ...] = GFF3_COLUMNS,
    usecols: list[str] = ["type", "start", "end", "attributes"],
    query_string: Optional[str] = None,
) -> pd.DataFrame:
    """Load a GFF3 file into a pandas DataFrame, optionally filtering by a query string.

    Args:
        filename (str): Path to the GFF3 file.
        sep (str): Separator used in the file.
        comment (str): Comment character in the file.
        header (int or None): Row number to use as the column names, None if no header.
        names (list): List of column names to use.
        usecols (list): List of columns to read from the file.
        query_string (str): Query string to filter the DataFrame.

    Returns:
        pd.DataFrame: DataFrame containing the filtered GFF3 data.

    """
    if query_string:
        return (
            pd.read_csv(
                filename,
                sep=sep,
                comment=comment,
                header=header,
                names=names,
                usecols=usecols,
            )
            .query(query_string)
            .sort_values(
                by=["start", "end"], ascending=[True, False], ignore_index=True
            )
        )

    return pd.read_csv(
        filename, sep=sep, comment=comment, header=header, names=names, usecols=usecols
    ).sort_values(by=["start", "end"], ascending=[True, False], ignore_index=True)


def filter_orfs(
    gff3_df: pd.DataFrame, orfs_strings: list[str] = ["Name=ORF", "Name=orf"]
) -> pd.DataFrame:
    """Filter out ORFs from a GFF3 DataFrame.

    Args:
        gff3_df (pd.DataFrame): DataFrame containing GFF3 data.
        orfs_strings (list): List of strings to identify ORFs.

    Returns:
        pd.DataFrame: DataFrame with ORFs removed.

    """
    return gff3_df[
        ~gff3_df["attributes"].str.contains("|".join(orfs_strings))
    ].reset_index(drop=True)


def check_single_an(
    an_path: Path,
    gene_dict: gdt_impl.GeneDict,
    keep_orfs: bool = False,
    query_string: str = QS_GENE_TRNA_RRNA,
) -> dict[str, Union[str, int, list[str]]]:
    """Check a single GFF3 file for gene information and dbxref.

    Args:
        an_path (Path): Path to the GFF3 file.
        gene_dict (GeneDict): Gene dictionary to check against.
        keep_orfs (bool): Whether to keep ORFs in the DataFrame.
        query_string (str): Query string to filter the DataFrame.

    Returns:
        dict: Dictionary containing the results of the check.

    """
    try:
        an: str = an_path.stem
        df = load_gff3(an_path, query_string=query_string)

        if not keep_orfs:  # removing ORFs
            df = filter_orfs(df)

        df["gene_id"] = df["attributes"].str.extract(RE_ID, expand=False)  # type: ignore[call-overload]
        gene_ids = df["gene_id"].values

        in_gene_dict_mask = [g in gene_dict for g in gene_ids]

        # Get dbxref info
        dbxref_mask = df["attributes"].str.contains(RE_dbxref_GeneID, na=False)

        status = "good_to_go"
        if not all(in_gene_dict_mask):
            status = "M_in_gene_dict" if all(dbxref_mask) else "M_dbxref_GeneID"

        return {
            "AN": an,
            "status": status,
            "gene_count": len(df),
            "dbxref_count": sum(dbxref_mask),
            "gene_dict_count": sum(in_gene_dict_mask),
            "genes": gene_ids.tolist(),
            "genes_without_dbxref": df[~dbxref_mask]["gene_id"].tolist(),
            "genes_with_dbxref": df[dbxref_mask]["gene_id"].tolist(),
            "genes_not_in_dict": [
                g for g, in_dict in zip(gene_ids, in_gene_dict_mask) if not in_dict
            ],
            "genes_in_dict": [
                g for g, in_dict in zip(gene_ids, in_gene_dict_mask) if in_dict
            ],
        }
    except Exception as e:
        return {"AN": an, "status": "error", "error": str(e)}


def check_column(
    log: logger_setup.GDTLogger,
    df: pd.DataFrame,
    col: str,
    df_txt: str = "TSV",
) -> None:
    """Check if a specific column exists in the DataFrame.

    Args:
        log (GDTLogger): Logger instance for logging messages.
        df (pd.DataFrame): DataFrame to check.
        col (str): Column name to check for.
        df_txt (str): Text representation of the DataFrame type for error messages.

    """
    log.trace(f"check_column called | col: {col} | df_txt: {df_txt}")
    if col not in df.columns:
        log.error(f"Column '{col}' not found in DataFrame")
        log.error(f"Available columns: {df.columns}")
        raise ValueError(
            f"Column '{col}' not found in {df_txt}. Please check the file."
        )


def check_gff_in_tsv(
    log: logger_setup.GDTLogger,
    df: pd.DataFrame,
    base_path: Path,
    gff_suffix: str = ".gff3",
    an_column: str = "AN",
) -> None:
    """Check if GFF3 files exist for each accession number in the DataFrame.

    Args:
        log (GDTLogger): Logger instance for logging messages.
        df (pd.DataFrame): DataFrame containing accession numbers.
        base_path (Path): Base path where GFF3 files are expected to be found.
        gff_suffix (str): Suffix for GFF3 files. Default is ".gff3".
        an_column (str): Column name containing accession numbers. Default is "AN".

    """
    log.trace(
        f"check_gff_in_tsv called | base_path: {base_path} | gff_suffix: {gff_suffix}"
    )
    check_column(log, df, an_column, "TSV")

    no_files = [
        (an, AN_path)
        for an in df[an_column]
        if not (AN_path := (base_path / f"{an}{gff_suffix}")).is_file()
    ]

    if no_files:
        for an, path in no_files:
            log.error(f"GFF3 file not found for {an}, expected {path}")
        raise FileNotFoundError(
            f"Missing {len(no_files)} GFF3 files. Please check the log for details."
        )


def filter_whole_tsv(
    log: logger_setup.GDTLogger,
    tsv_path: Path,
    gdt_path: Optional[Path] = None,
    keep_orfs: bool = False,
    workers: int = 0,
    an_column: str = "AN",
    gff_suffix: str = ".gff3",
    query_string: str = QS_GENE_TRNA_RRNA,
) -> None:
    """Filter a whole TSV containing GFF3 files and check them against a GeneDict.

    Args:
        log (GDTLogger): Logger instance for logging messages.
        tsv_path (Path): Path to the TSV file containing accession numbers.
        gdt_path (Optional[Path]): Path to the GDT file.
                                   If None, an empty GeneDict is used.
        keep_orfs (bool): Whether to keep ORFs in the GFF3 files. Default is False.
        workers (int): Number of worker processes to use for parallel processing.
                       Default is 0, meaing max cpu cores.
        an_column (str): Column name containing accession numbers in the TSV file.
                         Default is "AN".
        gff_suffix (str): Suffix for GFF3 files. Default is ".gff3".
        query_string (str): Query string to filter GFF3 files.
                            Default is QS_GENE_TRNA_RRNA.


    """
    max_workers = os.cpu_count() or 1
    workers = workers if (workers > 0 and workers <= max_workers) else max_workers

    an_missing_dbxref_geneid: list[str] = []
    an_missing_gene_dict: list[str] = []
    an_good_to_go: list[str] = []

    # check if tsv_path exists
    if not tsv_path.exists():
        log.error(f"tsv file not found: {gdt_path}")
        raise FileNotFoundError(f"tsv file not found: {gdt_path}")

    base_folder: Final[Path] = tsv_path.parent
    tsv = pd.read_csv(tsv_path, sep="\t")
    check_column(log, tsv, an_column)
    check_gff_in_tsv(log, tsv, base_folder, gff_suffix, an_column)

    MISC_DIR: Final[Path] = base_folder / "misc"  # noqa: N806
    GDT_DIR: Final[Path] = MISC_DIR / "gdt"  # noqa: N806
    GDT_DIR.mkdir(511, True, True)  # 511 = 0o777

    # check if gdt_path exists, if not, create empty gene_dict
    if gdt_path:
        if not gdt_path.exists():
            log.error(f"gdt file not found: {gdt_path}")
            raise FileNotFoundError(f"gdt file not found: {gdt_path}")

        # check if gdt file is in GDT_DIR
        if gdt_path.parent != GDT_DIR:
            gdt_path = shutil.move(gdt_path, GDT_DIR / gdt_path.name)
            log.info(f"Moving gdt file to {gdt_path}")

        gene_dict = gdt_impl.read_gdt(gdt_path)
        log.debug(f"GeneDict loaded from {gdt_path}")
        log.trace(f"Header : {gene_dict.header}")
        log.trace(f"Info   : {gene_dict.info}")

    else:
        gene_dict = gdt_impl.GeneDict()
        log.debug("No gdt file provided. Using empty gene_dict.")

    # start processing
    log.info(f"Processing {len(tsv)} ANs with {workers} workers")
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(
                check_single_an,
                base_folder / f"{an}{gff_suffix}",
                gene_dict,
                keep_orfs,
                query_string,
            )
            for an in tsv[an_column]
        ]
    concurrent.futures.wait(futures)

    for future in futures:
        result = future.result()
        if result["status"] == "error":
            log.error(f"Error processing {result['AN']}: {result['error']}")
            continue

        an: str = cast(str, result["AN"])
        log.trace(f"-- [Processing: {an}] --")
        log.trace(
            f"\tgenes: {result['gene_count']} | have dbxref: {result['dbxref_count']} |"
            f" genes in gene_dict: {result['gene_dict_count']}"
        )
        log.trace(f"\tgenes: {result['genes']}")
        log.trace(f"\twith dbxref : {result['genes_with_dbxref']}")
        log.trace(f"\tin gene_dict : {result['genes_in_dict']}")
        log.trace(f"\twithout dbxref : {result['genes_without_dbxref']}")
        log.trace(f"\tnot in gene_dict: {result['genes_not_in_dict']}")

        if result["status"] == "M_in_gene_dict":
            log.trace(f"\t{an} is missing genes in gene_dict but have dbxref")
            an_missing_gene_dict.append(an)

        elif result["status"] == "M_dbxref_GeneID":
            log.trace(
                f"\t{an} is missing genes in gene_dict and is also missing dbxref"
            )
            an_missing_dbxref_geneid.append(an)

        else:
            log.trace(f"\t{an} is good to go!")
            an_good_to_go.append(an)

        log.trace(f"-- [End Processing: {an}] --")

    log.info(f"ANs good to go: {len(an_good_to_go)}")
    log.trace(f"ANs good to go: {an_good_to_go}")
    log.info(f"ANs missing gene_dict: {len(an_missing_gene_dict)}")
    log.trace(f"ANs missing gene_dict: {an_missing_gene_dict}")
    log.info(f"ANs missing dbxref: {len(an_missing_dbxref_geneid)}")
    log.trace(f"ANs missing dbxref: {an_missing_dbxref_geneid}")
    log.info("Processing finished, resolving output files")

    path_gene_dict = MISC_DIR / "AN_missing_gene_dict.txt"
    path_dbxref = MISC_DIR / "AN_missing_dbxref_GeneID.txt"

    if an_missing_dbxref_geneid:
        with open(path_dbxref, "w") as f:
            f.write("\n".join(an_missing_dbxref_geneid))

    else:
        log.debug("No ANs missing dbxref GeneID, skipping file creation")
        # check if file exists and remove it
        if path_dbxref.exists():
            log.debug(f"Removing file: {path_dbxref}")
            path_dbxref.unlink()

    if an_missing_gene_dict:
        with open(path_gene_dict, "w") as f:
            f.write("\n".join(an_missing_gene_dict))

    else:
        log.debug("No ANs missing gene_dict, skipping file creation")
        if path_gene_dict.exists():
            log.debug(f"Removing file: {path_gene_dict}")
            path_gene_dict.unlink()


def standardize_tsv(
    log: logger_setup.GDTLogger,
    tsv_path: Path,
    gdt_path: Path,
    an_colum: str,
    gff_suffix: str,
    query_string: str,
    check_flag: bool,
    second_place: bool,
    gdt_tag: str,
    error_on_missing: bool,
    save_copy: bool,
) -> None:
    """Standardize GFF3 files listed in a TSV based on a GeneDict.

    Args:
        log (GDTLogger): Logger instance for logging messages.
        tsv_path (Path): Path to the TSV file containing accession numbers.
        gdt_path (Path): Path to the GDT file.
        an_colum (str): Column name containing accession numbers in the TSV file.
        gff_suffix (str): Suffix for GFF3 files.
        query_string (str): Query string to filter GFF3 files.
        check_flag (bool): If True, do not save changes to GFF3 files.
        second_place (bool): If True, add gdt_tag to the second place in attributes gff.
        gdt_tag (str): Tag to use for gdt_tag in GFF3 attributes.
        error_on_missing (bool): If True, raise an ValueError
                                 if a gene ID is not in the GeneDict.
        save_copy (bool): If True, save a copy of the original GFF3 file.

    """
    if not tsv_path.exists():
        log.error(f"tsv file not found: {tsv_path}")
        raise FileNotFoundError(f"tsv file not found: {tsv_path}")

    if not gdt_path.exists():
        log.error(f"gdt file not found: {gdt_path}")
        raise FileNotFoundError(f"gdt file not found: {gdt_path}")

    gene_dict = gdt_impl.read_gdt(gdt_path)
    log.debug(f"Gene dictionary loaded from {gdt_path}")

    tsv = pd.read_csv(tsv_path, sep="\t")
    check_column(log, tsv, an_colum)
    check_gff_in_tsv(log, tsv, tsv_path.parent, gff_suffix, an_colum)

    for an in tsv[an_colum]:
        gff_path = tsv_path.parent / f"{an}{gff_suffix}"
        standardize_gff3(
            log,
            gff_path,
            gene_dict,
            query_string,
            check_flag,
            second_place,
            gdt_tag,
            error_on_missing,
            save_copy,
        )

    if check_flag:
        log.info(f"Not saving new gff, check flag set to {check_flag}")


def standardize_gff3(
    log: logger_setup.GDTLogger,
    gff_path: Path,
    gene_dict: gdt_impl.GeneDict,
    query_string: str,
    check_flag: bool,
    second_place: bool,
    gdt_tag: str,
    error_on_missing: bool,
    save_copy: bool,
    single_run: bool = False,
) -> None:
    """Standardize a GFF3 file by adding a gdt_tag to the attributes column.

    Args:
        log (GDTLogger): Logger instance for logging messages.
        gff_path (Path): Path to the GFF3 file.
        gene_dict (gdt_impl.GeneDict): GeneDict to check against.
        query_string (str): Query string to filter GFF3 features.
        check_flag (bool): If True, do not save changes to the GFF3 file.
        second_place (bool): If True, add gdt_tag to the second place in attributes gff.
        gdt_tag (str): Tag to use for the gdt_tag in GFF3 attributes.
        error_on_missing (bool): If True, raise an ValueError
                                 if a gene ID is not in the GeneDict.
        save_copy (bool): If True, save a copy of the original GFF3 file.
        single_run (bool): If True, check if the GFF3 file exists before processing.
                           Default is False, because in bulk processing,
                           the check should be done in the calling function.

    """
    if single_run and not gff_path.exists():
        log.error(f"GFF3 file not found: {gff_path}")
        raise FileNotFoundError(f"GFF3 file not found: {gff_path}")

    with open(gff_path, "r") as f:
        lines = f.readlines()

    headers, index = [], 0
    while lines[index].startswith("#"):
        headers.append(lines[index].strip())
        index += 1

    contents = []
    series_holder = pd.Series([""], dtype="string")

    for text in lines[index:]:
        if not (text := text.strip()):
            continue
        line = text.split("\t")
        joined_line = "\t".join(line)

        # line[2] is type line, line[8] is attributes
        series_holder[0] = line[2]
        if pd.eval(query_string, local_dict={"type": series_holder})[0]:  # type: ignore[index]
            gene_id = m.group(1) if (m := RE_ID.search(line[8])) else None
            if gene_id:
                gdt_label = gene_dict.get(gene_id, None)

                if not gdt_label:
                    log.error(f"Gene ID {gene_id} not found in gene_dict.")

                    if error_on_missing:
                        raise ValueError(f"Gene ID {gene_id} not found in gene_dict.")

                    contents.append("\t".join(line))
                    continue

                gdt_str = f"{gdt_tag}={gdt_label.label}"

                if gdt_str in line[8]:
                    log.trace(
                        f"Skipping {gdt_str} in {gff_path.name}. Already present."
                    )
                    contents.append("\t".join(line))
                    continue

                if f"{gdt_tag}=" in line[8]:
                    log.debug(f"Removing existing {gdt_tag} tag in {gff_path.name}.")
                    line[8] = re.sub(rf"{gdt_tag}=[^;]*;?", "", line[8])
                    line[8] = line[8][:-1] if line[8].endswith(";") else line[8]

                if second_place:
                    left, right = line[8].split(";", 1)
                    line[8] = (
                        f"{left};{gdt_str};{right}" if right else f"{left};{gdt_str}"
                    )

                else:
                    line[8] = (
                        f"{line[8]}{'' if line[8].endswith(';') else ';'}"
                        f"{gdt_tag}={gdt_label.label}"
                    )
            else:
                _handle_missing_gene_id(
                    log, gff_path, query_string, joined_line, error_on_missing
                )

        contents.append("\t".join(line))

    if not check_flag:
        log.info(f"Standardizing {gff_path.name} by adding: {gdt_tag}")
        if save_copy:
            backup_path = gff_path.with_suffix(".original")
            shutil.copy(gff_path, backup_path)
            log.info(f"Backup created at {backup_path}")

        with open(gff_path, "w") as f:
            f.write("\n".join(headers))
            f.write("\n")
            f.write("\n".join(contents))
            f.write("\n\n")

    elif single_run:
        log.info(f"Not saving new gff, check flag set to {check_flag}")


def _handle_missing_gene_id(
    log: logger_setup.GDTLogger,
    gff_path: Path,
    query_string: str,
    joined_line: str,
    error_on_missing: bool = False,
) -> None:
    """Handle case where gene_id is not found."""
    log.error(
        f"ID not found in {gff_path.name}. This is not supposed to happen, "
        f"and could be a problem with query_string ({query_string}). "
        f"Feature att: {joined_line}"
    )
    if error_on_missing:
        raise ValueError(f"ID not found in {gff_path.name}. att: {joined_line}")
