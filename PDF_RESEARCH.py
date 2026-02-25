import os
import streamlit as st
import time
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
st.set_page_config(page_title="PDF RESEARCH", layout="wide")
st.title("PDF Research Tool 📚")
st.sidebar.title("Upload PDF Files")
uploaded_pdfs = []
for i in range(3):
    uploaded_file = st.sidebar.file_uploader(
        f"Upload PDF {i+1}",
        type=["pdf"],
        key=f"pdf_{i}"
    )
    if uploaded_file:
        uploaded_pdfs.append(uploaded_file)

process_pdf_clicked = st.sidebar.button("Process PDFs")
persist_directory = "chroma_store"
if process_pdf_clicked:
    if not uploaded_pdfs:
        st.error("Please upload at least one PDF.")
        st.stop()
    all_docs = []
    for uploaded_file in uploaded_pdfs:
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        loader = PyPDFLoader(uploaded_file.name)
        data = loader.load()
        all_docs.extend(data)
    if not all_docs:
        st.error("No text extracted from PDFs.")
        st.stop()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=200
    )
    docs = text_splitter.split_documents(all_docs)
    if not docs:
        st.error("Text splitting failed.")
        st.stop()
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vectorstore = Chroma.from_documents(
        docs,
        embeddings,
        persist_directory=persist_directory
    )
    vectorstore.persist()

    st.success("Embeddings created successfully ✅")
    time.sleep(1)
query = st.text_input("Ask a question about your PDFs:")
if query:
    if not os.path.exists(persist_directory):
        st.warning("Please process PDFs first.")
        st.stop()

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )
    results = vectorstore.similarity_search(query, k=1)
    st.header("Top Matching Results 📄")
    for i, doc in enumerate(results):
        st.write(f"### Result")
        st.write(doc.page_content)

        st.divider()
