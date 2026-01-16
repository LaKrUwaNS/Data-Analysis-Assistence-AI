import pandas as pd
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader

def load_dataframe(path: str):
    if path.endswith(".csv"):
        return pd.read_csv(path)
    if path.endswith(".xlsx"):
        return pd.read_excel(path)
    return None

def dataframe_to_documents(df: pd.DataFrame, filename: str):
    docs = []

    docs.append(Document(
        page_content=(
            f"Dataset Overview for {filename}\n"
            f"Rows: {df.shape[0]}\n"
            f"Columns: {df.shape[1]}\n"
            f"Column Names: {list(df.columns)}"
        )
    ))

    docs.append(Document(
        page_content=f"Column Data Types:\n{df.dtypes.to_string()}"
    ))

    docs.append(Document(
        page_content=f"Missing Values Per Column:\n{df.isnull().sum().to_string()}"
    ))

    docs.append(Document(
        page_content=f"Statistical Summary:\n{df.describe(include='all').to_string()}"
    ))

    return docs

def load_pdf_documents(path: str):
    loader = PyPDFLoader(path)
    return loader.load()
