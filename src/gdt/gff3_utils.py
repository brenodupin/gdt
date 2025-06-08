# -*- coding: utf-8 -*-

from typing import Optional, Union
from pathlib import Path
import pandas as pd

GFF3_COLUMNS: tuple[str, str, str, str, str, str, str, str, str] = (
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
QS_GENE_TRNA_RRNA = "type == ['gene', 'tRNA', 'rRNA']"


def load_gff3(
    filename: Union[str, Path],
    sep: str = "\t",
    comment: str = "#",
    header: Optional[int] = None,
    names: tuple[str, str, str, str, str, str, str, str, str] = GFF3_COLUMNS,
    usecols: list[str] = ["type", "start", "end", "attributes"],
    query_string: str = "",
) -> pd.DataFrame:
    """
    Load a GFF3 file into a pandas DataFrame, optionally filtering by a query string.
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
    return gff3_df[
        ~gff3_df["attributes"].str.contains("|".join(orfs_strings))
    ].reset_index(drop=True)
