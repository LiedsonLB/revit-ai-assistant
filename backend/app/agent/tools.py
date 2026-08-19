"""
Definição das tools do agente + dispatcher que as executa.

Duas famílias:
  - Estruturadas/RAG: consultam Postgres diretamente (rápido, exato).
  - Revit: repassam a chamada para o Add-in C# via revit_bridge.client.
"""
from typing import Any
from sqlalchemy.orm import Session

from ..models import Requirement
from ..rag.retriever import search_documents
from ..revit_bridge.client import RevitBridgeClient

TOOLS: list[dict[str, Any]] = [
    {
        "name": "get_requirement",
        "description": (
            "Consulta os requisitos normativos estruturados de um tipo de ambiente "
            "(área mínima, pé-direito mínimo, número de portas). Use para perguntas "
            "diretas sobre um ambiente específico."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "environment": {
                    "type": "string",
                    "description": "Nome do ambiente, ex: 'sala', 'quarto', 'banheiro'.",
                }
            },
            "required": ["environment"],
        },
    },
    {
        "name": "search_norms",
        "description": (
            "Busca semântica (RAG vetorial) em documentos e normas técnicas indexadas. "
            "Use para perguntas abertas ou conceituais que não mapeiam para um único "
            "campo estruturado, ex: 'requisitos para ambientes de permanência prolongada'."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Pergunta em linguagem natural."},
                "top_k": {"type": "integer", "description": "Quantos trechos retornar.", "default": 5},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_levels",
        "description": "Retorna os níveis (pavimentos) do projeto Revit atualmente aberto.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "create_wall",
        "description": "Cria uma parede no modelo Revit ativo.",
        "input_schema": {
            "type": "object",
            "properties": {
                "level": {"type": "string", "description": "Nome do nível onde a parede será criada."},
                "start": {
                    "type": "object",
                    "properties": {"x": {"type": "number"}, "y": {"type": "number"}},
                    "required": ["x", "y"],
                },
                "end": {
                    "type": "object",
                    "properties": {"x": {"type": "number"}, "y": {"type": "number"}},
                    "required": ["x", "y"],
                },
                "height": {"type": "number", "description": "Altura da parede em metros."},
                "wall_type": {"type": "string", "description": "Nome do tipo de parede no projeto."},
            },
            "required": ["level", "start", "end", "height"],
        },
    },
    {
        "name": "create_room",
        "description": "Cria/identifica um ambiente (room) no modelo Revit em um ponto do nível informado.",
        "input_schema": {
            "type": "object",
            "properties": {
                "level": {"type": "string"},
                "point": {
                    "type": "object",
                    "properties": {"x": {"type": "number"}, "y": {"type": "number"}},
                    "required": ["x", "y"],
                },
                "name": {"type": "string", "description": "Nome/rótulo do ambiente."},
            },
            "required": ["level", "point"],
        },
    },
]


class ToolExecutor:
    """Executa uma tool pelo nome, roteando para SQL/RAG local ou para o bridge do Revit."""

    def __init__(self, db: Session):
        self.db = db
        self.bridge = RevitBridgeClient()

    def run(self, name: str, tool_input: dict[str, Any]) -> Any:
        handler = getattr(self, f"_tool_{name}", None)
        if handler is None:
            return {"error": f"tool desconhecida: {name}"}
        return handler(**tool_input)

    # ── Estruturado ──────────────────────────────────────────────
    def _tool_get_requirement(self, environment: str) -> dict[str, Any]:
        req = (
            self.db.query(Requirement)
            .filter(Requirement.environment.ilike(environment))
            .first()
        )
        if not req:
            return {"found": False, "environment": environment}
        return {
            "found": True,
            "environment": req.environment,
            "area_min": float(req.area_min) if req.area_min is not None else None,
            "height_min": float(req.height_min) if req.height_min is not None else None,
            "doors": req.doors,
            "extra": req.extra or {},
        }

    # ── RAG vetorial ────────────────────────────────────────────
    def _tool_search_norms(self, query: str, top_k: int = 5) -> dict[str, Any]:
        results = search_documents(self.db, query, top_k=top_k)
        return {
            "results": [
                {"source": r.source, "content": r.content, "score": r.score} for r in results
            ]
        }

    # ── Revit (via bridge C#) ───────────────────────────────────
    def _tool_get_levels(self) -> Any:
        return self.bridge.post("get_levels", {})

    def _tool_create_wall(self, **kwargs) -> Any:
        return self.bridge.post("create_wall", kwargs)

    def _tool_create_room(self, **kwargs) -> Any:
        return self.bridge.post("create_room", kwargs)
