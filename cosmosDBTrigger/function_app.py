import azure.functions as func
import datetime
import json
import logging

app = func.FunctionApp()


@app.cosmos_db_trigger(arg_name="azcosmosdb", container_name="devices",
                        database_name="devicesdb", connection="CosmosDBConnectionString") 
def cosmosDBFunction(azcosmosdb: func.DocumentList):
    logging.info('Python CosmosDB triggered.')
