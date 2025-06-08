from llama_cloud_services import LlamaParse
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
llamaKey = os.getenv("llamaParse")

# Initialize parser
parser = LlamaParse(
    api_key=llamaKey,
    verbose=True,
    premium_mode=True,
    language="en",
)

# Input and output folders
input_folder = "Insurance PDFs"
output_folder = "markdowns"

# Create the markdowns folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Iterate over all PDF files in the folder
for filename in os.listdir(input_folder):
    if filename.endswith(".pdf"):
        pdf_path = os.path.join(input_folder, filename)
        print(f"Parsing file: {pdf_path}")

        # Parse the file
        result = parser.parse(pdf_path)
        markdown_documents = result.get_markdown_documents(split_by_page=True)

        # Generate output .md file path
        base_name = os.path.splitext(filename)[0]  # remove .pdf
        output_filename = base_name + ".md"
        output_path = os.path.join(output_folder, output_filename)

        # Write markdown to file
        with open(output_path, "w", encoding="utf-8") as f:
            for i, doc in enumerate(markdown_documents):
                f.write(f"## Page {i+1}\n\n")
                f.write(doc.text)
                f.write("\n\n---\n\n")

        print(f"Markdown file created at: {output_path}")

# from llama_cloud_services import LlamaParse
# from dotenv import load_dotenv
# import os


# load_dotenv()

# llamaKey = os.getenv("llamaParse")


# parser = LlamaParse(
#     api_key=llamaKey,
#     verbose=True,
#     premium_mode=True,
#     language="en",
# )

# result = parser.parse("Insurance PDFs/America's_Choice_7350_Copper_SOB (1) (1).pdf")

# text_doc = result.get_text_documents(split_by_page=True)
# print(text_doc)

# markdown_documents = result.get_markdown_documents(split_by_page=True)

# output_path = "Insurance PDFs/America's_Choice_7350_Copper_2.md"

# with open(output_path, "w", encoding="utf-8") as f:
#     for i, doc in enumerate(markdown_documents):
#         f.write(f"## Page {i+1}\n\n")
#         f.write(doc.text)
#         f.write("\n\n---\n\n")

# print(f"Markdown file created at: {output_path}")
