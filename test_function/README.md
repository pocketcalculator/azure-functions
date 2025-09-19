# Azure Function - Cosmos DB Integration

This Azure Function adds items to a Cosmos DB database. It's designed for local development and testing.

## Prerequisites

1. **Azure Functions Core Tools**: Install the latest version
   ```bash
   npm install -g azure-functions-core-tools@4 --unsafe-perm true
   ```

2. **Python 3.8+**: Ensure Python is installed
   ```bash
   python --version
   ```

3. **Azure Cosmos DB**: You need either:
   - An Azure Cosmos DB account in Azure, OR
   - Azure Cosmos DB Emulator for local development

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Cosmos DB Connection

#### Option A: Using Azure Cosmos DB Emulator (Local Development)
1. Download and install [Azure Cosmos DB Emulator](https://docs.microsoft.com/en-us/azure/cosmos-db/local-emulator)
2. Start the emulator
3. Update `local.settings.json`:
   ```json
   {
     "Values": {
       "COSMOS_DB_CONNECTION_STRING": "AccountEndpoint=https://localhost:8081/;AccountKey=C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==;",
       "COSMOS_DB_DATABASE_NAME": "TestDatabase",
       "COSMOS_DB_CONTAINER_NAME": "TestContainer"
     }
   }
   ```

#### Option B: Using Azure Cosmos DB in the Cloud
1. Create a Cosmos DB account in Azure
2. Get the connection string from Azure portal
3. Update `local.settings.json` with your actual connection string:
   ```json
   {
     "Values": {
       "COSMOS_DB_CONNECTION_STRING": "AccountEndpoint=https://your-account.documents.azure.com:443/;AccountKey=your-key;",
       "COSMOS_DB_DATABASE_NAME": "YourDatabaseName",
       "COSMOS_DB_CONTAINER_NAME": "YourContainerName"
     }
   }
   ```

### 3. Create Database and Container

If using the emulator or a new Cosmos DB account, create the database and container:

1. Open Cosmos DB Data Explorer
2. Create a new database: `TestDatabase`
3. Create a new container: `TestContainer` with partition key `/id`

## Running the Function Locally

1. Start the Azure Functions runtime:
   ```bash
   func start
   ```

2. The function will be available at:
   - Add Item: `http://localhost:7071/api/add_item`
   - Health Check: `http://localhost:7071/api/health`

## Testing the Function

### Health Check
Test if the function is running:
```bash
curl http://localhost:7071/api/health
```

### Adding Items to Cosmos DB

#### Using curl with sample data:
```bash
# Test with sample item 1
curl -X POST http://localhost:7071/api/add_item \
  -H "Content-Type: application/json" \
  -d '{
    "id": "item-001",
    "name": "Test Product 1",
    "description": "This is a test product for Cosmos DB",
    "category": "Electronics",
    "price": 99.99,
    "data": {
      "brand": "TestBrand",
      "model": "TB-001"
    }
  }'
```

#### Using Python script:
```python
import requests
import json

# Load sample data
with open('sample_data.json', 'r') as f:
    data = json.load(f)

# Test each sample item
for item in data['sample_items']:
    response = requests.post(
        'http://localhost:7071/api/add_item',
        json=item
    )
    print(f"Item {item['id']}: {response.status_code} - {response.json()}")
```

#### Using PowerShell:
```powershell
$item = @{
    id = "item-ps-001"
    name = "PowerShell Test Item"
    description = "Test from PowerShell"
    category = "Testing"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:7071/api/add_item" -Method POST -Body $item -ContentType "application/json"
```

## Expected Responses

### Success Response (201 Created):
```json
{
  "message": "Item added successfully",
  "item_id": "item-001",
  "created_at": "2023-12-01T10:30:00.123456"
}
```

### Error Responses:
- **400 Bad Request**: Missing required fields
- **409 Conflict**: Item with ID already exists
- **500 Internal Server Error**: Database or configuration issues

## Project Structure
```
test_function/
├── function_app.py          # Main function code
├── host.json               # Function host configuration
├── local.settings.json     # Local development settings
├── requirements.txt        # Python dependencies
├── sample_data.json       # Sample test data
├── .gitignore            # Git ignore file
└── README.md             # This file
```

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `COSMOS_DB_CONNECTION_STRING` | Cosmos DB connection string | `AccountEndpoint=...;AccountKey=...;` |
| `COSMOS_DB_DATABASE_NAME` | Database name | `TestDatabase` |
| `COSMOS_DB_CONTAINER_NAME` | Container name | `TestContainer` |

## Troubleshooting

### Common Issues:

1. **"Configuration error"**: Check if `COSMOS_DB_CONNECTION_STRING` is set correctly
2. **"Database operation failed"**: Verify database and container exist
3. **Connection timeout**: If using emulator, ensure it's running
4. **Import errors**: Run `pip install -r requirements.txt`

### Debugging:
- Check function logs in the terminal where `func start` is running
- Verify Cosmos DB connectivity using Azure portal or emulator data explorer
- Test with simple data first before complex objects

## Next Steps

- Deploy to Azure using `func azure functionapp publish <app-name>`
- Add authentication and authorization
- Implement additional CRUD operations (read, update, delete)
- Add input validation and data sanitization
- Implement batch operations for multiple items