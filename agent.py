
import os  # this allows us to interact with files and more
import json
from dotenv import load_dotenv  # helps with environment variables
from google import genai  # helps in gemini model configuration
from google.genai import types  # importation of types which you will see down

load_dotenv()  # a function that loads dotenv

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"],
)  # initializing the model note that no bese url is required here cause the gemini SDK knows where to send the requests

count_files_declaration = types.FunctionDeclaration(
    name="count_files",
    description="Count the number of files in a directory, optionally filtered by extension.",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Directory path to count files in. Defaults to the current directory.",
            },
            "extension": {
                "type": "string",
                "description": "Optional file extension filter, e.g. 'pdf' or 'py'. Omit to count all files.",
            },
            "recursive": {
                "type": "boolean",
                "description": "Whether to search subdirectories too. Defaults to false.",
            },
        },
    },
)
get_file_size_declaration = types.FunctionDeclaration(
    name="get_file_size",
    description="Get the size of a specific file, display in a human readable format",
    parameters={
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "Full path to the file to check the size of .",
            },
        },
    },
)

tools = types.Tool(function_declarations=[count_files_declaration])


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

    return json.dumps({"count": count, "files": matched[:20]})  # cap preview list

def get_file_size(path: str) -> str:
    if not os.path.exists(path):
        return f"Error: '{path}' does not exist."

    if os.path.isdir(path):
        return f"Error: '{path}' is a directory not a file use count_files for files."
    size_bytes=os.path.getsize(path)

    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024

    return f"{size_bytes:.f} TB"
TOOL_FUNCTIONS = {"count_files": count_files, "get_file_size": get_file_size}


def run_agent(user_message: str, max_steps: int = 5) -> str:
    contents = [
        types.Content(role="user", parts=[types.Part(text=user_message)])
    ]

    for step in range(max_steps):
        response = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=contents,
            config=types.GenerateContentConfig(tools=[tools]),
        )

        candidate = response.candidates[0]
        contents.append(candidate.content)  # record the model's turn

        function_calls = [
            part.function_call
            for part in candidate.content.parts
            if part.function_call
        ]

        if not function_calls:
            return response.text

        function_response_parts = []
        for call in function_calls:
            print(f"[step {step}] calling tool: {call.name}({dict(call.args)})")
            if call.name not in TOOL_FUNCTIONS:
                result = f"ERROR: tool '{call.name}' is not available."
            else:
                fn = TOOL_FUNCTIONS[call.name]
                result = fn(**call.args)

            function_response_parts.append(
                types.Part.from_function_response(
                    name=call.name,
                    response={"result": result},
                )
            )

        contents.append(types.Content(role="user", parts=function_response_parts))

    return "Reached max steps without a final answer."


if __name__ == "__main__":
    print("File Assistant - ask me anything about files in a directory(counts, sizes,extentions).")
    print("Type 'quit' or 'exit' to stop.\n")

<<<<<<< HEAD
    question_count = 0
    while True:
        question = input("Ask me anything: ").strip()

        if question.lower() in ("quit", "exit"):
            print(f"Goodbye! You asked {question_count} question(s) this session.")
            break

        if not question:
            print("You didn't ask anything - try again.\n")
            continue

        question_count += 1
        answer = run_agent(question)
        print("\nAgent:", answer, "\n")