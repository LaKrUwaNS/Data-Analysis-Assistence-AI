from langchain_ollama import OllamaLLM, OllamaEmbeddings
import subprocess

def check_ollama_model(model_name: str) -> bool:
    """Check if an Ollama model is available."""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return model_name in result.stdout
    except Exception:
        return False

def get_llm(model: str = "llama3.2"):
    """Get LLM instance. Falls back to alternative models if not available."""
    fallback_models = ["llama3.2", "llama3.1:8b", "gemma3:1b"]

    for attempt_model in fallback_models:
        if check_ollama_model(attempt_model):
            if attempt_model != model:
                print(f"⚠️  Model '{model}' not found. Using '{attempt_model}' instead.")
                print(f"   To install the preferred model, run: ollama pull {model}")
            return OllamaLLM(
                model=attempt_model,
                temperature=0.1
            )

    raise ValueError(
        f"No language models are available.\n"
        f"Please install one by running:\n"
        f"  ollama pull llama3.2\n"
        f"  OR\n"
        f"  ollama pull llama3\n"
        f"  OR\n"
        f"  ollama pull gemma3:1b"
    )

def get_embeddings(model: str = "nomic-embed-text"):
    """Get embeddings instance. Falls back to alternative models if not available."""
    fallback_models = ["nomic-embed-text", "all-minilm", "llama3.2"]

    for attempt_model in fallback_models:
        if check_ollama_model(attempt_model):
            if attempt_model != model:
                print(f"WARNING: Using '{attempt_model}' for embeddings instead of '{model}'")
            return OllamaEmbeddings(model=attempt_model)

    # If no models are found, provide instructions
    raise ValueError(
        f"No embedding models found. Please install one by running:\n"
        f"  ollama pull nomic-embed-text\n"
        f"  OR\n"
        f"  ollama pull all-minilm\n\n"
        f"Recommended: ollama pull nomic-embed-text"
    )
