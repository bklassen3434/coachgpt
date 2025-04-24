import streamlit as st
import json
from pathlib import Path
import random

qa_path = Path("synthetic_data/generated_softball_qa.jsonl")
qa_data = [json.loads(line) for line in qa_path.read_text().splitlines()]

# Randomly sample 10% of the data
sample_size = max(1, int(len(qa_data) * 0.1))
sampled_qa = random.sample(qa_data, sample_size)

accepted = []
rejected = []
edited = []

st.title("🧑‍⚖️ Softball QA Review Interface")
st.markdown(f"### Reviewing {sample_size} randomly selected QA pairs (10% of total)")

for i, qa in enumerate(sampled_qa):
    st.markdown(f"### {i+1}. {qa['question']}")
    answer = st.text_area("Answer", qa['answer'], key=f"answer_{i}")

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("✅ Accept", key=f"accept_{i}"):
            accepted.append({"question": qa["question"], "answer": answer})
    with col2:
        if st.button("❌ Reject", key=f"reject_{i}"):
            rejected.append(qa)
    with col3:
        if st.button("✏️ Edit", key=f"edit_{i}"):
            edited.append({"question": qa["question"], "answer": answer})

# Save reviewed data
if st.button("💾 Save Reviewed"):
    with open("qa_accepted.jsonl", "w") as f:
        for qa in accepted:
            f.write(json.dumps(qa) + "\n")
    st.success("✅ Saved accepted responses.")
