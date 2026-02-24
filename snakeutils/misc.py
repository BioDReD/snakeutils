from pathlib import Path

def params_to_CLI(params:dict, sep=" ", br=" ", wildcards=None) :
    """
    Loads CLI parameters from a dict and generates a single string to add to the command line.
    A double dash is prepended to multiletters parameters and a single dash is prepended to single letter parmaters.
    """
    final = ""
    for key, value in params.items() :
        if value is None : 
            value = ""
        
        key = f"-{key}" if len(key) == 1 else f"--{key}"
        final += f"{key}{sep}{value}{br}"
    
    if wildcards is not None : 
        final = final.format(wildcards=wildcards)

    return final

def infer_chromosome_list_from_genome(genome_file:"str|Path") : 
    """
    Given a genome file (.fa/.fasta), tries to load the index file (.fasta.fai) that is expected next to the genome file.
    Loads the chromosome names from it and returns them as a list.
    """
    index = Path(str(genome_file) + ".fai")
    if not index.exists() : 
        raise ValueError(f"The index file {index} could not be found ! This file must be present and can be generated with the command `samtools faidx {genome_file}`")
    
    with open(index) as fp : 
        chroms = [l.split()[0] for l in fp if l]
        return chroms