import json
from dotenv import load_dotenv
from .specs import functions
import json
from typing import AsyncIterable, Optional
from .memory import memory
from .handler import function_calling_handler
from .llm import global_client
import json
from typing import AsyncIterable, Optional

load_dotenv()


async def assistant_response(memory):
    response = await global_client.chat.completions.create(
        model="gpt-4.1",
        messages=memory,
        temperature=0,
        stream=True,
        functions=functions,
        function_call="auto",
    )
    async for chunk in response:
        yield chunk


async def get_response(
    raw_message: str, custom_session_id: Optional[str]
) -> AsyncIterable[str]:

    history = ""
    messages = {"role": "user", "content": raw_message}
    memory.update_chat_history(custom_session_id, messages)
    history = memory.get_chat_history(custom_session_id)
    response_finished = True
    function_calling = False
    print("HISTORY______", history)

    while True:
        current_function = {"name": "", "arguments": ""}
        function_arg = ""
        assistant_accumulator = ""

        async for chunk in assistant_response(history):

            chunk = chunk.to_dict() if hasattr(chunk, "to_dict") else chunk.__dict__

            if "system_fingerprint" in chunk and custom_session_id:
                chunk["system_fingerprint"] = custom_session_id

            delta = chunk["choices"][0]["delta"]
            finish_reason = chunk["choices"][0]["finish_reason"]

            if "function_call" in delta:
                if "name" in delta["function_call"]:
                    current_function["name"] = delta["function_call"]["name"]
                if "arguments" in delta["function_call"]:
                    function_arg += delta["function_call"]["arguments"]

            if finish_reason == "stop":

                response_finished = True
                function_calling = False
            elif finish_reason == "function_call":
                current_function["arguments"] = json.loads(function_arg)

                history.append(
                    {
                        "role": "assistant",
                        "content": None,
                        "function_call": {
                            "name": current_function["name"],
                            "arguments": function_arg,
                        },
                    }
                )
                response_finished = False
                function_calling = True

            elif delta.get("content") is not None and finish_reason != "function_call":
                response_finished = False
                assistant_accumulator += delta["content"]
                yield "data: " + json.dumps(chunk) + "\n\n"

        if function_calling:
            print("Calling function:", current_function["name"])
            func_response = await function_calling_handler(
                current_function, custom_session_id
            )

            content = func_response["content"]
            if isinstance(content, list):
                content = "\n\n".join(
                    [
                        f"- {item['content']} (Source: {item['metadata'].get('source', 'N/A')})"
                        for item in content
                    ]
                )
                func_response["content"] = content

            history.append(func_response)

            response_finished = False
            function_calling = False
            continue

        if response_finished:
            break

    if assistant_accumulator:
        print("Final assistant response:", assistant_accumulator)
        print("Updating chat history with assistant response")
        memory.update_chat_history(
            custom_session_id,
            {"role": "assistant", "content": assistant_accumulator},
        )
