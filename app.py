from sklearn.preprocessing import MinMaxScaler
import numpy as np
import streamlit as st
import os
import uuid
from utils.chunking import chunk_text
from utils.retriever import retriever
from utils.prompt import format_prompt
from utils.completion import complete

st.title("Hybrid RAG with BM25 + Chroma + CrossEncoder")

uploaded_files = st.file_uploader("Upload .txt files", type=["txt"], accept_multiple_files=True)

if uploaded_files:
    st.write(f"{len(uploaded_files)} file(s) uploaded.")
    chunks = []
    for file in uploaded_files:
        content = file.read().decode("utf-8")
        chunks.extend(chunk_text(content))
    retriever.index(chunks)
    st.success("Uploaded documents indexed successfully.")

elif st.button("Index Preloaded Documents"):
    st.write("Indexing preloaded files in /data...")
    data_dir = "data"
    raw_texts = []
    for filename in os.listdir(data_dir):
        if filename.endswith(".txt"):
            with open(os.path.join(data_dir, filename), 'r', encoding='utf-8') as f:
                raw_texts.append(f.read())

    chunks = []
    for text in raw_texts:
        chunks.extend(chunk_text(text))

    retriever.index(chunks)
    st.success("Preloaded documents indexed successfully.")

query = st.text_input("Ask a question")
if query:
    top_results = retriever.retrieve(query, k=3, return_scores=True)
    contexts, scores = zip(*top_results)
    scaler = MinMaxScaler()
    scores_np = np.array(scores).reshape(-1, 1)
    norm_scores = scaler.fit_transform(scores_np).flatten()

    prompt = format_prompt(query, contexts)
    answer = complete(prompt)

    st.subheader("Answer")
    st.write(answer)

    st.subheader("Top Contexts with Scores")
    for idx, (context, norm_score) in enumerate(zip(contexts, norm_scores)):
        st.markdown(f"**Context {idx+1} (Score: {norm_score:.4f}):**\n{context}")
