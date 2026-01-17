import os
import streamlit as st
import numpy as np

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

# Modify normalization to also add str keys (keeps ints and numpy.int64 compatible)
def _normalize_faiss_index_keys(vs):
    """
    Ensure vs.index_to_docstore_id contains python int, numpy.int64 and str keys
    for every mapping entry so lookups are robust when FAISS returns numpy types.
    """
    if vs is None:
        return
    if not hasattr(vs, "index_to_docstore_id"):
        return
    mapping = getattr(vs, "index_to_docstore_id", None)
    if not isinstance(mapping, dict):
        return

    # Rebuild the mapping with all key type variants
    new_map = {}
    for k, v in list(mapping.items()):
        # try plain python int
        try:
            ik = int(k)
            new_map[ik] = v
            new_map[np.int64(ik)] = v
            new_map[str(ik)] = v
        except (ValueError, TypeError):
            # keep original key if conversion fails
            new_map[k] = v

    vs.index_to_docstore_id = new_map
    return vs

def _validate_vectorstore(vs):
    """Check if vectorstore mapping is valid; return True if OK, False if corrupted."""
    if vs is None:
        return False
    if not hasattr(vs, "index") or not hasattr(vs, "index_to_docstore_id"):
        return False
    # Check if we have mappings for all indices in the FAISS index
    try:
        num_vectors = vs.index.ntotal
        mapping = vs.index_to_docstore_id
        # Try to access a few random indices to validate mapping
        for i in range(min(3, num_vectors)):
            test_keys = [i, np.int64(i), str(i)]
            if not any(k in mapping for k in test_keys):
                return False
        return True
    except Exception:
        return False

# Load or initialize vectorstore
vectorstore = None
if os.path.exists(VECTOR_DIR) and os.listdir(VECTOR_DIR):
    try:
        vectorstore = FAISS.load_local(
            VECTOR_DIR,
            embeddings,
            allow_dangerous_deserialization=True
        )
        # normalize keys right after loading
        _normalize_faiss_index_keys(vectorstore)

        # Validate the vectorstore; if corrupted, delete and rebuild
        if not _validate_vectorstore(vectorstore):
            st.warning("Corrupted vector index detected. Rebuilding from scratch...")
            vectorstore = None
            # Delete corrupted index files
            import shutil
            shutil.rmtree(VECTOR_DIR, ignore_errors=True)
            os.makedirs(VECTOR_DIR, exist_ok=True)
    except Exception as e:
        st.warning(f"Failed to load vector index: {e}. Starting fresh...")
        vectorstore = None
        import shutil
        shutil.rmtree(VECTOR_DIR, ignore_errors=True)
        os.makedirs(VECTOR_DIR, exist_ok=True)

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

        # Always rebuild from scratch to avoid key mismatch issues
        st.info("Building vector index from documents...")
        vectorstore = FAISS.from_documents(docs, embeddings)
        _normalize_faiss_index_keys(vectorstore)
        vectorstore.save_local(VECTOR_DIR)
        st.sidebar.success("Dataset indexed successfully")

        st.subheader("📈 Automatic Data Visualizations")
        visualize_missing(df)
        visualize_distributions(df)

    else:
        docs = load_pdf_documents(save_path)
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        docs = splitter.split_documents(docs)

        # Always rebuild from scratch to avoid key mismatch issues
        st.info("Building vector index from PDF documents...")
        vectorstore = FAISS.from_documents(docs, embeddings)
        _normalize_faiss_index_keys(vectorstore)
        vectorstore.save_local(VECTOR_DIR)
        st.sidebar.success("PDF indexed successfully")

# Q&A Section
st.subheader("Ask Questions About Your Data")

question = st.text_input("Enter an analytical question")

if question and vectorstore:
    # Check if vectorstore has documents
    try:
        num_docs = vectorstore.index.ntotal
        if num_docs == 0:
            st.warning("No documents found in the vector store. Please upload a file first.")
            st.stop()
        else:
            st.info(f"Searching through {num_docs} document chunks...")
    except Exception:
        pass

    # Normalize before creating retriever
    vectorstore = _normalize_faiss_index_keys(vectorstore)

    # Retrieve relevant documents with better error handling
    docs = []
    try:
        # Lower the search results if needed
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        docs = retriever.invoke(question)
        if docs:
            st.success(f"Found {len(docs)} relevant document chunks")
        else:
            st.warning("No relevant documents found for your question. Try rephrasing or uploading more data.")
    except KeyError as e:
        st.error(f"Vector index error detected. Deleting corrupted index...")
        # Delete corrupted index and force rebuild
        import shutil
        shutil.rmtree(VECTOR_DIR, ignore_errors=True)
        os.makedirs(VECTOR_DIR, exist_ok=True)
        vectorstore = None
        st.error("Please re-upload your data file.")
        st.stop()
    except Exception as e:
        st.error(f"Unexpected error during retrieval: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        docs = []

    if docs:
        # Combine document contents
        context = "\n\n".join([doc.page_content for doc in docs])

        # Show a preview of retrieved context (for debugging)
        with st.expander("View Retrieved Context"):
            st.text(context[:1000] + "..." if len(context) > 1000 else context)

        # Create prompt and get answer
        prompt = f"""Based on the following context, answer the question.
    
Context:
{context}

Question: {question}

Answer:"""

        with st.spinner("Generating answer..."):
            answer = llm.invoke(prompt)

        st.write("### Answer")
        st.write(answer)
elif question and not vectorstore:
    st.error("Please upload a data file first before asking questions.")
