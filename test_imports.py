#!/usr/bin/env python3
"""Test script to verify all imports work correctly."""

print("Testing imports...")

try:
    import os
    print("✓ os imported")

    import streamlit as st
    print("✓ streamlit imported")

    from langchain_core.documents import Document
    print("✓ Document imported from langchain_core")

    from langchain_community.vectorstores import FAISS
    print("✓ FAISS imported from langchain_community")

    from langchain_text_splitters import RecursiveCharacterTextSplitter
    print("✓ RecursiveCharacterTextSplitter imported")

    from utils.llm import get_llm, get_embeddings
    print("✓ utils.llm imported")

    from utils.data_tools import load_dataframe, dataframe_to_documents, load_pdf_documents
    print("✓ utils.data_tools imported")

    from utils.visualization import visualize_missing, visualize_distributions
    print("✓ utils.visualization imported")

    print("\n✅ All imports successful! The ModuleNotFoundError has been fixed.")

except ModuleNotFoundError as e:
    print(f"\n❌ Import failed: {e}")
    exit(1)
except Exception as e:
    print(f"\n⚠️  Unexpected error: {e}")
    exit(1)

