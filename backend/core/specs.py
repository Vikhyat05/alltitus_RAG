functions = [
    {
        "name": "insurance_doc_search",
        "description": "Call this function whenever the user asks a question about insurance (e.g., deductibles, coverage limits, copays, exclusions). It runs a semantic search against the Supabase vector store that contains parsed insurance documents and returns the top-matching text chunks. The function accepts only the user’s query string and returns a list of dictionaries (each with content, metadata, and similarity).",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The insurance-related question or phrase you want to look up.",
                }
            },
            "required": ["query"],
        },
    }
]
