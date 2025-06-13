# -*- coding: utf-8 -*-

import re

from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from collections import UserDict, defaultdict
from typing import Callable, Iterable, TypeVar, Union, Optional


@dataclass(slots=True)
class Gene:
    label: str
    c: Optional[str]


@dataclass(slots=True)
class DbxrefGeneID(Gene):
    an_source: str
    GeneID: int


@dataclass(slots=True)
class GeneGeneric(Gene):
    an_sources: list[str] = field(default_factory=list)


@dataclass(slots=True)
class GeneDescription(Gene):
    source: str


GeneUnion = Union[GeneDescription, GeneGeneric, DbxrefGeneID]


class GeneDict(UserDict[str, GeneUnion]):
    def __init__(
        self,
        initial: Optional[dict[str, GeneUnion]] = None,
        *,
        version: str = "0.0.2",
        header: Optional[list[str]] = None,
        info: Optional[list[str]] = None,
    ):
        super().__init__(initial or {})
        self.version = version
        self.header = header if header is not None else []
        self.info = info if info is not None else []


T = TypeVar("T")
G = TypeVar("G", bound=Gene)

geneTuple = tuple[str, GeneUnion]
geneList = list[tuple[str, G]]

gdList = geneList[GeneDescription]
gnList = geneList[GeneGeneric]
dxList = geneList[DbxrefGeneID]

SortedGeneGroups = tuple[gdList, gnList, dxList]


def get_gene_dict_info(gene_dict: GeneDict) -> list[str]:
    """Get information about the gene dictionary.
    Args:
        gene_dict (dict): A dictionary containing gene information.
    Returns:
        info (str): A string containing information about the gene dictionary.
    """
    labels = set()
    gd_int = 0
    gn_int = 0
    dx_int = 0

    for key in gene_dict:
        labels.add(gene_dict[key].label)
        match gene_dict[key]:
            case DbxrefGeneID():
                dx_int += 1
            case GeneGeneric():
                gn_int += 1
            case GeneDescription():
                gd_int += 1
            case _:
                print(f"[INFO] Unknown type for key {key}: {type(gene_dict[key])}")

    info: list[str] = []
    info.append(f"Gene dictionary length: {len(gene_dict)}")
    info.append(f"Label: {len(labels)}")
    info.append(f"GeneDescriptions: {gd_int}")
    info.append(f"GeneGenerics    : {gn_int}")
    info.append(f"DbxrefGeneIDs   : {dx_int}")

    return info


def create_gene_dict(gdt_file: Union[str, Path], max_an_sources: int = 20) -> GeneDict:
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

    result = GeneDict()
    for line in lines:
        if line.startswith("#!"):
            result.header.append(line[2:].strip())
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

        if "#dx" in line:  # DbxrefGeneID dx
            stuff = line.split("#dx", 1)[1].strip()
            an_source = stuff.split(":")[0].strip()
            GeneID = int(stuff.split(":")[1].strip())

            result[tag] = DbxrefGeneID(
                label=current_section, an_source=an_source, GeneID=GeneID, c=comment
            )

        elif "#gn" in line:  # GeneGeneric gn
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

        elif "#gd" in line:  # GeneDescription gd
            source = line.split("#gd", 1)[1].strip()

            result[tag] = GeneDescription(
                label=current_section, source=source, c=comment
            )

    # Not the best use of cast, but it works
    result.info = get_gene_dict_info(result)
    return result


def _natural_sort_key(s: str) -> list[Union[int, str]]:
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r"(\d+)", s)]


def natural_sort(
    iterable: Iterable[T], key: Callable[[T], str] | None = None, reverse: bool = False
) -> list[T]:
    """Sort a list in natural order.
    Args:
        iterable: An iterable to sort.
        key: Function to extract comparison key from each element.
        reverse: Whether to sort in reverse order.
    Returns:
        A sorted list in natural order.
    """
    if key is None:  # Original behavior for simple strings
        # Type narrowing: if key is None, T must be str
        return sorted(iterable, key=_natural_sort_key, reverse=reverse)  # type: ignore[arg-type]

    return sorted(iterable, key=lambda x: _natural_sort_key(key(x)), reverse=reverse)


def write_gdt_file(
    gene_dict: GeneDict, gdt_file: Union[str, Path], overwrite: bool = False
) -> None:
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

    if gene_dict.version != "0.0.2":
        raise ValueError(f"GDT not on version 0.0.2. GDT version: {gene_dict.version}")

    all_labels: list[str] = natural_sort({gene.label for gene in gene_dict.values()})

    label_as_key = defaultdict(list)
    for key, value in gene_dict.items():
        label_as_key[value.label].append((key, value))

    all_sorted: dict[str, SortedGeneGroups] = {}
    for label, values in label_as_key.items():
        gd: gdList = []
        gn: gnList = []
        dx: dxList = []
        for key, value in values:
            match value:
                case GeneDescription():
                    gd.append((key, value))
                case GeneGeneric():
                    gn.append((key, value))
                case DbxrefGeneID():
                    dx.append((key, value))

        # Sort each group once
        all_sorted[label] = (
            natural_sort(gd, key=lambda x: x[0]),
            natural_sort(gn, key=lambda x: x[0]),
            natural_sort(dx, key=lambda x: x[0]),
        )

    with open(gdt_file, "w") as f:
        for line in gene_dict.header:
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
                    f"{key} #dx {value.an_source}:{value.GeneID}"
                    f"{' #c ' + value.c if value.c else ''}\n"
                )


def create_stripped_gdt(
    gdt_file: Union[Path, str], gdt_file_out: Union[Path, str], overwrite: bool = True
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
    header = gene_dict.header
    header.append(
        f"{datetime.now().strftime('%Y-%m-%d %H:%M')}"
        f" - Stripped GDT version from original GDT file {gdt_file.name}"
    )

    # keep only GeneDescription
    stripped = GeneDict()
    stripped.data = {
        key: value
        for key, value in gene_dict.items()
        if isinstance(value, GeneDescription)
    }

    stripped.info = get_gene_dict_info(stripped)
    stripped.header = header
    write_gdt_file(stripped, gdt_file_out, overwrite=overwrite)

    print("Info before stripping:")
    [print(x) for x in gene_dict.info]

    print("\nNew Header:")
    [print(x) for x in stripped.header]
    print("New Info:")
    [print(x) for x in stripped.info]


def create_empty_gdt(gdt_file: Union[Path, str]) -> None:
    """Create an empty GDT file.
    Args:
        gdt_file (str): Path to the GDT file.
    """
    gdt_file = Path(gdt_file).resolve()

    with open(gdt_file, "w") as f:
        f.write("#! version 0.0.2\n")
        f.write(f"#! {datetime.now().strftime('%Y-%m-%d %H:%M')} - Empty gdt_file\n")
