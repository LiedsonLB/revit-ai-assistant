import type { ChatResponse } from "../types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export async function sendChatMessage(sessionId: string, message: string): Promise<ChatResponse> {
  const response = await fetch(`${API_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: sessionId, message }),
  });

  if (!response.ok) {
    throw new Error(`Falha ao consultar o agente (HTTP ${response.status})`);
  }

  return response.json();
}
