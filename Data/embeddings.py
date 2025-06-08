import os
from markdown_it import MarkdownIt
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()


openai_key = os.getenv("OPENAI_API_KEY")
supabase_url = os.getenv("SUPABASE_URL")
supabase_service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
openai_client = OpenAI(api_key=openai_key)
supabase = create_client(supabase_url, supabase_service_role_key)


md = MarkdownIt()


splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)


def get_text_chunks(file_path):
    """
    Reads a text or markdown file and splits it into smaller text chunks
    for embedding using Langchain's RecursiveCharacterTextSplitter.

    Args:
        file_path (str): Path to the text file.

    Returns:
        list[str]: A list of text chunks.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    text = text.replace("\n", " ")
    chunks = splitter.split_text(text)
    return chunks


def get_embeddings(texts):
    """
    Generates embeddings for a list of text chunks using OpenAI's embedding model.

    Args:
        texts (list[str]): List of text strings to embed.

    Returns:
        list[list[float]]: List of embedding vectors corresponding to each text chunk.
    """
    response = openai_client.embeddings.create(
        model="text-embedding-3-small", input=texts
    )
    return [e.embedding for e in response.data]


def upload_to_supabase(chunks, embeddings, source_file):
    """
    Uploads text chunks and their embeddings to the Supabase `markdown_docs` table.

    Args:
        chunks (list[str]): Text chunks to store.
        embeddings (list[list[float]]): Corresponding embedding vectors.
        source_file (str): Name of the source file for metadata tracking.
    """
    for chunk, embed in zip(chunks, embeddings):
        supabase.table("markdown_docs").insert(
            {"content": chunk, "embedding": embed, "metadata": {"source": source_file}}
        ).execute()


def process_file(file_path):
    """
    Processes a single file by:
    - Splitting into chunks,
    - Embedding each chunk,
    - Uploading the results to Supabase.

    Args:
        file_path (str): Path to the file to process.
    """
    chunks = get_text_chunks(file_path)
    embeddings = get_embeddings(chunks)
    upload_to_supabase(chunks, embeddings, os.path.basename(file_path))


# === Batch Processing All .txt Files in Folder ===
folder = "./cleaned"
for fname in os.listdir(folder):
    if fname.endswith(".txt"):
        print(f"Processing {fname}...")
        process_file(os.path.join(folder, fname))
