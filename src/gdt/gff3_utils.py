# -*- coding: utf-8 -*-

import pandas as pd  # type: ignore

GFF3_COLUMNS = (
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
QS_GENE = 'type == "gene"'
QS_GENE_TRNA_RRNA = 'type == ["gene", "tRNA", "rRNA"]'


def load_gff3_old(
    filename,
    sep="\t",
    comment="#",
    header=None,
    names=GFF3_COLUMNS,
    usecols=["type", "start", "end", "attributes"],
    query_string="",
):
    if query_string:
        return pd.read_csv(
            filename,
            sep=sep,
            comment=comment,
            header=header,
            names=names,
            usecols=usecols,
        ).query(query_string)

    return pd.read_csv(
        filename, sep=sep, comment=comment, header=header, names=names, usecols=usecols
    )


def filter_orfs_old(gff3_df, orfs_strings=["Name=ORF", "Name=orf"]):
    return gff3_df[
        ~gff3_df["attributes"].str.contains("|".join(orfs_strings))
    ].sort_values(
        by=["start", "end"], ascending=[True, False], ignore_index=True
    )  # type: ignore


def load_gff3(
    filename,
    sep="\t",
    comment="#",
    header=None,
    names=GFF3_COLUMNS,
    usecols=["type", "start", "end", "attributes"],
    query_string="",
):

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
        )  # type: ignore

    return pd.read_csv(
        filename, sep=sep, comment=comment, header=header, names=names, usecols=usecols
    ).sort_values(
        by=["start", "end"], ascending=[True, False], ignore_index=True
    )  # type: ignore


def filter_orfs(gff3_df, orfs_strings=["Name=ORF", "Name=orf"]):
    return gff3_df[
        ~gff3_df["attributes"].str.contains("|".join(orfs_strings))
    ].reset_index(
        drop=True
    )  # type: ignore
