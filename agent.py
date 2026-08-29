
import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(
    api_key=os.environ["GEMINI_API_KEY"],
)

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


TOOL_FUNCTIONS = {"count_files": count_files}


def run_agent(user_message: str, max_steps: int = 5) -> str:
    contents = [
        types.Content(role="user", parts=[types.Part(text=user_message)])
    ]

    for step in range(max_steps):
        response = client.models.generate_content(
            model="gemini-3.6-flash",
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
    question = input("Ask me anything: ")
    answer = run_agent(question)
    print("\nAgent:", answer)