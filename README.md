# Revit AI Assistant

Assistente de IA para Revit com arquitetura híbrida:

- **Python (FastAPI)** — agente de IA, tool calling, RAG híbrido (SQL estruturado + busca vetorial), orquestração.
- **C# (Add-in Revit)** — bridge que expõe a Revit API via HTTP para o backend Python executar comandos (`create_wall`, `get_levels`, etc).
- **PostgreSQL + pgvector** — armazena requisitos normativos estruturados (tabelas) e embeddings de documentos/normas.
- **React + TypeScript + Tailwind** — interface de chat, tema "glass-tech dark" (fundo escuro, cartões com vidro fosco, grade tipo prancheta CAD, acento ciano).

```
┌─────────────┐   Revit API   ┌─────────────┐   HTTP/WS   ┌──────────────────┐
│    Revit    │◄─────────────►│  Add-in C#  │◄───────────►│  Backend Python   │
└─────────────┘                └─────────────┘              │  FastAPI + Agent  │
                                                              │  RAG híbrido      │
                                                              └─────────┬─────────┘
                                                                        │
                                                              ┌─────────▼─────────┐
                                                              │ PostgreSQL+pgvector│
                                                              └────────────────────┘
                                                                        ▲
                                                              ┌─────────┴─────────┐
                                                              │  React frontend    │
                                                              └────────────────────┘
```

## Subir o ambiente (backend + banco + frontend)

```bash
cp .env.example .env
# edite .env e coloque sua ANTHROPIC_API_KEY (ou OPENAI_API_KEY, veja backend/app/config.py)
docker compose up --build
```

- Backend: http://localhost:8000 (docs em `/docs`)
- Frontend: http://localhost:5173
- Postgres: localhost:5432 (usuário/senha em `.env`)

O Revit + add-in C# rodam **fora do Docker**, na máquina Windows com Revit instalado
(veja `revit-addin/README.md`).

## Estrutura

```
revit-ai-assistant/
├── docker-compose.yml
├── db/init.sql                 # schema: requisitos, documentos (pgvector), levels
├── backend/                    # FastAPI
│   └── app/
│       ├── agent/              # LLM + tool calling
│       ├── rag/                # embeddings + retriever híbrido
│       ├── revit_bridge/       # cliente HTTP que fala com o add-in C#
│       ├── api/                # rotas (chat, requirements, ingest)
│       └── scripts/import_excel.py
├── frontend/                   # React + TS + Tailwind (Vite)
└── revit-addin/                # Add-in C# (.NET) — Revit Bridge
```

## Fluxo do agente (hybrid RAG)

1. Usuário pergunta algo no chat React.
2. Backend chama o LLM com um conjunto de *tools*:
   - `get_requirement(environment, field)` → consulta direta no Postgres (dado estruturado).
   - `search_norms(query)` → busca vetorial em `documents` (pgvector).
   - `get_levels()`, `create_wall(...)`, `create_room(...)` → chamadas que o backend repassa
     via HTTP para o Add-in C#, que executa na Revit API.
3. O LLM decide quais tools chamar, o backend executa e devolve o resultado; o LLM formula
   a resposta final (e pode encadear várias chamadas, ex: consultar requisito → consultar
   níveis → criar paredes → criar ambiente).

## Importar suas tabelas (Excel → Postgres)

```bash
docker compose exec backend python scripts/import_excel.py /caminho/requisitos.xlsx requisitos
```

Veja `backend/scripts/import_excel.py` — normaliza colunas e faz upsert na tabela `requirements`.

## Próximos passos sugeridos

- Trocar o stub de autenticação do bridge C# por algo real (API key / mTLS) antes de expor
  fora de `localhost`.
- Adicionar mais `tools` conforme as operações do Revit que você precisar automatizar.
- Trocar `sentence-transformers` (local) por embeddings da Anthropic/OpenAI se preferir não
  baixar modelo local — ponto único de troca em `backend/app/rag/embeddings.py`.
