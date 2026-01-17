#!/usr/bin/env python3
"""Quick test to verify the setup."""

print("=" * 60)
print("Testing RAG Data Assistant Setup")
print("=" * 60)

print("\n1. Testing imports...")
try:
    from utils.llm import get_llm, get_embeddings
    print("   ✅ Imports successful")
except Exception as e:
    print(f"   ❌ Import failed: {e}")
    exit(1)

print("\n2. Testing LLM initialization...")
try:
    llm = get_llm()
    print("   ✅ LLM initialized")
except Exception as e:
    print(f"   ❌ LLM initialization failed: {e}")
    exit(1)

print("\n3. Testing embeddings initialization...")
try:
    embeddings = get_embeddings()
    print("   ✅ Embeddings initialized")
except Exception as e:
    print(f"   ❌ Embeddings initialization failed: {e}")
    exit(1)

print("\n" + "=" * 60)
print("✅ All tests passed! You can now run: streamlit run app.py")
print("=" * 60)

