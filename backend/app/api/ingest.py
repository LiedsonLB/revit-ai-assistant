from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import IngestRequest
from ..rag.embeddings import chunk_text
from ..rag.retriever import index_document

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("")
def ingest(req: IngestRequest, db: Session = Depends(get_db)):
    chunks = chunk_text(req.text)
    count = index_document(db, req.source, chunks)
    return {"source": req.source, "chunks_indexed": count}
