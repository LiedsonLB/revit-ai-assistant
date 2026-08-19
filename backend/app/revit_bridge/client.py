"""
Cliente HTTP que fala com o Add-in C# (Revit Bridge). O add-in expõe um
servidor HTTP local (ver revit-addin/BridgeServer.cs) rodando na mesma
máquina do Revit, com endpoints simples do tipo POST /tools/{tool_name}.
"""
import httpx

from ..config import settings


class RevitBridgeClient:
    def __init__(self):
        self.base_url = settings.revit_bridge_url.rstrip("/")
        self.timeout = settings.revit_bridge_timeout

    def post(self, tool_name: str, payload: dict) -> dict:
        url = f"{self.base_url}/tools/{tool_name}"
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.ConnectError:
            return {
                "error": "revit_bridge_unreachable",
                "message": (
                    f"Não foi possível conectar ao Add-in Revit em {self.base_url}. "
                    "Confirme que o Revit está aberto com o add-in carregado."
                ),
            }
        except httpx.HTTPStatusError as exc:
            return {"error": "revit_bridge_error", "status": exc.response.status_code, "detail": exc.response.text}
