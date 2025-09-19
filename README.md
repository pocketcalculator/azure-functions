# Azure Functions Collection

This repository contains multiple Azure Functions for various data processing and integration scenarios.

## 📁 Repository Structure

```
azure-functions/
├── cosmosDBTrigger/           # Cosmos DB triggered function
├── eventHubsTrigger/          # Event Hubs triggered function  
├── httpTrigger/               # HTTP triggered function
├── iotHub2cosmosDBTrigger/    # IoT Hub to Cosmos DB function
├── iot_datamover_cosmosdb/    # IoT data mover to Cosmos DB
├── iothub2cosmosdb/           # IoT Hub to Cosmos DB integration
├── test_function/             # Test function for development
└── test_function_2/           # Additional test function
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Azure Functions Core Tools
- Azure CLI

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/pocketcalculator/azure-functions.git
   cd azure-functions
   ```

2. **Set up a function for local development:**
   ```bash
   cd [function-directory]
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure local settings:**
   ```bash
   cp local.settings.json.sample local.settings.json
   # Edit local.settings.json with your configuration
   ```

4. **Run locally:**
   ```bash
   func start
   ```

## 🔧 Function Descriptions

### CosmosDB Trigger
- **Path:** `cosmosDBTrigger/`
- **Trigger:** Cosmos DB change feed
- **Purpose:** Process changes in Cosmos DB documents

### Event Hubs Trigger  
- **Path:** `eventHubsTrigger/`
- **Trigger:** Event Hubs messages
- **Purpose:** Process streaming data from Event Hubs

### HTTP Trigger
- **Path:** `httpTrigger/`
- **Trigger:** HTTP requests
- **Purpose:** RESTful API endpoints

### IoT Hub Integrations
- **Paths:** `iotHub2cosmosDBTrigger/`, `iot_datamover_cosmosdb/`, `iothub2cosmosdb/`
- **Trigger:** IoT Hub messages
- **Purpose:** Process IoT device data and store in Cosmos DB

### Test Functions
- **Paths:** `test_function/`, `test_function_2/`
- **Purpose:** Development and testing scenarios

## 🔒 Security

- All sensitive configuration is stored in `local.settings.json` files (not tracked in git)
- Connection strings and secrets are excluded from version control
- Each function has its own `.gitignore` for additional protection

## 🚢 Deployment

Each function can be deployed independently:

```bash
cd [function-directory]
func azure functionapp publish YOUR-FUNCTION-APP-NAME
```

## 📝 Configuration

Each function requires a `local.settings.json` file for local development. Sample files are provided where available.

Example `local.settings.json`:
```json
{
  "IsEncrypted": false,
  "Values": {
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AzureWebJobsStorage": "your-storage-connection-string",
    "CosmosDBConnectionString": "your-cosmosdb-connection-string"
  }
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## 📄 License

See individual function directories for specific license information.