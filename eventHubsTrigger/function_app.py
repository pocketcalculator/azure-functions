import azure.functions as func
import datetime
import json
import logging

app = func.FunctionApp()


@app.event_hub_message_trigger(arg_name="azeventhub", event_hub_name="paulsczurek-raspiiot",
connection="EventHubConnectionString") 
def EventHubsExample(azeventhub: func.EventHubEvent):
    logging.info('Python EventHub trigger processed an event: %s',
                azeventhub.get_body().decode('utf-8'))
