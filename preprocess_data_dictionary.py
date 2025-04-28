import re
import json
import pdfplumber
from helper import is_garbage



# ------------------ Input PDF ------------------ #
pdf_path = "PDFs/Yakkertech Data Dictionary.pdf"


# ------------------ Extract Text With Bullet Points From PDF ------------------ #
def read_data_dictionary(file_path: str) -> str:

    full_text = ""
    found_first_header = False

    column_header_pattern = re.compile(r"\u25cf\s+(.+?)\s+\((\w+)\):\s+(.*)")

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            lines = text.split("\n")
            page_text = ""
            
            for line in lines:
                if not found_first_header:
                    if column_header_pattern.match(line.strip()):
                        found_first_header = True
                        page_text += line + "\n"
                else:
                    page_text += line + "\n"
                    
            if page_text:
                full_text += page_text

    return full_text

# ------------------ Chunk Data Dictionary ------------------ #
def chunk_data_dictionary(text: str) -> list[dict]:
    lines = text.split("\n")
    chunks = []
    
    current_chunk = ""
    current_header = ""
    current_column = ""
    
    # Pattern to match both standard and comma-separated formats, capturing up to the )
    column_header_pattern = re.compile(r"\u25cf\s+(.+?)\s*\(([A-Z,-]+)\)")
    
    for line in lines:
        line = line.strip()
        
        if "\u25cf" in line:
            # Save previous chunk if it exists
            if current_chunk:
                chunks.append({
                    "header": current_header,
                    "column": current_column, 
                    "content": current_chunk.strip().replace("\u25cf", "")
                })
            
            # Start new chunk
            match = column_header_pattern.match(line)
            if match:
                # Everything before the parentheses becomes the header
                current_header = match.group(1).strip()
                current_column = match.group(2)
                # Get content after the )
                content_start = match.end()
                content = line[content_start:].strip()
                if content.startswith(":"): # Remove leading colon if present
                    content = content[1:].strip()
                # Remove bullet point and leading space
                current_chunk = f"{line[:content_start].replace('\u25cf', '')} {content}\n"
            else:
                # Remove bullet point and leading space
                current_chunk = line.replace("\u25cf ", "", 1) + "\n"
                current_header = ""
                current_column = ""
        else:
            current_chunk += line + "\n"

    # Add final chunk if it exists
    if current_chunk:
        chunks.append({
            "header": current_header,
            "column": current_column,
            "content": current_chunk.strip().replace("\u25cf", "")
        })

    return chunks


# ------------------ Add Metadata To Data Dictionary ------------------ #
def add_metadata(chunks: list, source="Yakkertech Data Dictionary")-> list[dict]:
    # # Filter out garbage first
    # filtered = [
    #     chunk for chunk in chunks
    #     if not is_garbage(chunk["content"], min_unique_ratio=0.25, min_word_count=5)
    # ]

    formatted = []
    for i, chunk in enumerate(chunks):
        header = chunk["header"]
        column = chunk["column"]
        # Create unique ID from source and column name
        chunk_id = f"{source.lower().replace(' ', '_')}_{header}"

        formatted.append({
            "content": chunk["content"],
            "metadata": {
                "id": chunk_id,
                "source": "PDF",
                "collection": "Data Dictionary",
                "document_name": source,
                "column_name": header,
                "column_letter": column,
            }
        })

    return formatted

def main():
    text = read_data_dictionary(pdf_path)
    chunks = chunk_data_dictionary(text)
    formatted_chunks = add_metadata(chunks)

    with open(f"preprocessed/{pdf_path.strip().lower().replace('.pdf',  '').replace('/', '_')}.json", "w") as f:
        json.dump(formatted_chunks, f, indent=2)



if __name__ == "__main__":
    main()