import os
import streamlit as st

from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter

from utils.llm import get_llm, get_embeddings
from utils.data_tools import load_dataframe, dataframe_to_documents, load_pdf_documents
from utils.visualization import visualize_missing, visualize_distributions

UPLOAD_DIR = "data/uploads"
VECTOR_DIR = "vectorstore/faiss_index"

os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VECTOR_DIR, exist_ok=True)

st.set_page_config(page_title="InsightRAG – Data Analysis Assistant", layout="wide")
st.title("📊 InsightRAG – AI Data Analysis Assistant")

# Initialize LLM and Embeddings
llm = get_llm()
embeddings = get_embeddings()

# Load or initialize vectorstore
vectorstore = None
if os.path.exists(VECTOR_DIR) and os.listdir(VECTOR_DIR):
    vectorstore = FAISS.load_local(
        VECTOR_DIR,
        embeddings,
        allow_dangerous_deserialization=True
    )

# Sidebar upload
st.sidebar.header("Upload Data")
file = st.sidebar.file_uploader(
    "Upload CSV, Excel, or PDF",
    type=["csv", "xlsx", "pdf"]
)

df = None

if file:
    save_path = os.path.join(UPLOAD_DIR, file.name)
    with open(save_path, "wb") as f:
        f.write(file.getbuffer())

    if file.name.endswith(("csv", "xlsx")):
        df = load_dataframe(save_path)
        st.sidebar.success("Dataset loaded")

        st.sidebar.write("Rows:", df.shape[0])
        st.sidebar.write("Columns:", df.shape[1])
        st.sidebar.write("Column Names:", df.columns.tolist())

        docs = dataframe_to_documents(df, file.name)

        if vectorstore:
            vectorstore.add_documents(docs)
        else:
            vectorstore = FAISS.from_documents(docs, embeddings)

        vectorstore.save_local(VECTOR_DIR)

        st.subheader("📈 Automatic Data Visualizations")
        visualize_missing(df)
        visualize_distributions(df)

    else:
        docs = load_pdf_documents(save_path)
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = splitter.split_documents(docs)

        if vectorstore:
            vectorstore.add_documents(docs)
        else:
            vectorstore = FAISS.from_documents(docs, embeddings)

        vectorstore.save_local(VECTOR_DIR)
        st.sidebar.success("PDF indexed successfully")

# Q&A Section
st.subheader("Ask Questions About Your Data")

question = st.text_input("Enter an analytical question")

if question and vectorstore:
    # Retrieve relevant documents
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    docs = retriever.invoke(question)

    # Combine document contents
    context = "\n\n".join([doc.page_content for doc in docs])

    # Create prompt and get answer
    prompt = f"""Based on the following context, answer the question.
    
Context:
{context}

Question: {question}

Answer:"""

    answer = llm.invoke(prompt)

    st.write("### Answer")
    st.write(answer)
