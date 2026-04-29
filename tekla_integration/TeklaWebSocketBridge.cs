using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.WebSockets;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using Tekla.Structures.Model;
using Tekla.Structures.Geometry3d;
using Newtonsoft.Json;

namespace TeklaStructures.AIBuildX
{
    /// <summary>
    /// Real-time WebSocket bridge between Tekla Structures and Python API server
    /// </summary>
    public class TeklaWebSocketBridge : IDisposable
    {
        private readonly Model _model;
        private readonly Events _events;
        private ClientWebSocket _webSocket;
        private readonly Uri _serverUri;
        private readonly CancellationTokenSource _cts;
        private bool _isConnected;
        private readonly object _lock = new object();

        // Configuration
        private const string SERVER_URL = "ws://localhost:8000/ws/tekla";
        private const int RECONNECT_DELAY_MS = 5000;
        private const int HEARTBEAT_INTERVAL_MS = 30000;

        public TeklaWebSocketBridge()
        {
            _model = new Model();
            _events = new Events();
            _serverUri = new Uri(SERVER_URL);
            _cts = new CancellationTokenSource();
            _isConnected = false;

            if (!_model.GetConnectionStatus())
            {
                throw new InvalidOperationException("Failed to connect to Tekla Structures");
            }

            SetupEventHandlers();
        }

        /// <summary>
        /// Start the WebSocket bridge
        /// </summary>
        public async Task StartAsync()
        {
            Console.WriteLine("Starting Tekla WebSocket Bridge...");

            // Register Tekla events
            _events.Register();

            // Start WebSocket connection
            await ConnectWebSocketAsync();

            // Start heartbeat
            _ = Task.Run(() => SendHeartbeatAsync(_cts.Token));

            Console.WriteLine("Tekla WebSocket Bridge started successfully");
        }

        /// <summary>
        /// Stop the WebSocket bridge
        /// </summary>
        public async Task StopAsync()
        {
            Console.WriteLine("Stopping Tekla WebSocket Bridge...");

            _cts.Cancel();
            _events.UnRegister();

            if (_webSocket != null)
            {
                await _webSocket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Bridge stopping", CancellationToken.None);
            }

            _isConnected = false;
            Console.WriteLine("Tekla WebSocket Bridge stopped");
        }

        private void SetupEventHandlers()
        {
            // Model object changes
            _events.ModelObjectChanged += async (changes) =>
            {
                await SendModelUpdateAsync(changes);
            };

            // Selection changes
            _events.SelectionChange += async () =>
            {
                await SendSelectionUpdateAsync();
            };

            // Model changes
            _events.ModelChanged += async () =>
            {
                await SendModelChangedAsync();
            };

            // Clash detection
            _events.ClashDetected += async (clashData) =>
            {
                await SendClashUpdateAsync(clashData);
            };
        }

        private async Task ConnectWebSocketAsync()
        {
            while (!_cts.Token.IsCancellationRequested)
            {
                try
                {
                    _webSocket = new ClientWebSocket();
                    await _webSocket.ConnectAsync(_serverUri, _cts.Token);

                    _isConnected = true;
                    Console.WriteLine("Connected to Python API server");

                    // Send initial status
                    await SendStatusUpdateAsync(true);

                    // Start receiving messages
                    await ReceiveMessagesAsync();

                }
                catch (Exception ex)
                {
                    Console.WriteLine($"WebSocket connection failed: {ex.Message}");
                    _isConnected = false;

                    if (!_cts.Token.IsCancellationRequested)
                    {
                        await Task.Delay(RECONNECT_DELAY_MS, _cts.Token);
                    }
                }
            }
        }

        private async Task ReceiveMessagesAsync()
        {
            var buffer = new byte[4096];

            try
            {
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
            catch (Exception ex)
            {
                Console.WriteLine($"Error receiving WebSocket message: {ex.Message}");
            }
            finally
            {
                _isConnected = false;
                await SendStatusUpdateAsync(false);
            }
        }

        private async Task ProcessMessageAsync(string message)
        {
            try
            {
                var data = JsonConvert.DeserializeObject<Dictionary<string, object>>(message);
                var command = data.GetValueOrDefault("command")?.ToString();

                switch (command)
                {
                    case "CREATE_OBJECTS":
                        await CreateObjectsAsync(data);
                        break;

                    case "SYNC_MODEL":
                        await SyncModelAsync();
                        break;

                    case "GET_MODEL_INFO":
                        await SendModelInfoAsync();
                        break;

                    default:
                        Console.WriteLine($"Unknown command: {command}");
                        break;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error processing message: {ex.Message}");
            }
        }

        private async Task CreateObjectsAsync(Dictionary<string, object> data)
        {
            var transactionId = data.GetValueOrDefault("transaction_id")?.ToString();
            var objects = data.GetValueOrDefault("objects") as Newtonsoft.Json.Linq.JArray;

            if (objects == null) return;

            var createdObjects = new List<Dictionary<string, object>>();

            using (var transaction = new Transaction(_model))
            {
                transaction.Start();

                try
                {
                    foreach (var obj in objects)
                    {
                        var objData = obj.ToObject<Dictionary<string, object>>();
                        var createdObj = await CreateSingleObjectAsync(objData);
                        if (createdObj != null)
                        {
                            createdObjects.Add(createdObj);
                        }
                    }

                    transaction.Commit();

                    // Send success response
                    var response = new
                    {
                        type = "command_response",
                        command = "CREATE_OBJECTS",
                        transaction_id = transactionId,
                        success = true,
                        created_objects = createdObjects,
                        timestamp = DateTime.UtcNow.ToString("o")
                    };

                    await SendMessageAsync(response);

                }
                catch (Exception ex)
                {
                    transaction.RollBack();

                    var errorResponse = new
                    {
                        type = "command_response",
                        command = "CREATE_OBJECTS",
                        transaction_id = transactionId,
                        success = false,
                        error = ex.Message,
                        timestamp = DateTime.UtcNow.ToString("o")
                    };

                    await SendMessageAsync(errorResponse);
                }
            }
        }

        private async Task<Dictionary<string, object>> CreateSingleObjectAsync(Dictionary<string, object> objData)
        {
            var type = objData.GetValueOrDefault("type")?.ToString();

            switch (type)
            {
                case "beam":
                    return CreateBeam(objData);

                case "column":
                    return CreateColumn(objData);

                case "plate":
                    return CreatePlate(objData);

                case "bolt_group":
                    return CreateBoltGroup(objData);

                default:
                    Console.WriteLine($"Unknown object type: {type}");
                    return null;
            }
        }

        private Dictionary<string, object> CreateBeam(Dictionary<string, object> data)
        {
            try
            {
                var startPoint = GetPoint(data, "start_point");
                var endPoint = GetPoint(data, "end_point");
                var profile = data.GetValueOrDefault("profile")?.ToString() ?? "HEA200";
                var material = data.GetValueOrDefault("material")?.ToString() ?? "S235JR";

                var beam = new Beam(startPoint, endPoint)
                {
                    Profile = { ProfileString = profile },
                    Material = { MaterialString = material },
                    Name = data.GetValueOrDefault("name")?.ToString() ?? $"Beam_{Guid.NewGuid().ToString().Substring(0, 8)}"
                };

                beam.Insert();

                return new Dictionary<string, object>
                {
                    ["id"] = beam.Identifier.GUID.ToString(),
                    ["type"] = "beam",
                    ["name"] = beam.Name,
                    ["profile"] = profile,
                    ["material"] = material
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error creating beam: {ex.Message}");
                return null;
            }
        }

        private Dictionary<string, object> CreateColumn(Dictionary<string, object> data)
        {
            try
            {
                var startPoint = GetPoint(data, "start_point");
                var endPoint = GetPoint(data, "end_point");
                var profile = data.GetValueOrDefault("profile")?.ToString() ?? "HEA200";
                var material = data.GetValueOrDefault("material")?.ToString() ?? "S235JR";

                var column = new Column(startPoint, endPoint)
                {
                    Profile = { ProfileString = profile },
                    Material = { MaterialString = material },
                    Name = data.GetValueOrDefault("name")?.ToString() ?? $"Column_{Guid.NewGuid().ToString().Substring(0, 8)}"
                };

                column.Insert();

                return new Dictionary<string, object>
                {
                    ["id"] = column.Identifier.GUID.ToString(),
                    ["type"] = "column",
                    ["name"] = column.Name,
                    ["profile"] = profile,
                    ["material"] = material
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error creating column: {ex.Message}");
                return null;
            }
        }

        private Dictionary<string, object> CreatePlate(Dictionary<string, object> data)
        {
            try
            {
                var vertices = data.GetValueOrDefault("vertices") as Newtonsoft.Json.Linq.JArray;
                var thickness = Convert.ToDouble(data.GetValueOrDefault("thickness") ?? 10.0);
                var material = data.GetValueOrDefault("material")?.ToString() ?? "S235JR";

                if (vertices == null || vertices.Count < 3) return null;

                var contourPlate = new ContourPlate
                {
                    Name = data.GetValueOrDefault("name")?.ToString() ?? $"Plate_{Guid.NewGuid().ToString().Substring(0, 8)}",
                    Material = { MaterialString = material }
                };

                // Add contour points
                foreach (var vertex in vertices)
                {
                    var pointData = vertex.ToObject<List<double>>();
                    if (pointData.Count >= 3)
                    {
                        var point = new Point(pointData[0], pointData[1], pointData[2]);
                        contourPlate.AddContourPoint(new ContourPoint(point, ContourPointType.PolyPoint));
                    }
                }

                contourPlate.Insert();

                return new Dictionary<string, object>
                {
                    ["id"] = contourPlate.Identifier.GUID.ToString(),
                    ["type"] = "plate",
                    ["name"] = contourPlate.Name,
                    ["material"] = material,
                    ["thickness"] = thickness
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error creating plate: {ex.Message}");
                return null;
            }
        }

        private Dictionary<string, object> CreateBoltGroup(Dictionary<string, object> data)
        {
            try
            {
                var position = GetPoint(data, "position");
                var boltStandard = data.GetValueOrDefault("bolt_standard")?.ToString() ?? "UNC";
                var boltSize = data.GetValueOrDefault("bolt_size")?.ToString() ?? "3/4";
                var boltCount = Convert.ToInt32(data.GetValueOrDefault("bolt_count") ?? 4);

                var boltGroup = new BoltGroup
                {
                    BoltStandard = boltStandard,
                    BoltSize = boltSize,
                    BoltCount = boltCount
                };

                boltGroup.Insert();

                return new Dictionary<string, object>
                {
                    ["id"] = boltGroup.Identifier.GUID.ToString(),
                    ["type"] = "bolt_group",
                    ["bolt_standard"] = boltStandard,
                    ["bolt_size"] = boltSize,
                    ["bolt_count"] = boltCount
                };
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error creating bolt group: {ex.Message}");
                return null;
            }
        }

        private Point GetPoint(Dictionary<string, object> data, string key)
        {
            var pointData = data.GetValueOrDefault(key) as Newtonsoft.Json.Linq.JArray;
            if (pointData != null && pointData.Count >= 3)
            {
                return new Point(
                    pointData[0].ToObject<double>(),
                    pointData[1].ToObject<double>(),
                    pointData[2].ToObject<double>()
                );
            }
            return new Point(0, 0, 0);
        }

        private async Task SendModelUpdateAsync(List<ChangeData> changes)
        {
            var modelChanges = changes.Select(c => new
            {
                change_type = c.Type.ToString(),
                object_id = c.Object.Identifier.GUID.ToString(),
                object_type = c.Object.GetType().Name,
                timestamp = DateTime.UtcNow.ToString("o"),
                source = c.ChangeSourceType.ToString()
            }).ToList();

            var update = new
            {
                type = "model_update",
                changes = modelChanges,
                model_name = _model.GetInfo().ModelName,
                total_objects = GetModelObjectCount(),
                timestamp = DateTime.UtcNow.ToString("o")
            };

            await SendMessageAsync(update);
        }

        private async Task SendSelectionUpdateAsync()
        {
            var update = new
            {
                type = "selection_update",
                selected_objects = GetSelectedObjectIds(),
                timestamp = DateTime.UtcNow.ToString("o")
            };

            await SendMessageAsync(update);
        }

        private async Task SendModelChangedAsync()
        {
            var update = new
            {
                type = "model_changed",
                model_name = _model.GetInfo().ModelName,
                timestamp = DateTime.UtcNow.ToString("o")
            };

            await SendMessageAsync(update);
        }

        private async Task SendClashUpdateAsync(object clashData)
        {
            var update = new
            {
                type = "clash_update",
                clash_data = clashData,
                timestamp = DateTime.UtcNow.ToString("o")
            };

            await SendMessageAsync(update);
        }

        private async Task SendStatusUpdateAsync(bool connected)
        {
            var status = new
            {
                type = "status",
                connected = connected,
                tekla_version = GetTeklaVersion(),
                model_name = _model.GetInfo().ModelName,
                timestamp = DateTime.UtcNow.ToString("o")
            };

            await SendMessageAsync(status);
        }

        private async Task SendModelInfoAsync()
        {
            var info = new
            {
                type = "model_info",
                model_name = _model.GetInfo().ModelName,
                total_objects = GetModelObjectCount(),
                object_breakdown = GetObjectBreakdown(),
                timestamp = DateTime.UtcNow.ToString("o")
            };

            await SendMessageAsync(info);
        }

        private async Task SyncModelAsync()
        {
            _model.CommitChanges();

            var syncResponse = new
            {
                type = "sync_complete",
                model_name = _model.GetInfo().ModelName,
                total_objects = GetModelObjectCount(),
                timestamp = DateTime.UtcNow.ToString("o")
            };

            await SendMessageAsync(syncResponse);
        }

        private async Task SendHeartbeatAsync(CancellationToken token)
        {
            while (!token.IsCancellationRequested)
            {
                if (_isConnected)
                {
                    var heartbeat = new
                    {
                        type = "heartbeat",
                        timestamp = DateTime.UtcNow.ToString("o")
                    };

                    await SendMessageAsync(heartbeat);
                }

                await Task.Delay(HEARTBEAT_INTERVAL_MS, token);
            }
        }

        public async Task SendEventAsync(string eventType, object payload)
        {
            var message = new Dictionary<string, object>
            {
                ["type"] = eventType,
                ["payload"] = payload,
                ["timestamp"] = DateTime.UtcNow.ToString("o")
            };

            await SendMessageAsync(message);
        }

        private async Task SendMessageAsync(object message)
        {
            if (!_isConnected || _webSocket.State != WebSocketState.Open) return;

            try
            {
                var json = JsonConvert.SerializeObject(message);
                var buffer = Encoding.UTF8.GetBytes(json);

                await _webSocket.SendAsync(new ArraySegment<byte>(buffer), WebSocketMessageType.Text, true, _cts.Token);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error sending message: {ex.Message}");
                _isConnected = false;
            }
        }

        private List<string> GetSelectedObjectIds()
        {
            var selector = new Tekla.Structures.Model.UI.ModelObjectSelector();
            var selected = new List<string>();
            var enumerator = selector.GetSelectedObjects();
            while (enumerator.MoveNext())
            {
                if (enumerator.Current is ModelObject obj)
                {
                    selected.Add(obj.Identifier.GUID.ToString());
                }
            }
            return selected;
        }

        private int GetModelObjectCount()
        {
            var enumerator = _model.GetObjects(typeof(ModelObject));
            return enumerator.GetSize();
        }

        private Dictionary<string, int> GetObjectBreakdown()
        {
            var breakdown = new Dictionary<string, int>();
            var enumerator = _model.GetObjects(typeof(ModelObject));
            while (enumerator.MoveNext())
            {
                if (enumerator.Current is ModelObject obj)
                {
                    var typeName = obj.GetType().Name;
                    if (breakdown.ContainsKey(typeName))
                    {
                        breakdown[typeName]++;
                    }
                    else
                    {
                        breakdown[typeName] = 1;
                    }
                }
            }
            return breakdown;
        }

        private string GetTeklaVersion()
        {
            try
            {
                return Tekla.Structures.Info.TeklaVersion.ToString();
            }
            catch
            {
                return "Unknown";
            }
        }

        public void Dispose()
        {
            _cts?.Cancel();
            _cts?.Dispose();
            _webSocket?.Dispose();
            _events?.UnRegister();
        }
    }
}