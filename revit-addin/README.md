# Revit Bridge (Add-in C#)

Add-in que roda dentro do Revit e expõe um servidor HTTP local. O backend Python
(fora do Revit, geralmente em Docker) manda comandos como JSON e este add-in
executa via Revit API, dentro de um `ExternalEvent` (a Revit API só pode ser
chamada na thread principal do Revit).

## Requisitos

- Revit 2024 ou 2025 instalado (ajuste as referências de DLL no `.csproj` para
  a sua versão — o caminho padrão é `C:\Program Files\Autodesk\Revit 2024\`).
- .NET 8 SDK (ou a versão de target framework exigida pela sua versão do Revit).

## Build

```powershell
dotnet build RevitBridge.csproj -c Release
```

Copie o `.addin` resultante e a DLL para:
`%APPDATA%\Autodesk\Revit\Addins\2024\`

## Como funciona

1. `App.cs` — ponto de entrada do add-in (`IExternalApplication`). No `OnStartup`,
   inicia o `BridgeServer` (HttpListener numa thread separada) e registra um
   `ExternalEvent` para executar código com acesso à Revit API.
2. `BridgeServer.cs` — servidor HTTP minimalista (`HttpListener`, sem dependências
   externas) escutando em `http://localhost:5005/tools/{tool_name}`. Recebe o
   JSON do backend Python, enfileira a execução no `ExternalEvent` e devolve o
   resultado.
3. `Tools/ToolDispatcher.cs` — roteia `tool_name` → método concreto
   (`get_levels`, `create_wall`, `create_room`, ...), espelhando exatamente os
   nomes/schemas definidos em `backend/app/agent/tools.py`.
4. `Commands/CreateWallCommand.cs` — exemplo de como um comando efetivamente usa
   a Revit API (`Wall.Create(...)`).

## Segurança

Este é um scaffold de desenvolvimento: o `BridgeServer` escuta em `localhost`
sem autenticação. Antes de expor fora da própria máquina, adicione um header
de API key (comparando com um valor do `.env` do backend) e considere rodar
atrás de um túnel (ex: Tailscale) em vez de abrir a porta na rede.
