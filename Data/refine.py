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
    with open(file_path, "r") as f:
        raw_md = f.read()

    text = raw_md
    text = text.replace("\n", " ")

    return text


def format_markdown_with_gpt(markdown_text: str) -> str:
    """
    Sends markdown to GPT-4 and asks it to return well-structured plain text
    with headings, paragraphs, and tables converted into bullet lists.
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
    Refines the markdown text from the file and returns the cleaned text.
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
