def append_line_to_file(path, line, overwrite = False):
    contents = ""
    if(not overwrite):
        with open(path, "r") as file:
            contents = file.read()

    with open(path, "w") as file:
        if(len(contents) > 0):
            contents += "\n"
        contents += line
        file.write(contents)