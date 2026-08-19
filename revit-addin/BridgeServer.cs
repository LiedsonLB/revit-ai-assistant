using System;
using System.IO;
using System.Net;
using System.Text;
using System.Text.Json;
using System.Threading;
using RevitBridge.Tools;

namespace RevitBridge
{
    /// <summary>
    /// Servidor HTTP minimalista (HttpListener puro, sem ASP.NET) rodando dentro
    /// do processo do Revit. Escuta POST /tools/{tool_name} e delega para o
    /// ToolDispatcher, que executa via ExternalEvent na thread da Revit API.
    /// </summary>
    public class BridgeServer
    {
        private readonly HttpListener _listener = new HttpListener();
        private readonly ToolDispatcher _dispatcher;
        private Thread? _thread;
        private volatile bool _running;

        public BridgeServer(ToolDispatcher dispatcher, int port)
        {
            _dispatcher = dispatcher;
            _listener.Prefixes.Add($"http://localhost:{port}/");
        }

        public void Start()
        {
            _listener.Start();
            _running = true;
            _thread = new Thread(Listen) { IsBackground = true };
            _thread.Start();
        }

        public void Stop()
        {
            _running = false;
            _listener.Stop();
        }

        private void Listen()
        {
            while (_running)
            {
                try
                {
                    var context = _listener.GetContext(); // bloqueia até uma request chegar
                    ThreadPool.QueueUserWorkItem(_ => HandleRequest(context));
                }
                catch (HttpListenerException)
                {
                    // listener foi parado (Stop()) — sai do loop
                    break;
                }
                catch (ObjectDisposedException)
                {
                    break;
                }
            }
        }

        private void HandleRequest(HttpListenerContext context)
        {
            var request = context.Request;
            var response = context.Response;

            try
            {
                if (request.HttpMethod != "POST" || !request.Url!.AbsolutePath.StartsWith("/tools/"))
                {
                    WriteJson(response, 404, new { error = "not_found" });
                    return;
                }

                var toolName = request.Url.AbsolutePath.Substring("/tools/".Length).Trim('/');

                string body;
                using (var reader = new StreamReader(request.InputStream, Encoding.UTF8))
                    body = reader.ReadToEnd();

                var input = string.IsNullOrWhiteSpace(body)
                    ? JsonDocument.Parse("{}").RootElement
                    : JsonDocument.Parse(body).RootElement;

                // Executa de forma síncrona: o dispatcher dispara o ExternalEvent e
                // aguarda (com timeout) o resultado ser preenchido pela thread do Revit.
                object result = _dispatcher.Execute(toolName, input);
                WriteJson(response, 200, result);
            }
            catch (Exception ex)
            {
                WriteJson(response, 500, new { error = "internal_error", message = ex.Message });
            }
        }

        private static void WriteJson(HttpListenerResponse response, int statusCode, object payload)
        {
            var json = JsonSerializer.Serialize(payload);
            var bytes = Encoding.UTF8.GetBytes(json);

            response.StatusCode = statusCode;
            response.ContentType = "application/json";
            response.ContentLength64 = bytes.Length;
            response.OutputStream.Write(bytes, 0, bytes.Length);
            response.OutputStream.Close();
        }
    }
}
