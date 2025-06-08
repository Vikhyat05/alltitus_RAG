import os
from markdown_it import MarkdownIt
from dotenv import load_dotenv
from openai import OpenAI
from supabase import create_client
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

# Init
openai_key = os.getenv("OPENAI_API_KEY")
supabase_url = os.getenv("SUPABASE_URL")
supabase_service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
openai_client = OpenAI(api_key=openai_key)
supabase = create_client(supabase_url, supabase_service_role_key)

# Markdown parser
md = MarkdownIt()


splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)


# Read and chunk a .txt file
def get_text_chunks(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    text = text.replace("\n", " ")
    chunks = splitter.split_text(text)
    return chunks


# Embed each chunk using OpenAI
def get_embeddings(texts):
    response = openai_client.embeddings.create(
        model="text-embedding-3-small", input=texts
    )
    return [e.embedding for e in response.data]


# Upload chunks and embeddings to Supabase
def upload_to_supabase(chunks, embeddings, source_file):
    for chunk, embed in zip(chunks, embeddings):
        supabase.table("markdown_docs").insert(
            {"content": chunk, "embedding": embed, "metadata": {"source": source_file}}
        ).execute()


# Main processor for a single file
def process_file(file_path):
    chunks = get_text_chunks(file_path)
    embeddings = get_embeddings(chunks)
    upload_to_supabase(chunks, embeddings, os.path.basename(file_path))


# Process all .txt files in ./cleaned folder
folder = "./cleaned"
for fname in os.listdir(folder):
    if fname.endswith(".txt"):
        print(f"Processing {fname}...")
        process_file(os.path.join(folder, fname))
