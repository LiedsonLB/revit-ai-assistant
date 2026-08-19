import type { ChatMessage } from "../types";

interface MessageBubbleProps {
  message: ChatMessage;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`flex max-w-[80%] flex-col gap-2 ${isUser ? "items-end" : "items-start"}`}>
        <div
          className={
            isUser
              ? "rounded-2xl rounded-br-sm bg-cyan-glow/10 border border-cyan-glow/25 px-4 py-3 text-sm text-slate-100"
              : "glass rounded-2xl rounded-bl-sm px-4 py-3 text-sm text-slate-200 shadow-glow"
          }
        >
          {message.pending ? (
            <span className="inline-flex items-center gap-1.5 font-mono text-xs text-slate-400">
              <Dot delay="0ms" />
              <Dot delay="150ms" />
              <Dot delay="300ms" />
              processando
            </span>
          ) : (
            <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
          )}
        </div>

        {message.toolCalls && message.toolCalls.length > 0 && (
          <div className="flex flex-wrap gap-1.5">
            {message.toolCalls.map((call, i) => (
              <span
                key={i}
                className="rounded-full border border-blueprint-600 bg-blueprint-800/80 px-2.5 py-1 font-mono text-[10px] uppercase tracking-wider text-cyan-soft"
                title={JSON.stringify(call.result)}
              >
                {call.name}()
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function Dot({ delay }: { delay: string }) {
  return (
    <span
      className="h-1 w-1 animate-bounce rounded-full bg-cyan-glow"
      style={{ animationDelay: delay }}
    />
  );
}
