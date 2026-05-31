import logging
import os

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry import metrics, trace
from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

SERVICE_NAME = "journal-api"
connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
logger = logging.getLogger(SERVICE_NAME)

# Initialize Telemetry
if connection_string:
    # configure_azure_monitor automatically sets up trace, metric, and log SDKs
    # and exports them to Application Insights using the connection string.
    try:
        configure_azure_monitor(
            connection_string=connection_string,
        )
        logger.info("Azure Monitor OpenTelemetry successfully configured.")
    except Exception as e:
        logger.warning(f"Azure Monitor OpenTelemetry could not be configured: {e}")
else:
    # Ensure logs still show up in console during local dev if AI is off
    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO)
    logger.info("APPLICATIONINSIGHTS_CONNECTION_STRING not found. Azure Monitor export disabled.")


def instrument_app(app):
    """
    Instruments the FastAPI app for OpenTelemetry.
    This adds middleware to capture request durations and status codes.
    """
    FastAPIInstrumentor.instrument_app(
        app,
        tracer_provider=trace.get_tracer_provider(),
        meter_provider=metrics.get_meter_provider(),
    )

    # Instrument database calls
    # This captures SQL queries and durations automatically
    AsyncPGInstrumentor().instrument()


# Standard OpenTelemetry entry points
tracer = trace.get_tracer(SERVICE_NAME)
meter = metrics.get_meter(SERVICE_NAME)

# Define metrics used in the application
entry_created_counter = meter.create_counter(
    "journal.entries.created", unit="1", description="Total number of journal entries created"
)
