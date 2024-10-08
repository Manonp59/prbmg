import logging
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry._logs import set_logger_provider
from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from azure.monitor.opentelemetry.exporter import AzureMonitorMetricExporter
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter

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

# SET UP TRACE EXPORTER
trace_exporter = AzureMonitorTraceExporter(
    connection_string=APPLICATIONINSIGHTS_CONNECTION_STRING
)
resource = Resource(attributes={"cloud.role": "DjangoApplication","service.name":"DjangoApplication"})
tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))

trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer(__name__)

# SET UP METRIC
metric_exporter = AzureMonitorMetricExporter(
    connection_string=APPLICATIONINSIGHTS_CONNECTION_STRING
)

frequency_millis = 60000 #min
reader = PeriodicExportingMetricReader(exporter=metric_exporter, export_interval_millis=frequency_millis)
metrics.set_meter_provider(MeterProvider(metric_readers=[reader]))
meter = metrics.get_meter_provider().get_meter("satisfaction_metrics")

# Create custom metric 
prediction_counter_per_minute = meter.create_counter("prediction_counter_per_minute")