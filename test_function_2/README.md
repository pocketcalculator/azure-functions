# Azure Function - Event Hub to Cosmos DB Integration

This Azure Function listens to Event Hub messages and automatically adds them to Cosmos DB. It's designed to process IoT device data and other event-driven data streams.

## Prerequisites

1. **Azure Functions Core Tools**: Install the latest version
   ```bash
   npm install -g azure-functions-core-tools@4 --unsafe-perm true
   ```

2. **Python 3.8+**: Ensure Python is installed
   ```bash
   python --version
   ```

3. **Azure Event Hub**: An existing Event Hub with messages
4. **Azure Cosmos DB**: Same database used by the HTTP function

## Project Structure
```
test_function_2/
├── function_app.py              # Main Event Hub-triggered function
├── host.json                   # Function host configuration
├── local.settings.json         # Local development settings
├── requirements.txt            # Python dependencies
├── sample_eventhub_data.json   # Sample message data
├── .gitignore                 # Git ignore file
└── README.md                  # This file
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configuration
The function is pre-configured with your Event Hub and Cosmos DB settings:

- **Event Hub**: `msfthack2025iothub`
- **Consumer Group**: `$Default`
- **Cosmos DB Database**: `devicesdb`
- **Cosmos DB Container**: `devices`

### 3. Local Development Setup

For local testing, you'll need to use the **Azure Storage Emulator** or **Azurite** for Event Hub checkpointing:

#### Option A: Using Azurite (Recommended)
```bash
# Install Azurite
npm install -g azurite

# Start Azurite
azurite --silent --location c:\\azurite --debug c:\\azurite\\debug.log
```

#### Option B: Using Azure Storage Account
Update `local.settings.json` with a real storage account connection string:
```json
{
  "Values": {
    "AzureWebJobsStorage": "DefaultEndpointsProtocol=https;AccountName=youraccount;AccountKey=yourkey;EndpointSuffix=core.windows.net"
  }
}
```

## Running the Function Locally

1. **Start the function:**
   ```bash
   func start
   ```

2. **The function will automatically:**
   - Connect to the Event Hub
   - Start listening for messages
   - Process messages one at a time
   - Add valid JSON messages to Cosmos DB
   - Log errors for malformed messages

3. **Health check endpoint:**
   - `http://localhost:7071/api/health`

## Message Processing

### Expected Message Format
The function expects JSON messages with this structure:
```json
{
  "id": "unique-device-id",          // Optional - will be generated if missing
  "name": "Device Name",             // Optional - will be generated if missing
  "description": "Device description",
  "category": "device-category",
  "deviceType": "sensor-type",
  "location": "Physical location",
  "data": {
    // Any device-specific data
    "temperature": 22.5,
    "timestamp": "2025-09-18T10:30:00Z"
  }
}
```

### Automatic Enhancements
The function automatically adds:
- **Event Hub metadata**: partition key, sequence number, offset, enqueued time
- **Processing timestamps**: `received_at`, `processed_by`, `source`
- **Generated ID**: If not provided, creates unique ID from Event Hub metadata
- **Generated name**: If not provided, creates descriptive name

### Error Handling
- **Malformed JSON**: Logged to stdout, message skipped
- **Missing required fields**: Auto-generated where possible
- **Cosmos DB conflicts**: Attempts to update existing items
- **Large messages**: Function timeout set to 10 minutes

## Testing the Function

### 1. Monitor Function Logs
Watch the function logs to see message processing:
```bash
func start --verbose
```

### 2. Send Test Messages to Event Hub

#### Using Azure CLI:
```bash
# Send a single message
az eventhubs eventhub send --resource-group your-rg --namespace-name your-namespace --name msfthack2025iothub --messages '[{"id":"test-001","name":"Test Device","data":{"value":123}}]'
```

#### Using Event Hub SDK (Python):
```python
from azure.eventhub import EventHubProducerClient, EventData
import json

connection_str = "your-connection-string"
eventhub_name = "msfthack2025iothub"

producer = EventHubProducerClient.from_connection_string(
    conn_str=connection_str, 
    eventhub_name=eventhub_name
)

# Send sample message
sample_data = {
    "id": "test-device-001",
    "name": "Test Temperature Sensor",
    "category": "sensors",
    "data": {"temperature": 25.5, "humidity": 60.0}
}

with producer:
    event_data_batch = producer.create_batch()
    event_data_batch.add(EventData(json.dumps(sample_data)))
    producer.send_batch(event_data_batch)
```

### 3. Verify Data in Cosmos DB
Check your Cosmos DB container to see the processed messages:
- Azure portal > Cosmos DB > Data Explorer
- Look for items with `"source": "eventhub"`

### 4. Health Check
```bash
curl http://localhost:7071/api/health
```

## Sample Messages

See `sample_eventhub_data.json` for example messages including:
- IoT sensor data (temperature, motion, pressure)
- Vehicle tracking data
- Utility meter readings
- Messages without IDs (auto-generated)
- Examples of malformed messages

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `EVENT_HUB_CONNECTION_STRING` | Event Hub connection string | `Endpoint=sb://...;SharedAccessKey=...;EntityPath=...` |
| `EVENT_HUB_NAME` | Event Hub name | `msfthack2025iothub` |
| `EVENT_HUB_CONSUMER_GROUP` | Consumer group | `$Default` |
| `COSMOS_DB_CONNECTION_STRING` | Cosmos DB connection string | `AccountEndpoint=...;AccountKey=...;` |
| `COSMOS_DB_DATABASE_NAME` | Database name | `devicesdb` |
| `COSMOS_DB_CONTAINER_NAME` | Container name | `devices` |

## Monitoring and Debugging

### Log Analysis
Monitor these log patterns:
- `Successfully added item to Cosmos DB: {id}` - Successful processing
- `Failed to parse JSON message` - Malformed message received
- `Item with id {id} already exists, attempting to update` - Duplicate handling
- `Cosmos DB error for message {id}` - Database issues

### Performance Considerations
- **Processing Mode**: One message at a time (configurable in host.json)
- **Timeout**: 10 minutes for large messages
- **Checkpointing**: Automatic via Azure Storage
- **Error Handling**: Non-blocking (continues processing other messages)

### Common Issues
1. **Function not starting**: Check Event Hub connection string and permissions
2. **Messages not processing**: Verify consumer group and Event Hub name
3. **Cosmos DB errors**: Check connection string and container existence
4. **Checkpoint errors**: Ensure Azure Storage (Azurite) is running

## Message Flow
```
Event Hub Message → JSON Parsing → Validation → 
Enhancement (metadata/timestamps) → Cosmos DB Storage → Logging
```

## Scaling Considerations
- Function automatically scales based on Event Hub partition count
- Each partition is processed by a separate function instance
- Message ordering is preserved within each partition
- Consider partition key strategy for optimal distribution

## Next Steps
- Monitor function performance and scaling
- Implement dead letter queue for persistent failures
- Add custom metrics and alerts
- Consider batch processing for higher throughput scenarios
- Implement message filtering based on device types or categories