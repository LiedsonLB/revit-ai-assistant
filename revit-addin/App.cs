using Autodesk.Revit.UI;
using RevitBridge.Tools;

namespace RevitBridge
{
    /// <summary>
    /// Ponto de entrada do add-in. Sobe o BridgeServer HTTP e registra o
    /// ExternalEvent usado para executar comandos na thread da Revit API.
    /// </summary>
    public class App : IExternalApplication
    {
        private BridgeServer? _server;
        private ToolExternalEventHandler? _handler;
        private ExternalEvent? _externalEvent;

        public Result OnStartup(UIControlledApplication application)
        {
            _handler = new ToolExternalEventHandler();
            _externalEvent = ExternalEvent.Create(_handler);

            var dispatcher = new ToolDispatcher(application, _handler, _externalEvent);
            _server = new BridgeServer(dispatcher, port: 5005);
            _server.Start();

            return Result.Succeeded;
        }

        public Result OnShutdown(UIControlledApplication application)
        {
            _server?.Stop();
            return Result.Succeeded;
        }
    }
}
