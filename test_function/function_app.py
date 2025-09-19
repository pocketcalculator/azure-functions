import azure.functions as func
import logging
import json
import os
from datetime import datetime
from azure.cosmos import CosmosClient, exceptions

# Initialize the function app
app = func.FunctionApp()

# Initialize Cosmos DB client
def get_cosmos_client():
    """Initialize and return Cosmos DB client"""
    connection_string = os.environ.get('COSMOS_DB_CONNECTION_STRING')
    if not connection_string:
        raise ValueError("COSMOS_DB_CONNECTION_STRING environment variable is required")
    
    return CosmosClient.from_connection_string(connection_string)

def get_container():
    """Get Cosmos DB container"""
    client = get_cosmos_client()
    database_name = os.environ.get('COSMOS_DB_DATABASE_NAME', 'TestDatabase')
    container_name = os.environ.get('COSMOS_DB_CONTAINER_NAME', 'TestContainer')
    
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)
    
    return container

@app.route(route="add_item", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
def add_item_to_cosmos(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Function to add an item to Cosmos DB
    
    Expected JSON payload:
    {
        "id": "unique-id",
        "name": "Item Name",
        "description": "Item Description",
        "category": "Category",
        "data": { ... any additional data ... }
    }
    """
    logging.info('Python HTTP trigger function processed a request.')

    try:
        # Parse request body
        req_body = req.get_json()
        
        if not req_body:
            return func.HttpResponse(
                json.dumps({"error": "Request body is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Validate required fields
        required_fields = ['id', 'name']
        for field in required_fields:
            if field not in req_body:
                return func.HttpResponse(
                    json.dumps({"error": f"Field '{field}' is required"}),
                    status_code=400,
                    mimetype="application/json"
                )
        
        # Add timestamp and processing info
        item_data = req_body.copy()
        item_data['created_at'] = datetime.utcnow().isoformat()
        item_data['processed_by'] = 'azure-function'
        
        # Get Cosmos DB container
        container = get_container()
        
        # Add item to Cosmos DB
        created_item = container.create_item(body=item_data)
        
        logging.info(f'Successfully added item with id: {created_item["id"]}')
        
        return func.HttpResponse(
            json.dumps({
                "message": "Item added successfully",
                "item_id": created_item["id"],
                "created_at": created_item["created_at"]
            }),
            status_code=201,
            mimetype="application/json"
        )
        
    except exceptions.CosmosResourceExistsError:
        logging.warning(f'Item with id {req_body.get("id")} already exists')
        return func.HttpResponse(
            json.dumps({"error": "Item with this ID already exists"}),
            status_code=409,
            mimetype="application/json"
        )
    
    except exceptions.CosmosHttpResponseError as e:
        logging.error(f'Cosmos DB error: {str(e)}')
        return func.HttpResponse(
            json.dumps({"error": "Database operation failed"}),
            status_code=500,
            mimetype="application/json"
        )
    
    except ValueError as e:
        logging.error(f'Configuration error: {str(e)}')
        return func.HttpResponse(
            json.dumps({"error": "Function configuration error"}),
            status_code=500,
            mimetype="application/json"
        )
    
    except Exception as e:
        logging.error(f'Unexpected error: {str(e)}')
        return func.HttpResponse(
            json.dumps({"error": "Internal server error"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint"""
    return func.HttpResponse(
        json.dumps({"status": "healthy", "timestamp": datetime.utcnow().isoformat()}),
        status_code=200,
        mimetype="application/json"
    )