import os
import json
from google.genai import types


def count_files(path: str = ".", extension: str = None, recursive: bool = False) -> str:
    if not os.path.isdir(path):
        return f"Error: '{path}' is not a valid directory."

    count = 0
    matched = []

    if recursive:
        for root, _, files in os.walk(path):
            for f in files:
                if extension is None or f.lower().endswith(f".{extension.lstrip('.').lower()}"):
                    count += 1
                    matched.append(os.path.join(root, f))
    else:
        for f in os.listdir(path):
            full = os.path.join(path, f)
            if os.path.isfile(full):
                if extension is None or f.lower().endswith(f".{extension.lstrip('.').lower()}"):
                    count += 1
                    matched.append(full)

    return json.dumps({"count": count, "files": matched[:20]})


def get_file_size(path: str) -> str:
    if not os.path.exists(path):
        return f"Error: '{path}' does not exist."
    if os.path.isdir(path):
        return f"Error: '{path}' is a directory, not a file. Use count_files for directories."

    size_bytes = os.path.getsize(path)
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


TOOL_FUNCTIONS = {
    "count_files": count_files,
    "get_file_size": get_file_size,
}

count_files_declaration = types.FunctionDeclaration(
    name="count_files",
    description="Count the number of files in a directory, optionally filtered by extension.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Directory path to count files in. Defaults to the current directory."},
            "extension": {"type": "string", "description": "Optional file extension filter, e.g. 'pdf' or 'py'. Omit to count all files."},
            "recursive": {"type": "boolean", "description": "Whether to search subdirectories too. Defaults to false."},
        },
    },
)

get_file_size_declaration = types.FunctionDeclaration(
    name="get_file_size",
    description="Get the size of a specific file, shown in a human-readable unit (KB, MB, GB, etc).",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Full path to the file to check the size of."},
        },
    },
)

tools = types.Tool(function_declarations=[count_files_declaration, get_file_size_declaration])