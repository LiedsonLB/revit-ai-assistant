export type Role = "user" | "assistant";

export interface ToolCallLog {
  name: string;
  input: Record<string, unknown>;
  result: unknown;
}

export interface ChatMessage {
  id: string;
  role: Role;
  content: string;
  toolCalls?: ToolCallLog[];
  pending?: boolean;
}

export interface ChatResponse {
  session_id: string;
  reply: string;
  tool_calls: ToolCallLog[];
}
