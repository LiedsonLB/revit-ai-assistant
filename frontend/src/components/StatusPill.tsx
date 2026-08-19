interface StatusPillProps {
  label: string;
  tone?: "idle" | "active" | "warn";
}

const TONE_STYLES: Record<NonNullable<StatusPillProps["tone"]>, string> = {
  idle: "bg-slate-500",
  active: "bg-cyan-glow shadow-[0_0_6px_2px_rgba(79,216,255,0.6)]",
  warn: "bg-amber-flag shadow-[0_0_6px_2px_rgba(255,180,84,0.5)]",
};

export default function StatusPill({ label, tone = "idle" }: StatusPillProps) {
  return (
    <div className="flex items-center gap-2 text-[11px] font-mono uppercase tracking-wider text-slate-400">
      <span className={`h-1.5 w-1.5 rounded-full ${TONE_STYLES[tone]}`} />
      {label}
    </div>
  );
}
