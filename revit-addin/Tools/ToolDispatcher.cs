using System;
using System.Text.Json;
using System.Threading;
using Autodesk.Revit.UI;

namespace RevitBridge.Tools
{
    /// <summary>
    /// Handler do ExternalEvent: guarda qual tool/input deve ser executado, e o
    /// Revit chama Execute() na thread principal quando o evento é sinalizado.
    /// </summary>
    public class ToolExternalEventHandler : IExternalEventHandler
    {
        private string _pendingTool = "";
        private JsonElement _pendingInput;
        private readonly ManualResetEventSlim _done = new ManualResetEventSlim(false);
        private object _result = new { };

        public void Request(string toolName, JsonElement input)
        {
            _pendingTool = toolName;
            _pendingInput = input;
            _done.Reset();
        }

        public object WaitForResult(int timeoutMs)
        {
            _done.Wait(timeoutMs);
            return _result;
        }

        public void Execute(UIApplication app)
        {
            try
            {
                _result = _pendingTool switch
                {
                    "get_levels" => GeometryTools.GetLevels(app),
                    "create_wall" => GeometryTools.CreateWall(app, _pendingInput),
                    "create_room" => GeometryTools.CreateRoom(app, _pendingInput),
                    _ => new { error = "unknown_tool", tool = _pendingTool },
                };
            }
            catch (Exception ex)
            {
                _result = new { error = "revit_execution_error", message = ex.Message };
            }
            finally
            {
                _done.Set();
            }
        }

        public string GetName() => "RevitBridgeToolHandler";
    }

    /// <summary>
    /// Ponte entre o servidor HTTP (thread arbitrária do ThreadPool) e o
    /// ExternalEvent (que só executa na thread principal do Revit).
    /// </summary>
    public class ToolDispatcher
    {
        private readonly ToolExternalEventHandler _handler;
        private readonly ExternalEvent _externalEvent;
        private const int TimeoutMs = 15000;

        public ToolDispatcher(UIControlledApplication app, ToolExternalEventHandler handler, ExternalEvent externalEvent)
        {
            _handler = handler;
            _externalEvent = externalEvent;
        }

        public object Execute(string toolName, JsonElement input)
        {
            _handler.Request(toolName, input);
            _externalEvent.Raise();
            return _handler.WaitForResult(TimeoutMs);
        }
    }
}
