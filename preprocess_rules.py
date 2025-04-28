import pdfplumber
import re
import json
from helper import is_garbage
from llms import summarize_chunks


# ------------------ Input PDF ------------------ #
pdf_path = "PDFs/NCAA_Softball_Rulebook_202223.pdf"



# ------------------ Extract Text From PDF With Rules Only ------------------ #
def extract_text_from_pdf_with_rules_only(pdf_path: str) -> str:

    full_text = ""
    rule_header_pattern = re.compile(r"^\d+\.\d+\s+.+")

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            # Check if any line matches the rule header format
            if any(rule_header_pattern.match(line.strip()) for line in text.split("\n")):
                full_text += text + "\n"

    return full_text



# ------------------ Chunk Rules ------------------ #
def chunk_rules(text: str) -> list[dict]:
    lines = text.split("\n")
    rule_chunks = []

    rule_header_pattern = re.compile(r"^(\d+\.\d+)\s+.+")

    current_chunk = ""
    current_header = ""

    for line in lines:
        line = line.strip()
        match = rule_header_pattern.match(line)

        if match:
            # Save previous chunk if it exists
            if current_chunk:
                rule_chunks.append({
                    "header": current_header,
                    "content": current_chunk.strip()
                })
            # Start new chunk
            current_header = line
            current_chunk = line + "\n"
        else:
            current_chunk += line + "\n"

    # Add final chunk if it exists
    if current_chunk:
        rule_chunks.append({
            "header": current_header,
            "content": current_chunk.strip()
        })

    return rule_chunks



# ------------------ Add Metadata To Rules ------------------ #
def add_metadata(rule_chunks: list[dict], source: str = "NCAA Rulebook 2022-23") -> list[dict]:
    # Filter out garbage first
    filtered = [
        chunk for chunk in rule_chunks
        if not is_garbage(chunk["content"], min_unique_ratio=0.25, min_word_count=5)
    ]

    # Summarize in batch
    summaries = summarize_chunks([chunk["content"] for chunk in filtered])

    formatted = []
    for i, chunk in enumerate(filtered):
        header = chunk["header"]
        match = re.match(r"^(\d+\.\d+)\s+(.+)", header)
        if not match:
            continue
        rule_title = match.group(2)
        rule_number = match.group(1)
        summary = summaries[i]

        # Create unique ID from source and rule number
        chunk_id = f"{source.lower().replace(' ', '_')}_{rule_number.replace('.', '_')}"

        formatted.append({
            "content": chunk["content"],
            "metadata": {
                "id": chunk_id,
                "source": "PDF", 
                "document_name": source,
                "collection": "Rules",
                "rule_title": rule_title,
                "rule_number": rule_number,
                "summary": summary
            }
        })
    return formatted



# ------------------ Main Pipeline ------------------ #
def main():
    rule_text = extract_text_from_pdf_with_rules_only(pdf_path)
    chunks = chunk_rules(rule_text)
    formatted_chunks = add_metadata(chunks)

    with open(f"preprocessed/{pdf_path.strip().lower().replace('.pdf',  '').replace('/', '_')}.json", "w") as f:
        json.dump(formatted_chunks, f, indent=2)

    

if __name__ == "__main__":
    main()