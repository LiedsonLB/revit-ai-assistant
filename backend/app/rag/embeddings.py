"""
Camada de embeddings — isolada aqui para trocar de estratégia sem tocar no resto:
hoje usa sentence-transformers local (multilingual, roda sem API key). Se preferir
usar embeddings via API (OpenAI/Voyage), troque só a função embed_text().
"""
from functools import lru_cache

from ..config import settings


@lru_cache(maxsize=1)
def _get_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(settings.embedding_model)


def embed_text(text: str) -> list[float]:
    model = _get_model()
    vector = model.encode(text, normalize_embeddings=True)
    return vector.tolist()


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """Chunking simples por caracteres com overlap. Suficiente para normas em texto corrido;
    troque por um splitter estrutural (ex: por seção/artigo) se o formato do documento pedir."""
    text = text.strip()
    if not text:
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks
