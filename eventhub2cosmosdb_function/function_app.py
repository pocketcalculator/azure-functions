import azure.functions as func
import datetime
import json
import logging

app = func.FunctionApp()

@app.event_hub_message_trigger(arg_name="eventhubmsg", event_hub_name="EventHubName", connection="EventHubConnectionString")
@app.cosmos_db_output(arg_name="outputDocument", container_name="Messages", database_name="SensorReadings", connection="CosmosDBConnectionString")
def eventHubToCosmosDBFunction(eventhubmsg: func.EventHubEvent, outputDocument: func.Out[func.Document]):
    logging.info('Python EventHub trigger processed an event: %s', eventhubmsg.get_body().decode('utf-8'))
    
    # Parse the Event Hub message
    message = json.loads(eventhubmsg.get_body().decode('utf-8'))
    
    # Extract the data from the eventhub message body
    extracted_data = {
        "id": message.get("id"),
        "value": message.get("value"),
        "timestamp": message.get("timestamp")
    }   

    # Create a document to send to CosmosDB
    document = {
        "id": extracted_data["id"],
        "value": extracted_data["value"],
        "timestamp": extracted_data["timestamp"],
    }
    
    # Set the document to the CosmosDB output binding
    outputDocument.set(func.Document.from_dict(document))