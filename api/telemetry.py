import logging
import os

from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor, ConsoleLogExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import ConsoleMetricExporter, PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

SERVICE_NAME = "journal-api"

resource = Resource.create({"service.name": SERVICE_NAME})

# OTLP configuration
otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
if otlp_endpoint:
    logging.info(f"OTLP exporter endpoint set to {otlp_endpoint}")
else:
    logging.info("No OTLP exporter endpoint detected; using console exporters")

# Tracing
trace_provider = TracerProvider(resource=resource)
if otlp_endpoint:
    trace_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint)))
else:
    trace_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(trace_provider)
tracer = trace.get_tracer(SERVICE_NAME)

# Metrics
metric_readers = []
if otlp_endpoint:
    metric_readers.append(PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=otlp_endpoint)))
else:
    metric_readers.append(
        PeriodicExportingMetricReader(ConsoleMetricExporter(), export_interval_millis=5000)
    )

meter_provider = MeterProvider(
    resource=resource,
    metric_readers=metric_readers,
)
metrics.set_meter_provider(meter_provider)
meter = metrics.get_meter(SERVICE_NAME)
entry_created_counter = meter.create_counter(
    "journal.entries.created",
    description="Number of journal entries created",
)

# Logging and correlation
logger_provider = LoggerProvider(resource=resource)
if otlp_endpoint:
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(OTLPLogExporter(endpoint=otlp_endpoint))
    )
else:
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(ConsoleLogExporter()))
set_logger_provider(logger_provider)

otel_logging_handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(otel_logging_handler)
root_logger.addHandler(logging.StreamHandler())


def instrument_app(app):
    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=trace_provider,
        meter_provider=meter_provider,
    )
