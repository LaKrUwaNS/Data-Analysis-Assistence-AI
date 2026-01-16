#!/usr/bin/env python3
"""
Setup script to pull required Ollama models for the RAG application.
"""

import subprocess
import sys

REQUIRED_MODELS = [
    ("nomic-embed-text", "Embedding model (recommended)", True),
    ("llama3.2", "Language model for Q&A", False),
]

ALTERNATIVE_MODELS = [
    ("all-minilm", "Alternative embedding model"),
    ("llama3", "Alternative language model (larger)"),
    ("gemma3:1b", "Alternative language model (smaller)"),
]

def check_ollama_installed():
    """Check if Ollama is installed."""
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False

def list_installed_models():
    """List all installed Ollama models."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            return result.stdout
        return ""
    except Exception as e:
        print(f"Error listing models: {e}")
        return ""

def pull_model(model_name):
    """Pull an Ollama model."""
    print(f"\n📥 Pulling {model_name}...")
    try:
        result = subprocess.run(
            ["ollama", "pull", model_name],
            capture_output=False,
            text=True,
            timeout=600  # 10 minutes timeout
        )
        if result.returncode == 0:
            print(f"✅ Successfully pulled {model_name}")
            return True
        else:
            print(f"❌ Failed to pull {model_name}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏱️  Timeout while pulling {model_name}")
        return False
    except Exception as e:
        print(f"❌ Error pulling {model_name}: {e}")
        return False

def main():
    print("=" * 60)
    print("RAG Data Assistant - Model Setup")
    print("=" * 60)

    # Check if Ollama is installed
    if not check_ollama_installed():
        print("\n❌ Ollama is not installed or not in PATH.")
        print("\nPlease install Ollama first:")
        print("  Visit: https://ollama.ai/download")
        print("\nAfter installation, run this script again.")
        sys.exit(1)

    print("\n✅ Ollama is installed")

    # List currently installed models
    print("\n📋 Currently installed models:")
    print("-" * 60)
    installed = list_installed_models()
    if installed:
        print(installed)
    else:
        print("  No models found or unable to list models")

    # Check which required models are missing
    missing_models = []
    for model_name, description, required in REQUIRED_MODELS:
        if model_name not in installed:
            missing_models.append((model_name, description, required))

    if not missing_models:
        print("\n✅ All required models are already installed!")
        return

    # Show missing models
    print("\n📦 Missing models:")
    print("-" * 60)
    for model_name, description, required in missing_models:
        status = "REQUIRED" if required else "RECOMMENDED"
        print(f"  • {model_name} - {description} [{status}]")

    # Ask user if they want to pull models
    print("\n" + "=" * 60)
    response = input("\nDo you want to pull the missing models? (y/n): ").strip().lower()

    if response != 'y':
        print("\n⚠️  Skipping model installation.")
        print("\nTo manually install models, run:")
        for model_name, _, _ in missing_models:
            print(f"  ollama pull {model_name}")
        return

    # Pull missing models
    print("\n" + "=" * 60)
    success_count = 0
    for model_name, description, _ in missing_models:
        if pull_model(model_name):
            success_count += 1

    # Summary
    print("\n" + "=" * 60)
    print(f"\n✅ Successfully pulled {success_count}/{len(missing_models)} models")

    if success_count == len(missing_models):
        print("\n🎉 Setup complete! You can now run the application:")
        print("  streamlit run app.py")
    else:
        print("\n⚠️  Some models failed to install.")
        print("\nAlternative models you can try:")
        for model_name, description in ALTERNATIVE_MODELS:
            print(f"  ollama pull {model_name}  # {description}")

if __name__ == "__main__":
    main()

