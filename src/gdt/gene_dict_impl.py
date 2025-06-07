# -*- coding: utf-8 -*-

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
import re
from typing import Optional
from pathlib import Path


@dataclass(slots=True)
class Gene:
    label: str
    c: Optional[str]


@dataclass(slots=True)
class GeneDbxref(Gene):
    an_source: str
    dbxref: int


@dataclass(slots=True)
class GeneGeneric(Gene):
    an_sources: list = field(default_factory=list)


@dataclass(slots=True)
class GeneDescription(Gene):
    source: str


def get_gene_dict_info(gene_dict: dict) -> str:
    """Get information about the gene dictionary.
    Args:
        gene_dict (dict): A dictionary containing gene information.
    Returns:
        info (str): A string containing information about the gene dictionary.
    """
    labels, GeneGeneric_count, GeneDescription_count, GeneDbxref_count = set(), 0, 0, 0
    info = gene_dict.pop("gdt_info", None)
    header = gene_dict.pop("gdt_header", None)

    for key in gene_dict:
        labels.add(gene_dict[key].label)
        match gene_dict[key]:
            case GeneDbxref():
                GeneDbxref_count += 1
            case GeneGeneric():
                GeneGeneric_count += 1
            case GeneDescription():
                GeneDescription_count += 1
            case _:
                print(f"[INFO] Unknown type for key {key}: {type(gene_dict[key])}")

    info = []
    info.append(f"Gene dictionary length: {len(gene_dict)}")
    info.append(f"Label: {len(labels)}")
    info.append(f"GeneDescription: {GeneDescription_count}")
    info.append(f"GeneGenerics: {GeneGeneric_count}")
    info.append(f"GeneDbxref: {GeneDbxref_count}")

    if header:
        gene_dict["gdt_header"] = header

    return info


def create_gene_dict(gdt_file: str, max_an_sources: int = 20) -> dict:
    """Create a gene dictionary from a GDT file.
    Args:
        gdt_file (str): Path to the GDT file.
        max_an_sources (int): Maximum number of AN sources to include in GeneGeneric.
                            If set to 0, all sources will be included. Default is 20.
    Returns:
        gene_dict (dict): A dictionary containing gene information.
    """
    gdt_file = Path(gdt_file).resolve()

    if not gdt_file.exists():
        raise FileNotFoundError(f"GDT file not found: {gdt_file}")

    with open(gdt_file, "r") as f:
        lines = [line.strip() for line in f.read().split("\n") if line.strip()]

    if lines[0] != "#! version 0.0.2":
        raise ValueError(
            f"Invalid GDT file version: {lines[0]}. Expected '#! version 0.0.2'"
        )

    result = {}
    header = []
    for line in lines:
        if line.startswith("#!"):
            header.append(line[2:].strip())
            continue
        else:
            break

    current_section = None
    for line in lines:
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1]
            continue

        # Skip if no section is defined
        if not line or not current_section:
            continue

        # Parse gene line
        tag = line.split("#", 1)[0].strip()
        if not tag:
            print(f"Skipping empty tag in line: {line}")
            continue

        if "#c" in line:
            line, comment = line.split("#c", 1)
            comment = comment.strip()
            line = line.strip()
        else:
            comment = None

        if "#dx" in line:  # GeneDX type
            stuff = line.split("#dx", 1)[1].strip()
            an_source = stuff.split(":")[0].strip()
            dbxref = int(stuff.split(":")[1].strip())

            result[tag] = GeneDbxref(
                label=current_section, an_source=an_source, dbxref=dbxref, c=comment
            )

        elif "#gn" in line:  # GeneND type
            an_sources = [s.strip() for s in line.split("#gn", 1)[1].strip().split()]
            an_sources = an_sources if an_sources else []

            if len(an_sources) >= max_an_sources and max_an_sources > 0:
                an_sources = an_sources[:max_an_sources]
                comment = comment if comment else ""
                comment += f" |More than {max_an_sources} sources,"
                f"adding only the first {max_an_sources}|"

            result[tag] = GeneGeneric(
                label=current_section, an_sources=an_sources, c=comment
            )

        elif "#gd" in line:  # GeneDescription type
            source = line.split("#gd", 1)[1].strip()

            result[tag] = GeneDescription(
                label=current_section, source=source, c=comment
            )

    result["gdt_info"] = get_gene_dict_info(result)
    result["gdt_header"] = header
    return result


def _natural_sort_key(s):
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r"(\d+)", s)]


def natural_sort(iterable, key=None, reverse=False):
    """Sort a list in natural order.
    Args:
        iterable (list): A list to sort.
        key (function, optional): Function to extract comparison key from each element.
    Returns:
        list: A sorted list in natural order.
    """
    if not key:  # Original behavior for simple strings
        return sorted(iterable, key=_natural_sort_key, reverse=reverse)

    return sorted(iterable, key=lambda x: _natural_sort_key(key(x)), reverse=reverse)


def write_gdt_file(gd_source: dict, gdt_file: str, overwrite: bool = False) -> None:
    """Write a gene dictionary to a GDT file, sorted by label.
    Args:
        gene_dict (dict): A dictionary containing gene information.
        gdt_file (str): Path to the GDT file.
    """
    gdt_file = Path(gdt_file).resolve()
    if gdt_file.exists() and not overwrite:
        raise FileExistsError(
            f"GDT file already exists: {gdt_file}. Use overwrite=True to overwrite."
        )

    if gd_source["gdt_header"][0] != "version 0.0.2":
        raise ValueError(
            f"GDT not on version 0.0.2. GDT version: {gd_source['gdt_header'][0]}"
        )

    gene_dict = {
        k: v for k, v in gd_source.items() if k not in ["gdt_header", "gdt_info"]
    }
    all_labels = natural_sort({gene.label for gene in gene_dict.values()})

    label_as_key = defaultdict(list)
    for key, value in gene_dict.items():
        label_as_key[value.label].append((key, value))

    all_sorted = {}
    for label, values in label_as_key.items():
        groups = {"gd": [], "gn": [], "dx": []}
        for key, value in values:
            match value:
                case GeneDescription():
                    groups["gd"].append((key, value))
                case GeneGeneric():
                    groups["gn"].append((key, value))
                case GeneDbxref():
                    groups["dx"].append((key, value))

        # Sort each group once
        all_sorted[label] = [
            natural_sort(groups["gd"], key=lambda x: x[0]),
            natural_sort(groups["gn"], key=lambda x: x[0]),
            natural_sort(groups["dx"], key=lambda x: x[0]),
        ]

    with open(gdt_file, "w") as f:
        for line in gd_source["gdt_header"]:
            f.write(f"#! {line}\n")

        for label in all_labels:
            f.write(f"\n[{label}]\n")
            gd, gn, dx = all_sorted[label]

            for key, value in gd:
                f.write(
                    f"{key} #gd {value.source}"
                    f"{' #c ' + value.c if value.c else ''}\n"
                )

            for key, value in gn:
                if value.an_sources:
                    f.write(
                        f"{key} #gn {' '.join(value.an_sources)}"
                        f"{' #c ' + value.c if value.c else ''}\n"
                    )
                else:
                    f.write(f"{key} #gn{' #c ' + value.c if value.c else ''}\n")

            for key, value in dx:
                f.write(
                    f"{key} #dx {value.an_source}:{value.dbxref}"
                    f"{' #c ' + value.c if value.c else ''}\n"
                )


def create_stripped_gdt(
    gdt_file: str, gdt_file_out: str, overwrite: bool = True
) -> None:
    """Create a stripped GDT file from a GDT file.
    Args:
        gdt_file (str): Path to the GDT file.
        gdt_file_out (str): Path to the output GDT file.
    """
    gdt_file = Path(gdt_file).resolve()
    gdt_file_out = Path(gdt_file_out).resolve()

    if not gdt_file.exists():
        raise FileNotFoundError(f"GDT file not found: {gdt_file}")

    if gdt_file_out.exists() and not overwrite:
        raise FileExistsError(
            f"GDT file already exists: {gdt_file_out}. Use overwrite=True to overwrite."
        )

    gene_dict = create_gene_dict(gdt_file)
    header = gene_dict["gdt_header"]
    header.append(
        f"{datetime.now().strftime('%Y-%m-%d %H:%M')}"
        f" - Stripped GDT version from original GDT file {gdt_file.name}"
    )

    # keep only GeneDescription
    gene_dict = {
        key: value
        for key, value in gene_dict.items()
        if isinstance(value, GeneDescription)
    }

    gene_dict["gdt_info"] = get_gene_dict_info(gene_dict)
    gene_dict["gdt_header"] = header
    write_gdt_file(gene_dict, gdt_file_out, overwrite=overwrite)

    print("Info before stripping:")
    [print(x) for x in gene_dict["gdt_info"]]

    print("New Header:")
    [print(x) for x in gene_dict["gdt_header"]]
    print("New Info:")
    [print(x) for x in gene_dict["gdt_info"]]
