"""Hugging Face / sentence-transformers cache paths for production (systemd)."""
import os


def configure_ml_cache():
    """Point model downloads to a writable directory under /opt/cortex."""
    if os.getenv("FLASK_ENV", "").lower() == "production":
        default_root = "/opt/cortex/.cache"
    else:
        default_root = os.path.join(os.getcwd(), ".cache")

    cache_root = os.getenv("CORTEX_ML_CACHE", default_root)
    hf_home = os.getenv("HF_HOME", os.path.join(cache_root, "huggingface"))
    st_home = os.getenv(
        "SENTENCE_TRANSFORMERS_HOME",
        os.path.join(cache_root, "sentence_transformers"),
    )

    for path in (cache_root, hf_home, st_home):
        os.makedirs(path, exist_ok=True)

    os.environ.setdefault("HF_HOME", hf_home)
    os.environ.setdefault("TRANSFORMERS_CACHE", hf_home)
    os.environ.setdefault("HUGGINGFACE_HUB_CACHE", hf_home)
    os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", st_home)
    return hf_home


def load_embeddings():
    configure_ml_cache()
    from langchain_community.embeddings import HuggingFaceEmbeddings

    model = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    return HuggingFaceEmbeddings(model_name=model)