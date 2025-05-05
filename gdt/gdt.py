# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path
from .gff3_utils import *

@dataclass
class Gene:
    __slots__ = ("label", "c")
    label: str
    c: Optional[str]

@dataclass
class GeneDbxref(Gene):
    __slots__ = ("an_source", "dbxref")
    an_source: str
    dbxref: int

@dataclass
class GeneGeneric(Gene):
    __slots__ = ("an_sources",)
    an_sources: list = field(default_factory=list)

@dataclass
class GeneDescription(Gene):
    __slots__ = ("source",)
    source: str

def _get_gene_dict_info(gene_dict: dict) -> str:
    labels, GeneGeneric_count, GeneDescription_count, GeneDbxref_count = set(), 0, 0, 0
    for key in gene_dict:
        labels.add(gene_dict[key].label)
        if isinstance(gene_dict[key], GeneDbxref):
            GeneDbxref_count += 1
        elif isinstance(gene_dict[key], GeneGeneric):
            GeneGeneric_count += 1
        elif isinstance(gene_dict[key], GeneDescription):
            GeneDescription_count += 1
        else:
            print(f"[INFO] Unknown type for key {key}: {type(gene_dict[key])}")
    
    info = []
    info.append(f"Gene dictionary length: {len(gene_dict)}")
    info.append(f"Label: {len(labels)}")
    info.append(f"GeneDescription: {GeneDescription_count}")
    info.append(f"GeneGenerics: {GeneGeneric_count}")
    info.append(f"GeneDbxref: {GeneDbxref_count}")
    return info

def create_gene_dict(gdt_file: str) -> dict:
    """ Create a gene dictionary from a GDT file.
    Args:
        gdt_file (str): Path to the GDT file.
    Returns:
        dict: A dictionary containing gene information.
    """
    gdt_file = Path(gdt_file).resolve()
    
    if not gdt_file.exists():
        raise FileNotFoundError(f"GDT file not found: {gdt_file}")
    
    with open(gdt_file, 'r') as f:
        lines = [line.strip() for line in f.read().split('\n') if line.strip()]
    
    if lines[0] != '#! version 0.0.2':
        raise ValueError(f"Invalid GDT file version: {lines[0]}. Expected '#! version 0.0.2'")
    
    result = {} 
    header = []
    for line in lines:
        if line.startswith('#!'):
            header.append(line[2:].strip())
            continue
        else:
            break
    
    current_section = None
    for line in lines:        
        if line.startswith('[') and line.endswith(']'):
            current_section = line[1:-1]
            continue
        
        # Skip if no section is defined
        if not line or not current_section:
            continue
        
        # Parse gene line
        tag = line.split('#', 1)[0].strip()
        if not tag:
            print(f"Skipping empty tag in line: {line}")
            continue

        if '#c' in line:
            line, comment = line.split('#c', 1)
            comment = comment.strip()
            line = line.strip()
        else:
            comment = None

        if '#dx' in line: # GeneDX type
            stuff = line.split('#dx', 1)[1].strip()
            an_source = stuff.split(':')[0].strip()
            dbxref = int(stuff.split(':')[1].strip())
            
            result[tag] = GeneDbxref(
                label=current_section,
                an_source=an_source,
                dbxref=dbxref,
                c=comment)
        
        elif '#gn' in line: # GeneND type
            an_sources = [s.strip() for s in line.split('#gn', 1)[1].strip().split()]
            an_sources = an_sources if an_sources else []
            if len(an_sources) >= 20:
                an_sources = an_sources[:20]
                comment = comment if comment else ''
                comment += ' |More than 20 sources, adding only the first 20|'
            result[tag] = GeneGeneric(
                label=current_section,
                an_sources=an_sources,
                c=comment)
        
        elif '#gd' in line: # GeneDescription type
            source = line.split('#gd', 1)[1].strip()
        
            result[tag] = GeneDescription(
                label=current_section,
                source=source,
                c=comment)
    
    result['info'] = _get_gene_dict_info(result)
    result['header'] = header
    return result


if __name__ == "__main__":
    exit(0)

    ans = ['NC_007982.1', 'NC_007886.1', 'NC_006581.1', 'NC_002511.2', 'NC_001660.1']
    test_dir = Path('test_stuff').resolve()
    for an in ans:
        an = an.strip() + '.gff3'
        print(f'Doing {an}')
        a_1 = load_gff3(test_dir / an, query_string='type == "gene"')
        a_1_norfs = filter_orfs(a_1)

        a_2 = load_gff3_2(test_dir / an, query_string='type == "gene"')
        a_2_norfs = filter_orfs_2(a_2)
    
        print(f'load normal: {a_1.equals(a_2)}')
        print(f'filter orfs: {a_1_norfs.equals(a_2_norfs)}')

        print(a_1_norfs.info())
        print(a_2_norfs.info())
        raise
