

def params_to_CLI(params:dict, sep=" ", br=" ") :
    """
    Loads CLI parameters from a dict and generates a single string to add to the command line.
    A double dash is prepended to multiletters parameters and a single dash is prepended to single letter parmaters.
    """
    final = ""
    for key, value in params.items() :
        key = f"-{key}" if len(key) == 1 else f"--{key}"
        final += f"{key}{sep}{value}{br}"
    
    return final
