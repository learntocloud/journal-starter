"""Application logging configuration, completed in Task 3."""

import logging


def configure_logging(level: int = logging.INFO) -> None:
    """Configure application logging at the requested level, defaulting to INFO.

    TODO (Task 3):
      - Use logging.basicConfig() with the requested level and a format that
        includes the level, logger name, and message.
      - Set the root logger's level explicitly too: basicConfig() does nothing
        when a server or test runner has already installed handlers.
      - Preserve existing handlers; do not use force=True.

    Module loggers inherit this configuration through normal propagation. The
    logging exercise runs entry operations at INFO and DEBUG to compare output.
    Never log journal text, settings objects, or credentials.
    """

    logging.basicConfig(
        level=level,
        format="%(levelname)s %(name)s %(message)s",
    )
    logging.getLogger().setLevel(level)
