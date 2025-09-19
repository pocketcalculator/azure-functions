import azure.functions as func
import logging

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