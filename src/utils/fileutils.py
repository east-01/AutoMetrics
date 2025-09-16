def append_line_to_file(path, line, overwrite = False):
    """ Given a filepath, open it and append the line to it and save it.

    Arguments:
        path (str): The filepath.
        line (str): The line to append.
        overwrite (bool): Overwrite the file, if set to true the file will only have the new line
            after inserting.
    
    Returns: None.
    """
    
    contents = ""
    if(not overwrite):
        with open(path, "r") as file:
            contents = file.read()

    with open(path, "w") as file:
        if(len(contents) > 0):
            contents += "\n"
        contents += line
        file.write(contents)