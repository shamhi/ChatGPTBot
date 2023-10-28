import structlog
import logging
import sys


def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout,
    )

    logger: structlog.typing.FilteringBoundLogger = structlog.get_logger(structlog.typing.FilteringBoundLogger)

    shared_processors: list[structlog.typing.Processor] = [
        structlog.processors.add_log_level
    ]

    processors = shared_processors + [
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M.%S", utc=False),
        structlog.dev.ConsoleRenderer(),
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(10),
    )

    return logger
