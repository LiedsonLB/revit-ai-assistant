"""
Loop do agente: manda a mensagem + tools para o LLM, executa as tools que
ele pedir, devolve o resultado, e repete até o LLM parar de pedir tools
(stop_reason != "tool_use") ou até MAX_STEPS por segurança.
"""
from sqlalchemy.orm import Session

from ..schemas import ChatResponse, ToolCallLog
from .llm_client import LLMClient
from .tools import TOOLS, ToolExecutor

SYSTEM_PROMPT = """\
Você é um assistente de IA especializado em projetos de arquitetura no Revit.
Você tem acesso a ferramentas para:
  1. Consultar requisitos normativos estruturados (get_requirement) — use para
     perguntas diretas e objetivas sobre um ambiente específico.
  2. Buscar em normas/documentos técnicos (search_norms) — use para perguntas
     mais abertas ou conceituais.
  3. Consultar e modificar o modelo Revit ativo (get_levels, create_wall,
     create_room) — use quando o usuário pedir para criar, analisar ou alterar
     elementos do projeto.

Sempre prefira a ferramenta mais específica disponível. Encadeie chamadas quando
necessário (ex: primeiro consultar o requisito de área, depois os níveis do
projeto, depois criar as paredes). Responda sempre em português do Brasil, de
forma direta e técnica. Se uma ferramenta retornar erro de conexão com o Revit,
explique isso claramente ao usuário em vez de inventar um resultado.
"""

MAX_STEPS = 6

# NOTA: o encadeamento multi-turno abaixo (messages.append com result.raw.content)
# usa o formato de blocos da Anthropic. Com LLM_PROVIDER=openai a primeira chamada
# funciona normalmente, mas para reaproveitar o loop completo adapte _stringify/
# messages.append para o formato de "assistant" + "tool" messages da OpenAI
# (veja https://platform.openai.com/docs/guides/function-calling).


def run_agent(db: Session, session_id: str, user_message: str) -> ChatResponse:
    llm = LLMClient()
    executor = ToolExecutor(db)

    messages: list[dict] = [{"role": "user", "content": user_message}]
    tool_log: list[ToolCallLog] = []

    for _ in range(MAX_STEPS):
        result = llm.call(system=SYSTEM_PROMPT, messages=messages, tools=TOOLS)

        if result.stop_reason != "tool_use" or not result.tool_calls:
            return ChatResponse(session_id=session_id, reply=result.text, tool_calls=tool_log)

        # Anexa a resposta do assistant (incluindo os blocos de tool_use) e
        # os resultados de cada tool, no formato que a Anthropic API espera.
        messages.append({"role": "assistant", "content": result.raw.content})

        tool_results = []
        for call in result.tool_calls:
            output = executor.run(call.name, call.input)
            tool_log.append(ToolCallLog(name=call.name, input=call.input, result=output))
            tool_results.append(
                {
                    "type": "tool_result",
                    "tool_use_id": call.id,
                    "content": _stringify(output),
                }
            )
        messages.append({"role": "user", "content": tool_results})

    return ChatResponse(
        session_id=session_id,
        reply="Atingi o limite de passos de raciocínio para esta pergunta. Pode reformular ou dividir em partes?",
        tool_calls=tool_log,
    )


def _stringify(value) -> str:
    import json
    return json.dumps(value, ensure_ascii=False, default=str)
