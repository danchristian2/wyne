from google.genai import types, errors
from .client import client, MODELS
from .tools import tools, TOOL_FUNCTIONS


def run_agent(user_message: str, max_steps: int = 5) -> str:
    contents = [types.Content(role="user", parts=[types.Part(text=user_message)])]
    model_index = 0

    for step in range(max_steps):
        current_model = MODELS[model_index]

        try:
            response = client.models.generate_content(
                model=current_model,
                contents=contents,
                config=types.GenerateContentConfig(tools=[tools]),
            )
        except errors.ClientError as e:
            if e.code == 429 and model_index < len(MODELS) - 1:
                model_index += 1
                print(f"[step {step}] {current_model} is out of quota, switching to {MODELS[model_index]}...")
                continue
            return f"Error: all models unavailable or a non-quota error occurred ({e})"

        candidate = response.candidates[0]
        contents.append(candidate.content)

        function_calls = [part.function_call for part in candidate.content.parts if part.function_call]

        if not function_calls:
            return response.text

        function_response_parts = []
        for call in function_calls:
            print(f"[step {step}] calling tool: {call.name}({dict(call.args)})")

            if call.name == "delete_file":
                confirm = input(f"⚠️  Agent wants to delete '{call.args.get('path')}'. Confirm? (y/n): ").strip().lower()
                if confirm != "y":
                    result = "User declined the deletion."
                else:
                    result = TOOL_FUNCTIONS[call.name](**call.args)
            elif call.name not in TOOL_FUNCTIONS:
                result = f"ERROR: tool '{call.name}' is not available."
            else:
                result = TOOL_FUNCTIONS[call.name](**call.args)

            function_response_parts.append(
                types.Part.from_function_response(name=call.name, response={"result": result})
            )

        contents.append(types.Content(role="user", parts=function_response_parts))

    return "Reached max steps without a final answer."