from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import chat, requirements, ingest

app = FastAPI(title="Revit AI Assistant", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrinja em produção
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(requirements.router)
app.include_router(ingest.router)


@app.get("/health")
def health():
    return {"status": "ok"}
