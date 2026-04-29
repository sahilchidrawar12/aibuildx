using System;
using System.Collections.Generic;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Autodesk.Revit.DB;
using Autodesk.Revit.UI;
using Newtonsoft.Json;

namespace RevitStructures.AIBuildX
{
    /// <summary>
    /// Placeholder architecture for a Revit WebSocket bridge.
    /// This class is intended to run inside a Revit add-in and communicate with the Python API server.
    /// </summary>
    public class RevitWebSocketBridge : IExternalEventHandler, IDisposable
    {
        private readonly UIApplication _uiApp;
        private ClientWebSocket _webSocket;
        private readonly Uri _serverUri;
        private readonly CancellationTokenSource _cts;
        private bool _isConnected;

        private const string SERVER_URL = "ws://localhost:8000/ws/revit";
        private const int RECONNECT_DELAY_MS = 5000;

        public RevitWebSocketBridge(UIApplication uiApp)
        {
            _uiApp = uiApp ?? throw new ArgumentNullException(nameof(uiApp));
            _serverUri = new Uri(SERVER_URL);
            _cts = new CancellationTokenSource();
            _isConnected = false;
        }

        public string GetName() => "RevitWebSocketBridge";

        public void Execute(UIApplication app)
        {
            // ExternalEvent execution context for Revit-safe commands
        }

        public async Task StartAsync()
        {
            while (!_cts.Token.IsCancellationRequested)
            {
                try
                {
                    _webSocket = new ClientWebSocket();
                    await _webSocket.ConnectAsync(_serverUri, _cts.Token);
                    _isConnected = true;
                    await SendStatusAsync(true);
                    await ReceiveMessagesAsync();
                }
                catch (Exception)
                {
                    _isConnected = false;
                    await Task.Delay(RECONNECT_DELAY_MS, _cts.Token);
                }
            }
        }

        private async Task ReceiveMessagesAsync()
        {
            var buffer = new byte[4096];
            while (_webSocket.State == WebSocketState.Open && !_cts.Token.IsCancellationRequested)
            {
                var result = await _webSocket.ReceiveAsync(new ArraySegment<byte>(buffer), _cts.Token);
                if (result.MessageType == WebSocketMessageType.Text)
                {
                    var message = Encoding.UTF8.GetString(buffer, 0, result.Count);
                    await ProcessMessageAsync(message);
                }
                else if (result.MessageType == WebSocketMessageType.Close)
                {
                    break;
                }
            }
        }

        private async Task ProcessMessageAsync(string message)
        {
            var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(message);
            if (data == null) return;

            object commandObj;
            data.TryGetValue("command", out commandObj);
            var command = commandObj?.ToString();
            switch (command)
            {
                case "CREATE_OBJECTS":
                    // Schedule Revit-safe object creation using ExternalEvent
                    break;
                case "SYNC_MODEL":
                    await SendModelInfoAsync();
                    break;
                default:
                    break;
            }
        }

        private async Task SendStatusAsync(bool connected)
        {
            var status = new
            {
                type = "status",
                connected = connected,
                timestamp = DateTime.UtcNow.ToString("o")
            };
            await SendMessageAsync(status);
        }

        private async Task SendModelInfoAsync()
        {
            var info = new
            {
                type = "model_info",
                model_name = _uiApp.ActiveUIDocument.Document.Title,
                timestamp = DateTime.UtcNow.ToString("o")
            };
            await SendMessageAsync(info);
        }

        private async Task SendMessageAsync(object message)
        {
            if (!_isConnected || _webSocket.State != WebSocketState.Open) return;
            var json = JsonConvert.SerializeObject(message);
            var buffer = Encoding.UTF8.GetBytes(json);
            await _webSocket.SendAsync(new ArraySegment<byte>(buffer), WebSocketMessageType.Text, true, _cts.Token);
        }

        public void Dispose()
        {
            _cts.Cancel();
            _webSocket?.Dispose();
            _cts.Dispose();
        }
    }
}
