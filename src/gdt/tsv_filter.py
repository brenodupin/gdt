# -*- coding: utf-8 -*-

import re
from typing import Optional
from . import gff3_utils
from . import gene_dict_impl
from . import logger_setup
import pandas as pd
import concurrent.futures
import logging
from pathlib import Path

RE_ID = re.compile(r"ID=([^;]+)")


def process_single_an(
    AN_path: Path,
    gene_dict: dict,
    keep_orfs=False,
    query_string=gff3_utils.QS_GENE_TRNA_RRNA,
) -> dict:
    try:
        AN = AN_path.stem
        df = gff3_utils.load_gff3(AN_path, query_string=query_string)

        if not keep_orfs:  # removing ORFs
            df = gff3_utils.filter_orfs(df)

        df["gene_id"] = df["attributes"].str.extract(RE_ID, expand=False)
        gene_ids = df["gene_id"].values

        in_gene_dict_mask = [g in gene_dict for g in gene_ids]

        # Get dbxref info
        dbxref_mask = df["attributes"].str.contains("Dbxref=", na=False).values

        # check homogeneity in the dbxref_mask
        msg = []
        if len(set(dbxref_mask)) > 1:
            msg.append(f"Dbxref mask is not homogeneous for {AN}")

        status = "good_to_go"
        if not all(in_gene_dict_mask):
            status = (
                "missing_gene_dict_with_dbxref"
                if all(dbxref_mask)
                else "missing_dbxref"
            )

        return {
            "AN": AN,
            "status": status,
            "msg": msg,
            "gene_count": len(df),
            "dbxref_count": sum(dbxref_mask),
            "gene_dict_count": sum(in_gene_dict_mask),
            "genes": gene_ids.tolist(),
            "genes_without_dbxref": gene_ids[~dbxref_mask].tolist(),  # type: ignore
            "genes_not_in_dict": [
                g for g, in_dict in zip(gene_ids, in_gene_dict_mask) if not in_dict
            ],
            "genes_in_dict": [
                g for g, in_dict in zip(gene_ids, in_gene_dict_mask) if in_dict
            ],
        }
    except Exception as e:
        return {"AN": AN, "status": "error", "error": str(e)}


def filter_whole_tsv(
    logger: logger_setup.GDTLogger,
    tsv_path: Path,
    gdt_path: Optional[Path] = None,
    keep_orfs=False,
    workers=0,
    AN_column="AN",
    gff3_suffix=".gff3",
) -> None:
    max_workers = concurrent.futures.ProcessPoolExecutor()._max_workers
    workers = workers if (workers > 0 and workers <= max_workers) else max_workers
    logger.trace(
        f"filter_whole_tsv called | tsv_path: {tsv_path} | gdt_path: {gdt_path}"
        f" | w: {workers} | keep_orfs: {keep_orfs}"
    )

    AN_missing_dbxref = []
    AN_missing_gene_dict = []
    AN_good_to_go = []

    # check if tsv_path exists
    if not tsv_path.exists():
        logger.error(f"tsv file not found: {gdt_path}")
        raise FileNotFoundError(f"tsv file not found: {gdt_path}")
    base_folder = tsv_path.parent
    tsv = pd.read_csv(tsv_path, sep="\t", header=0, dtype=str)

    # check if gdt_path exists, if not, create empty gene_dict
    if gdt_path:
        if not gdt_path.exists():
            logger.error(f"gdt file not found: {gdt_path}")
            raise FileNotFoundError(f"gdt file not found: {gdt_path}")
        gene_dict = gene_dict_impl.create_gene_dict(gdt_path)
        logger.debug(f"Gene dictionary loaded from {gdt_path}")
        logger.trace(f"gene_dict[gdt_header]: {gene_dict['gdt_header']}")
        logger.trace(f"gene_dict[gdt_info]  : {gene_dict['gdt_info']}")

    else:
        gene_dict = {}
        logger.debug("No gdt file provided. Using empty gene_dict.")

    # check if columns 'AN' exists
    if AN_column not in tsv.columns:
        logger.error(f"AN column '{AN_column}' not found in {tsv_path}")
        logger.error(f"Available columns: {tsv.columns}")
        raise ValueError(f"AN column '{AN_column}' not found in {tsv_path}")

    # start processing
    logger.info(f"Processing {len(tsv)} ANs with {workers} workers")
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as executor:
        futures = [
            executor.submit(
                process_single_an,
                base_folder / f"{an}{gff3_suffix}",
                gene_dict,
                keep_orfs,
            )
            for an in tsv[AN_column]
        ]
    concurrent.futures.wait(futures)

    for future in futures:
        result = future.result()
        if result["status"] == "error":
            logger.error(f"Error processing {result['AN']}: {result['error']}")
            continue

        AN = result["AN"]
        logger.trace(f"-- [Processing: {AN}] --")
        logger.trace(
            f"\tgenes: {result['gene_count']} | have dbxref: {result['dbxref_count']} |"
            f" genes in gene_dict: {result['gene_dict_count']}"
        )
        logger.trace(f"\tgenes: {result['genes']}")
        logger.trace(f"\tgenes without dbxref: {result['genes_without_dbxref']}")
        logger.trace(f"\tgenes not in gene_dict: {result['genes_not_in_dict']}")
        logger.trace(f"\tgenes IN gene_dict: {result['genes_in_dict']}")

        if result["status"] == "missing_gene_dict_with_dbxref":
            logger.trace(f"\t{AN} is missing genes in gene_dict but have dbxref")
            AN_missing_gene_dict.append(AN)
        elif result["status"] == "missing_dbxref":
            logger.trace(
                f"\t{AN} is missing genes in gene_dict and is also missing dbxref"
            )
            AN_missing_dbxref.append(AN)
        else:
            logger.trace(f"\t{AN} is good to go!")
            AN_good_to_go.append(AN)
        if result["msg"]:
            logger.trace(f"\tMessages: {result['msg']}")
        logger.trace(f"-- [End Processing: {AN}] --")

    logger.debug(f"ANs missing dbxref: {len(AN_missing_dbxref)}")
    logger.trace(f"ANs missing dbxref: {AN_missing_dbxref}")
    logger.debug(f"ANs missing gene_dict: {len(AN_missing_gene_dict)}")
    logger.trace(f"ANs missing gene_dict: {AN_missing_gene_dict}")
    logger.debug(f"ANs good to go: {len(AN_good_to_go)}")
    logger.trace(f"ANs good to go: {AN_good_to_go}")
    logger.info("Processing finished, creating output files")

    if AN_missing_dbxref:
        with open(base_folder / "AN_missing_dbxref", "w") as f:
            f.write("\n".join(AN_missing_dbxref))
    else:
        logger.debug("No ANs missing dbxref, skipping file creation")
        # check if file exists and remove it
        if (base_folder / "AN_missing_dbxref").exists():
            logger.debug(f"Removing file: {base_folder / 'AN_missing_dbxref'}")
            (base_folder / "AN_missing_dbxref").unlink()

    if AN_missing_gene_dict:
        with open(base_folder / "AN_missing_gene_dict", "w") as f:
            f.write("\n".join(AN_missing_gene_dict))
    else:
        logger.debug("No ANs missing gene_dict, skipping file creation")
        if (base_folder / "AN_missing_gene_dict").exists():
            logger.debug(f"Removing file: {base_folder / 'AN_missing_gene_dict'}")
            (base_folder / "AN_missing_gene_dict").unlink()
