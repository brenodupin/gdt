# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
import re
from typing import Optional
from pathlib import Path
import gdt.gff3_utils

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
    """ Get information about the gene dictionary.
    Args:
        gene_dict (dict): A dictionary containing gene information.
    Returns:
        info (str): A string containing information about the gene dictionary.
    """
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

def create_gene_dict(gdt_file: str, max_an_sources:int = 20) -> dict:
    """ Create a gene dictionary from a GDT file.
    Args:
        gdt_file (str): Path to the GDT file.
        max_an_sources (int): Maximum number of AN sources to include in GeneGeneric. If set to 0, all sources will be included. Default is 20.
    Returns:
        gene_dict (dict): A dictionary containing gene information.
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
            
            if len(an_sources) >= max_an_sources and max_an_sources > 0:
                an_sources = an_sources[:max_an_sources]
                comment = comment if comment else ''
                comment += f' |More than {max_an_sources} sources, adding only the first {max_an_sources}|'
            
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
    
    result['info'] = get_gene_dict_info(result)
    result['header'] = header
    return result

def natural_sort(iterable):
    """ Sort a list of strings in natural order.
    Args:
        iterable (list): A list of strings to sort.
    Returns:
        list: A sorted list of strings in natural order.
    """
    def natural_sort_key(s):
        return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]
    return sorted(iterable, key=natural_sort_key)

def write_gdt_file(gene_dict: dict, gdt_file: str, overwrite: bool = False) -> None:
    """ Write a gene dictionary to a GDT file.
    Args:
        gene_dict (dict): A dictionary containing gene information.
        gdt_file (str): Path to the GDT file.
    """
    gdt_file = Path(gdt_file).resolve()
    if gdt_file.exists() and not overwrite:
        raise FileExistsError(f"GDT file already exists: {gdt_file}. Use overwrite=True to overwrite.")
    
    if gene_dict['header'][0] != 'version 0.0.2':
        raise ValueError(f"GDT not on version 0.0.2. GDT version: {gene_dict['header'][0]}")

    # drop header and value keys from gene_dict
    header = gene_dict.pop('header')
    info = gene_dict.pop('info')
    all_labels = natural_sort({gene.label for gene in gene_dict.values()})

    with open(gdt_file, 'w') as f:
        for line in header:
            f.write(f'#! {line}\n')
        
        for tag in all_labels:
            f.write(f'\n[{tag}]\n')
            for key in gene_dict:
                if gene_dict[key].label == tag:
                    if isinstance(gene_dict[key], GeneDbxref):
                        f.write(f'{key} #dx {gene_dict[key].an_source}:{gene_dict[key].dbxref}'
                                f'{" #c " + gene_dict[key].c if gene_dict[key].c else ""}\n')
                    elif isinstance(gene_dict[key], GeneGeneric):
                        if gene_dict[key].an_sources:
                            f.write(f'{key} #gn {" ".join(gene_dict[key].an_sources)}'
                                    f'{" #c " + gene_dict[key].c if gene_dict[key].c else ""}\n')
                        else:
                            f.write(f'{key} #gn'
                                    f'{" #c " + gene_dict[key].c if gene_dict[key].c else ""}\n')
                    elif isinstance(gene_dict[key], GeneDescription):
                        f.write(f'{key} #gd {gene_dict[key].source}'
                                f'{" #c " + gene_dict[key].c if gene_dict[key].c else ""}\n')
                    else:
                        raise TypeError(f"Unknown type {type(gene_dict[key])} for |{key}|:|{gene_dict[key]}|")
    
    gene_dict['header'] = header
    gene_dict['info'] = info


if __name__ == "__main__":
    exit(0)

    ans = ['NC_007982.1', 'NC_007886.1', 'NC_006581.1', 'NC_002511.2', 'NC_001660.1']
    test_dir = Path('test_stuff').resolve()
    for an in ans:
        an = an.strip() + '.gff3'
        print(f'Doing {an}')
        a_1 = gdt.gff3_utils.load_gff3(test_dir / an, query_string='type == "gene"')
        a_1_norfs = gdt.gff3_utils.filter_orfs(a_1)

        a_2 = gdt.gff3_utils.load_gff3(test_dir / an, query_string='type == "gene"')
        a_2_norfs = gdt.gff3_utils.filter_orfs(a_2)
    
        print(f'load normal: {a_1.equals(a_2)}')
        print(f'filter orfs: {a_1_norfs.equals(a_2_norfs)}')

        print(a_1_norfs.info())
        print(a_2_norfs.info())
        raise
