import os
from constants import EXTENSION_TO_SKIP
from utils.color_utils import blue


def write_file(filename: str, content: str, directory: str):
    print(blue(filename))

    file_path = os.path.join(directory, filename)
    dir = os.path.dirname(file_path)

    # Check if the filename is actually a directory
    if os.path.isdir(file_path):
        print(f"Error: {filename} is a directory, not a file.")
        return

    os.makedirs(dir, exist_ok=True)

    # Open the file in write mode
    with open(file_path, "w") as file:
        # Write content to the file
        file.write(content)


def clean_dir(directory: str) -> None:
    # Check if the directory exists
    if os.path.exists(directory):
        # If it does, iterate over all files and directories
        for dirpath, _, filenames in os.walk(directory):
            for filename in filenames:
                _, extension = os.path.splitext(filename)
                if extension not in EXTENSION_TO_SKIP:
                    os.remove(os.path.join(dirpath, filename))
    else:
        os.makedirs(directory, exist_ok=True)


def read_file(filename: str):
    with open(filename, 'r') as file:
        return file.read()


def walk_directory(directory: str):
    code_contents = {}
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            if not any(filename.endswith(ext) for ext in EXTENSION_TO_SKIP):
                try:
                    relative_filepath = os.path.relpath(os.path.join(dirpath, filename), directory)
                    code_contents[relative_filepath] = read_file(os.path.join(dirpath, filename))
                except Exception as e:
                    code_contents[relative_filepath] = f"Error reading file {filename}: {str(e)}"
    return code_contents
