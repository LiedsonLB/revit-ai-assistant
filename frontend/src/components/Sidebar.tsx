import StatusPill from "./StatusPill";

interface SidebarProps {
  sessionId: string;
  toolCallCount: number;
}

export default function Sidebar({ sessionId, toolCallCount }: SidebarProps) {
  return (
    <aside className="hidden md:flex w-72 shrink-0 flex-col gap-6 border-r border-blueprint-600/40 bg-blueprint-900/60 p-6">
      <div>
        <div className="flex items-center gap-2">
          <div className="grid h-8 w-8 place-items-center rounded-md border border-cyan-glow/30 bg-cyan-glow/10">
            <svg viewBox="0 0 24 24" className="h-4 w-4 stroke-cyan-glow" fill="none" strokeWidth="1.6">
              <path d="M3 21V9l9-6 9 6v12" strokeLinejoin="round" />
              <path d="M9 21V13h6v8" strokeLinejoin="round" />
            </svg>
          </div>
          <div>
            <p className="font-display text-sm font-semibold text-white">Revit AI</p>
            <p className="font-mono text-[10px] uppercase tracking-widest text-slate-500">
              assistente de projeto
            </p>
          </div>
        </div>
      </div>

      <div className="glass rounded-lg p-4">
        <p className="mb-3 font-mono text-[10px] uppercase tracking-widest text-slate-500">
          Conexões
        </p>
        <div className="flex flex-col gap-2.5">
          <StatusPill label="Backend FastAPI" tone="active" />
          <StatusPill label="Postgres + pgvector" tone="active" />
          <StatusPill label="Add-in Revit" tone="warn" />
        </div>
      </div>

      <div className="glass rounded-lg p-4">
        <p className="mb-1 font-mono text-[10px] uppercase tracking-widest text-slate-500">
          Sessão
        </p>
        <p className="truncate font-mono text-xs text-slate-300">{sessionId}</p>
      </div>

      <div className="glass rounded-lg p-4">
        <p className="mb-1 font-mono text-[10px] uppercase tracking-widest text-slate-500">
          Chamadas de ferramenta
        </p>
        <p className="font-mono text-2xl font-semibold text-cyan-glow">{toolCallCount}</p>
      </div>

      <div className="mt-auto text-[10px] font-mono leading-relaxed text-slate-600">
        <p>Hybrid RAG</p>
        <p>SQL estruturado + busca vetorial</p>
        <p>+ Revit API via bridge C#</p>
      </div>
    </aside>
  );
}
