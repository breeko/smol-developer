def shared_dependencies_prompt(prompt: str, filepaths_string: str) -> str:
    return f"""You are an AI developer who is trying to write a program that will generate code for the user based on their intent.
    
        In response to the user's prompt:
    
        ---
        the app is: {prompt}
        ---
    
        the files we have decided to generate are: {filepaths_string}
    
        Now that we have a list of files, we need to understand what dependencies they share.
        Please name and briefly describe what is shared between the files we are generating, including exported variables, data schemas, id names of every DOM elements that javascript functions will use, message names, and function names.
        Exclusively focus on the names of the shared dependencies, and do not add any other explanation.
    """
