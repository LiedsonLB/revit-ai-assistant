import { useMemo, useState } from "react";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";

export default function App() {
  const sessionId = useMemo(() => crypto.randomUUID(), []);
  const [toolCallCount, setToolCallCount] = useState(0);

  return (
    <div className="relative flex h-screen w-screen overflow-hidden bg-blueprint-950">
      <div className="pointer-events-none absolute inset-0 bg-blueprint-grid bg-grid opacity-60" />

      {/* marcas de registro, tipo prancheta técnica */}
      <Crosshair className="left-4 top-4" />
      <Crosshair className="right-4 top-4" />
      <Crosshair className="bottom-4 left-4" />
      <Crosshair className="bottom-4 right-4" />

      <div className="relative flex h-full w-full">
        <Sidebar sessionId={sessionId} toolCallCount={toolCallCount} />
        <ChatWindow sessionId={sessionId} onToolCall={() => setToolCallCount((n) => n + 1)} />
      </div>
    </div>
  );
}

function Crosshair({ className }: { className: string }) {
  return (
    <svg
      viewBox="0 0 20 20"
      className={`pointer-events-none absolute h-5 w-5 stroke-cyan-glow/25 ${className}`}
      fill="none"
      strokeWidth="1"
    >
      <path d="M10 0v20M0 10h20" />
    </svg>
  );
}
