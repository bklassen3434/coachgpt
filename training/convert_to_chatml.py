import json
from pathlib import Path

def convert_qa_to_chatml(qa_data):
    """Convert QA pairs into ChatML format."""
    chatml_data = []
    
    for qa in qa_data:
        conversation = [
            {
                "role": "system",
                "content": "You are a helpful assistant that answers questions about NCAA softball rules. Provide clear, accurate answers based on the official rules."
            },
            {
                "role": "user",
                "content": qa["question"]
            },
            {
                "role": "assistant",
                "content": qa["answer"]
            }
        ]
        chatml_data.append(conversation)
    
    return chatml_data

def main():
    # Read the QA data
    qa_path = Path("synthetic_data/synthetic_softball_qa.jsonl")
    qa_data = [json.loads(line) for line in qa_path.read_text().splitlines()]
    
    # Convert to ChatML format
    chatml_data = convert_qa_to_chatml(qa_data)
    
    # Save the ChatML data
    output_path = Path("training_data/softball_qa_chatml.jsonl")
    with open(output_path, "w") as f:
        for conversation in chatml_data:
            f.write(json.dumps(conversation) + "\n")
    
    print(f"Converted {len(chatml_data)} QA pairs to ChatML format")
    print(f"Saved to {output_path}")

if __name__ == "__main__":
    main() 