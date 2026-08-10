import logging

from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import (
    OTLPLogExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
    OTLPMetricExporter,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
    OTLPSpanExporter,
)
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

OTLP_ENDPOINT = "http://host.docker.internal:4317"

resource = Resource.create(
    {
        "service.name": "journal-api",
        "service.version": "1.0.0",
        "deployment.environment": "development",
        "cloud.provider": "aws",
    }
)


def configure_tracing() -> None:
    trace_provider = TracerProvider(resource=resource)

    trace_exporter = OTLPSpanExporter(
        endpoint=OTLP_ENDPOINT,
        insecure=True,
    )

    trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))

    trace.set_tracer_provider(trace_provider)


def configure_metrics() -> None:
    metric_exporter = OTLPMetricExporter(
        endpoint=OTLP_ENDPOINT,
        insecure=True,
    )

    metric_reader = PeriodicExportingMetricReader(
        metric_exporter,
        export_interval_millis=10_000,
    )

    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=[metric_reader],
    )

    metrics.set_meter_provider(meter_provider)


def configure_logging() -> None:
    logger_provider = LoggerProvider(resource=resource)

    log_exporter = OTLPLogExporter(
        endpoint=OTLP_ENDPOINT,
        insecure=True,
    )

    logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

    set_logger_provider(logger_provider)

    otel_handler = LoggingHandler(
        level=logging.INFO,
        logger_provider=logger_provider,
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(otel_handler)


def configure_telemetry() -> None:
    configure_tracing()
    configure_metrics()
    configure_logging()


# Configure the providers before creating the instruments.
configure_telemetry()


# Objects imported by the rest of the application.
logger = logging.getLogger("journal-api")

tracer = trace.get_tracer("journal-api")

meter = metrics.get_meter("journal-api")

journal_entries_created = meter.create_counter(
    name="journal_entries_created",
    description="Number of journal entries created",
    unit="1",
)
