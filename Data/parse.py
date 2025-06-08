from llama_cloud_services import LlamaParse
from dotenv import load_dotenv
import os


load_dotenv()

llamaKey = os.getenv("llamaParse")


parser = LlamaParse(
    api_key=llamaKey,
    verbose=True,
    premium_mode=True,
    language="en",
)

result = parser.parse("Insurance PDFs/America's_Choice_7350_Copper_SOB (1) (1).pdf")

text_doc = result.get_text_documents(split_by_page=True)
print(text_doc)

markdown_documents = result.get_markdown_documents(split_by_page=True)

output_path = "Insurance PDFs/America's_Choice_7350_Copper_2.md"

with open(output_path, "w", encoding="utf-8") as f:
    for i, doc in enumerate(markdown_documents):
        f.write(f"## Page {i+1}\n\n")
        f.write(doc.text)
        f.write("\n\n---\n\n")

print(f"Markdown file created at: {output_path}")
