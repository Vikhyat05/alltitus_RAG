from typing import Optional
from utils.query import semantic_search


async def function_calling_handler(calling_data, session_id: Optional[str]):
    func_name = calling_data["name"]

    if func_name == "insurance_doc_search":
        func_response = semantic_search(calling_data["arguments"]["query"])
        print(func_response)
        return {"role": "function", "name": func_name, "content": func_response}

    return None
