from typing import Optional
from utils.query import semantic_search


async def function_calling_handler(calling_data, session_id: Optional[str]):
    """
    Handles function calls returned by the assistant during the chat flow.

    Currently supports:
    - "insurance_doc_search": Performs a semantic search on insurance documents
      using the query provided in the function arguments.

    Args:
        calling_data (dict): A dictionary containing the function call data from the assistant.
            Expected structure:
            {
                "name": "<function_name>",
                "arguments": {
                    "query": "<search_query>"
                }
            }
        session_id (Optional[str]): Unique session identifier (not used currently, but reserved for context-specific use).

    Returns:
        dict: A function message to be appended to the chat history in the format:
            {
                "role": "function",
                "name": "<function_name>",
                "content": "<result from function>"
            }

        None: If no supported function is matched.
    """
    func_name = calling_data["name"]

    if func_name == "insurance_doc_search":
        func_response = semantic_search(calling_data["arguments"]["query"])
        print(func_response)
        return {"role": "function", "name": func_name, "content": func_response}

    return None
