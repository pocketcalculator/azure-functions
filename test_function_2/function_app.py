import azure.functions as func
import logging
import json
import os
from datetime import datetime
from azure.cosmos import CosmosClient, exceptions
from typing import List

# Initialize the function app
app = func.FunctionApp()

@app.function_name(name="HttpTriggerTest")
@app.route(route="test", auth_level=func.AuthLevel.ANONYMOUS)
def test_function(req: func.HttpRequest) -> func.HttpResponse:
    """
    Simple HTTP trigger function for testing deployment
    """
    logging.info('HTTP trigger function processed a request.')
    
    return func.HttpResponse(
        "Hello from Azure Functions! Deployment is working correctly.",
        status_code=200
    )

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
    database_name = os.environ.get('COSMOS_DB_DATABASE_NAME', 'devicesdb')
    container_name = os.environ.get('COSMOS_DB_CONTAINER_NAME', 'devices')
    
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)
    
    return container

@app.event_hub_message_trigger(
    arg_name="azeventhub", 
    event_hub_name="msfthack2025iothub",
    connection="EVENT_HUB_CONNECTION_STRING",
    consumer_group="$Default"
)
def eventhub_to_cosmos(azeventhub: func.EventHubEvent):
    """
    Azure Function triggered by Event Hub messages.
    Processes JSON messages and adds them to Cosmos DB.
    
    The function expects JSON messages with the following structure:
    {
        "id": "unique-id",
        "name": "Device/Item Name",
        "description": "Optional description",
        "category": "Optional category",
        "data": { ... any additional data ... }
    }
    
    If 'id' is not provided, one will be generated.
    """
    logging.info('Event Hub trigger function processed an event.')
    
    try:
        # Get the message body
        message_body = azeventhub.get_body().decode('utf-8')
        logging.info(f'Received message: {message_body[:200]}...' if len(message_body) > 200 else f'Received message: {message_body}')
        
        # Parse JSON message
        try:
            message_data = json.loads(message_body)
        except json.JSONDecodeError as e:
            logging.error(f'Failed to parse JSON message: {e}')
            logging.error(f'Message body: {message_body}')
            return  # Skip malformed messages as requested
        
        # Validate message structure
        if not isinstance(message_data, dict):
            logging.error(f'Message is not a JSON object: {type(message_data)}')
            return
        
        # Generate ID if not provided
        if 'id' not in message_data or not message_data['id']:
            # Generate ID from Event Hub metadata and timestamp
            sequence_number = azeventhub.sequence_number
            partition_key = azeventhub.partition_key
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S%f')
            message_data['id'] = f'eh-{partition_key}-{sequence_number}-{timestamp}'
            logging.info(f'Generated ID for message: {message_data["id"]}')
        
        # Ensure 'name' field exists (required for consistency with HTTP function)
        if 'name' not in message_data:
            message_data['name'] = f'EventHub Message {message_data["id"]}'
        
        # Add Event Hub metadata and processing information
        message_data['eventhub_metadata'] = {
            'partition_key': azeventhub.partition_key,
            'sequence_number': azeventhub.sequence_number,
            'offset': azeventhub.offset,
            'enqueued_time': azeventhub.enqueued_time.isoformat() if azeventhub.enqueued_time else None,
            'consumer_group': os.environ.get('EVENT_HUB_CONSUMER_GROUP', '$Default')
        }
        
        # Add processing timestamps
        message_data['received_at'] = datetime.utcnow().isoformat()
        message_data['processed_by'] = 'azure-function-eventhub'
        message_data['source'] = 'eventhub'
        
        # Get Cosmos DB container
        container = get_container()
        
        # Add item to Cosmos DB
        try:
            created_item = container.create_item(body=message_data)
            logging.info(f'Successfully added item to Cosmos DB: {created_item["id"]}')
            
        except exceptions.CosmosResourceExistsError:
            # Item already exists, try to update it
            logging.warning(f'Item with id {message_data["id"]} already exists, attempting to update...')
            try:
                # Add update timestamp
                message_data['updated_at'] = datetime.utcnow().isoformat()
                updated_item = container.replace_item(item=message_data["id"], body=message_data)
                logging.info(f'Successfully updated existing item: {updated_item["id"]}')
            except Exception as update_error:
                logging.error(f'Failed to update existing item {message_data["id"]}: {str(update_error)}')
                
        except exceptions.CosmosHttpResponseError as e:
            logging.error(f'Cosmos DB error for message {message_data.get("id", "unknown")}: {str(e)}')
            # Don't raise - continue processing other messages
            
    except ValueError as e:
        logging.error(f'Configuration error: {str(e)}')
        
    except Exception as e:
        logging.error(f'Unexpected error processing Event Hub message: {str(e)}')
        logging.error(f'Message body: {message_body if "message_body" in locals() else "Could not retrieve message body"}')
        # Don't raise - continue processing other messages

@app.route(route="health", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """Health check endpoint"""
    try:
        # Test Cosmos DB connection
        container = get_container()
        
        return func.HttpResponse(
            json.dumps({
                "status": "healthy", 
                "timestamp": datetime.utcnow().isoformat(),
                "cosmos_db": "connected",
                "event_hub_config": "configured" if os.environ.get('EVENT_HUB_CONNECTION_STRING') else "missing"
            }),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f'Health check failed: {str(e)}')
        return func.HttpResponse(
            json.dumps({
                "status": "unhealthy", 
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }),
            status_code=500,
            mimetype="application/json"
        )