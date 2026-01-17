#!/usr/bin/env python3
"""Validate that the RAG Data Assistant is properly configured."""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    try:
        import streamlit
        import pandas
        import numpy
        import matplotlib
        import seaborn
        from langchain_community.vectorstores import FAISS
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        from langchain_ollama import OllamaLLM, OllamaEmbeddings
        print("  ✅ All core imports successful")
        return True
    except ImportError as e:
        print(f"  ❌ Import error: {e}")
        return False

def test_utils():
    """Test utility modules."""
    print("\nTesting utility modules...")
    try:
        from utils.llm import get_llm, get_embeddings, check_ollama_model
        from utils.data_tools import load_dataframe, dataframe_to_documents
        print("  ✅ Utility imports successful")
        return True
    except Exception as e:
        print(f"  ❌ Utility import error: {e}")
        return False

def test_ollama_models():
    """Test that required Ollama models are available."""
    print("\nChecking Ollama models...")
    try:
        from utils.llm import check_ollama_model
        
        # Check for at least one LLM
        llm_models = ["llama3.2", "llama3", "gemma3:1b"]
        llm_found = any(check_ollama_model(m) for m in llm_models)
        
        # Check for at least one embedding model
        emb_models = ["nomic-embed-text", "all-minilm"]
        emb_found = any(check_ollama_model(m) for m in emb_models)
        
        if llm_found:
            print("  ✅ Language model available")
        else:
            print("  ⚠️  No language model found")
            print("     Run: ollama pull llama3.2")
        
        if emb_found:
            print("  ✅ Embedding model available")
        else:
            print("  ⚠️  No embedding model found")
            print("     Run: ollama pull nomic-embed-text")
        
        return llm_found and emb_found
    except Exception as e:
        print(f"  ❌ Error checking models: {e}")
        return False

def test_llm_initialization():
    """Test LLM and embeddings initialization."""
    print("\nTesting LLM initialization...")
    try:
        from utils.llm import get_llm, get_embeddings
        llm = get_llm()
        print("  ✅ LLM initialized")
        
        embeddings = get_embeddings()
        print("  ✅ Embeddings initialized")
        return True
    except Exception as e:
        print(f"  ❌ Initialization error: {e}")
        return False

def main():
    print("=" * 70)
    print("RAG Data Assistant - Setup Validation")
    print("=" * 70)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Utilities", test_utils()))
    results.append(("Ollama Models", test_ollama_models()))
    results.append(("Initialization", test_llm_initialization()))
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20s} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 70)
    
    if all_passed:
        print("\n🎉 All validations passed!")
        print("\nYou can now run the application:")
        print("  streamlit run app.py")
        return 0
    else:
        print("\n⚠️  Some validations failed.")
        print("\nPlease fix the issues above before running the application.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

