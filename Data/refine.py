import os
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client


load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
supabase_url = os.getenv("SUPABASE_URL")
supabase_service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
openai_client = OpenAI(api_key=openai_key)
supabase = create_client(supabase_url, supabase_service_role_key)


def get_markdown_chunks(file_path):
    """
    Reads raw markdown content from the specified file and returns it as a single string,
    with newline characters replaced by spaces to normalize formatting.

    Args:
        file_path (str): Path to the markdown file.

    Returns:
        str: Flattened markdown content as a single string.
    """
    with open(file_path, "r") as f:
        raw_md = f.read()

    text = raw_md
    text = text.replace("\n", " ")

    return text


def format_markdown_with_gpt(markdown_text: str) -> str:
    """
    Sends raw markdown text to GPT-4 and requests a cleaned, structured plain-text version.

    The system prompt asks GPT to:
    - Preserve heading hierarchy
    - Convert tables into bullet points
    - Produce RAG-friendly, well-chunked output

    Args:
        markdown_text (str): Raw markdown content as a string.

    Returns:
        str: Cleaned and structured plain text response from GPT-4.
    """
    system_prompt = (
        "You are a Markdown cleaner that converts raw markdown text into readable plain text. "
        "Preserve meaningful headings and hierarchy. "
        "Convert all tables into clean bullet-point format with headers as bold labels. "
        "Make sure the result is clean and chunk-friendly for my RAG system. "
    )

    user_prompt = (
        f"Format this markdown content into structured plain text:\n\n{markdown_text}"
    )

    response = openai_client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
    )

    return response.choices[0].message.content.strip()


def refine_text(file_path: str) -> str:
    """
    Refines the content of a markdown file by converting it into readable plain text
    using GPT formatting.

    Args:
        file_path (str): Path to the markdown (.md) file.

    Returns:
        str: Cleaned and formatted plain text.
    """
    raw_text = get_markdown_chunks(file_path)

    refined_text = format_markdown_with_gpt(raw_text)

    return refined_text


folder = "./markdowns"

input_folder = "./markdowns"
output_folder = "./cleaned"

for fname in os.listdir(input_folder):
    if fname.endswith(".md"):
        print(f"Processing {fname}...")
        file_path = os.path.join(input_folder, fname)
        refined = refine_text(file_path)

        # Save to cleaned .txt file
        output_path = os.path.join(output_folder, fname.replace(".md", ".txt"))
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(refined)

        print(f"Saved to {output_path}")
