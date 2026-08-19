from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Document
from .embeddings import embed_text


@dataclass
class RetrievedChunk:
    source: str
    content: str
    score: float


def search_documents(db: Session, query: str, top_k: int = 5) -> list[RetrievedChunk]:
    """Busca por similaridade de cosseno usando pgvector (<=> operator)."""
    query_embedding = embed_text(query)

    stmt = (
        select(
            Document.source,
            Document.content,
            Document.embedding.cosine_distance(query_embedding).label("distance"),
        )
        .order_by("distance")
        .limit(top_k)
    )
    rows = db.execute(stmt).all()
    return [
        RetrievedChunk(source=row.source, content=row.content, score=1 - row.distance)
        for row in rows
    ]


def index_document(db: Session, source: str, chunks: list[str]) -> int:
    """Gera embeddings e insere os chunks na tabela documents. Retorna quantos foram inseridos."""
    from ..models import Document as DocumentModel

    for i, chunk in enumerate(chunks):
        db.add(
            DocumentModel(
                source=source,
                chunk_index=i,
                content=chunk,
                embedding=embed_text(chunk),
            )
        )
    db.commit()
    return len(chunks)
