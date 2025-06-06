

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
