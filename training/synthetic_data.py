import openai
import json
from pathlib import Path
from dotenv import load_dotenv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('qa_generation.log')
    ]
)

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)


# ------------------ Overview ------------------ #
# This script generates synthetic data for a softball rules assistant.
# It uses OpenAI's GPT-4o-mini model to generate questions and answers based on rule text.
# The generated data is saved in a JSONL file.



# ------------------ Generate QA ------------------ #
def generate_qa(rule):
    content = rule["content"]
    meta = rule["metadata"]
    rule_number = meta.get("rule_number", "N/A")
    rule_title = meta.get("rule_title", "Untitled")

    logging.info(f"Processing rule {rule_number}: {rule_title}")

    prompt = f"""
    You are generating training data for a softball rules assistant.

    Using the NCAA rule below, create:
    1. A realistic question a coach or umpire might ask about the rule.
    2. A clear, helpful answer that references the rule text.

    Only respond in this exact JSON format — no commentary, no code block, no extra text:

    {{
    "question": "...",
    "answer": "..."
    }}

    Rule {rule_number}: {rule_title} 
    Rule text: "{content}"
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=300
        )
        raw = response.choices[0].message.content

        if raw.startswith("```json"):
            raw = raw.replace("```json", "").replace("```", "").strip()

        try:
            result = json.loads(raw)
            logging.info(f"Successfully generated QA for rule {rule_number}")
            return result
        except json.JSONDecodeError:
            logging.error(f"JSON Parse Fail for rule {rule_number} - Raw Output:\n{raw}")
            return None
    except Exception as e:
        logging.error(f"Error processing rule {rule_number}: {str(e)}")
        return None

def main():
    logging.info("Starting QA generation process")
    
    with open("../preprocessed/pdfs_ncaa_softball_rulebook_202223.json", "r") as f:
        rules = json.load(f)
    
    logging.info(f"Loaded {len(rules)} rules to process")

    output_path = Path("synthetic_data/synthetic_softball_qa.jsonl")
    processed_count = 0
    total_rules = len(rules)

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(generate_qa, rule) for rule in rules]

        with open(output_path, "w") as out_f:
            for future in as_completed(futures):
                qa = future.result()
                if qa:
                    out_f.write(json.dumps(qa) + "\n")
                processed_count += 1
                logging.info(f"Progress: {processed_count}/{total_rules} rules processed")

    logging.info("QA generation process completed")

if __name__ == "__main__":
    main()
