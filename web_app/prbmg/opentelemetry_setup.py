import logging
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry._logs import set_logger_provider

from dotenv import load_dotenv
import os

load_dotenv()

APPLICATIONINSIGHTS_CONNECTION_STRING=os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING')
if not APPLICATIONINSIGHTS_CONNECTION_STRING:
    raise ValueError("The APPLICATIONINSIGHTS_CONNECTION_STRING environment variable is not set or is empty.")

# SET UP LOGGING EXPORTER
logger_provider = LoggerProvider()
set_logger_provider(logger_provider)

exporter = AzureMonitorLogExporter(
    connection_string=APPLICATIONINSIGHTS_CONNECTION_STRING
)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))

# Attach LoggingHandler to namespaced logger
handler = LoggingHandler()
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


DjangoInstrumentor().instrument()

RequestsInstrumentor().instrument()