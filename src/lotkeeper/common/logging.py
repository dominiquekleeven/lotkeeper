import fnmatch
import inspect
import logging
import sys

from loguru import logger

# List of loggers used by related libraries and packages
loggers = (
    "uvicorn*",
    "fastapi*",
    "asyncio*",
    "starlette*",
    "sqlalchemy*",
)


# List of keywords for logs to ignore
keywords_to_ignore = ("GET /health", "POST /health", "HTTP/1.1")


def setup_loguru() -> None:
    """Configure Loguru logger with PID in output"""
    logger.remove()  # remove default handler
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<cyan>{process}</cyan> | "  # PID
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>",
        level="INFO",
        backtrace=True,
        diagnose=True,
    )


class InterceptHandler(logging.Handler):
    """Recommended intercept handler for loguru

    Args:
        record: The logging record to emit
    """

    def emit(self, record: logging.LogRecord) -> None:
        level: str | int
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message.
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        # Check if the log message contains keywords to ignore
        message = record.getMessage()
        if any(keyword in message for keyword in keywords_to_ignore):
            return

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def propagate_logs() -> None:
    """Propogates the stdlib loggers to the loguru logger"""

    # Get all existing loggers
    existing_loggers = list(logging.root.manager.loggerDict.keys())

    # Find loggers that match our wildcard patterns
    matched_loggers = []
    for pattern in loggers:
        matched_loggers.extend(fnmatch.filter(existing_loggers, pattern))

    # Also add our base patterns (without wildcards) to ensure they're covered
    base_patterns = [pattern.rstrip("*") for pattern in loggers]
    for base_pattern in base_patterns:
        if base_pattern not in matched_loggers:
            matched_loggers.append(base_pattern)

    # Configure all matched loggers
    for logger_name in matched_loggers:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = []
        logging_logger.propagate = True

    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
