import { useEffect, useRef, useState } from "react";
import type { ChatMessage } from "../types";
import { sendChatMessage } from "../api/client";
import MessageBubble from "./MessageBubble";

const SUGGESTIONS = [
  "Qual a área mínima de uma sala?",
  "Quais os requisitos para ambientes de permanência prolongada?",
  "Liste os níveis do projeto ativo.",
];

interface ChatWindowProps {
  sessionId: string;
  onToolCall: () => void;
}

export default function ChatWindow({ sessionId, onToolCall }: ChatWindowProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Pronto. Posso consultar requisitos normativos, buscar em normas técnicas, ou " +
        "criar/analisar elementos no modelo Revit ativo (paredes, ambientes, níveis). " +
        "O que você precisa?",
    },
  ]);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages]);

  async function handleSend(text?: string) {
    const content = (text ?? input).trim();
    if (!content || isSending) return;

    const userMessage: ChatMessage = { id: crypto.randomUUID(), role: "user", content };
    const pendingId = crypto.randomUUID();

    setMessages((prev) => [
      ...prev,
      userMessage,
      { id: pendingId, role: "assistant", content: "", pending: true },
    ]);
    setInput("");
    setIsSending(true);

    try {
      const response = await sendChatMessage(sessionId, content);
      if (response.tool_calls?.length) onToolCall();

      setMessages((prev) =>
        prev.map((m) =>
          m.id === pendingId
            ? { ...m, content: response.reply, toolCalls: response.tool_calls, pending: false }
            : m
        )
      );
    } catch (err) {
      setMessages((prev) =>
        prev.map((m) =>
          m.id === pendingId
            ? {
                ...m,
                pending: false,
                content:
                  "Não consegui falar com o backend. Confirme que o serviço FastAPI está " +
                  "rodando (docker compose up) e que a VITE_API_URL está correta.",
              }
            : m
        )
      );
    } finally {
      setIsSending(false);
    }
  }

  return (
    <div className="flex h-full flex-1 flex-col">
      <header className="border-b border-blueprint-600/40 px-6 py-4">
        <h1 className="font-display text-base font-semibold text-white">Assistente de Projeto</h1>
        <p className="font-mono text-[11px] text-slate-500">
          hybrid RAG · tool calling · Revit API
        </p>
      </header>

      <div ref={scrollRef} className="scrollbar-thin flex-1 overflow-y-auto px-6 py-6">
        <div className="mx-auto flex max-w-2xl flex-col gap-4">
          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}

          {messages.length === 1 && (
            <div className="mt-2 flex flex-wrap gap-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => handleSend(s)}
                  className="rounded-full border border-blueprint-600 px-3 py-1.5 font-mono text-xs text-slate-400 transition hover:border-cyan-glow/40 hover:text-cyan-soft"
                >
                  {s}
                </button>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="border-t border-blueprint-600/40 p-4">
        <div className="mx-auto flex max-w-2xl items-end gap-2 rounded-xl glass px-3 py-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Pergunte sobre requisitos, normas, ou peça uma ação no Revit…"
            rows={1}
            className="max-h-32 flex-1 resize-none bg-transparent px-2 py-2 text-sm text-slate-100 placeholder:text-slate-600 focus:outline-none"
          />
          <button
            onClick={() => handleSend()}
            disabled={isSending || !input.trim()}
            className="grid h-9 w-9 shrink-0 place-items-center rounded-lg bg-cyan-glow/15 border border-cyan-glow/30 text-cyan-glow transition hover:bg-cyan-glow/25 disabled:opacity-30 disabled:hover:bg-cyan-glow/15"
            aria-label="Enviar mensagem"
          >
            <svg viewBox="0 0 24 24" className="h-4 w-4" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M5 12h14M13 6l6 6-6 6" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
