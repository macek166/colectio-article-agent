"""
Logging configuration for TCG Content Generator.

This module provides structured logging setup with console and file output handlers,
including rotation and integration with DocumentationManager.
"""

import logging
import sys
import traceback
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Optional
from datetime import datetime


class DocumentationManagerHandler(logging.Handler):
    """Custom logging handler that integrates with DocumentationManager."""

    def __init__(self, documentation_manager: Any, level: int = logging.NOTSET) -> None:
        """Initialize the handler with a DocumentationManager instance.

        Args:
            documentation_manager: DocumentationManager instance for logging
            level: Logging level threshold
        """
        super().__init__(level)
        self.documentation_manager = documentation_manager

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to DocumentationManager.

        Args:
            record: Log record to emit
        """
        try:
            # Log significant events to DOCUMENTATION.md
            if record.levelno >= logging.INFO and record.levelno < logging.ERROR:
                event = f"{record.name} - {record.funcName}"
                details = self.format(record)
                self.documentation_manager.log_event(event, details)

            # Log errors and critical issues to PROBLEMS.md
            elif record.levelno >= logging.ERROR:
                issue = f"{record.name} - {record.funcName}: {record.getMessage()}"
                status = "active"

                # Include stack trace if available
                details = self.format(record)
                if record.exc_info:
                    details += "\n\n**Stack Trace:**\n```\n"
                    details += ''.join(traceback.format_exception(*record.exc_info))
                    details += "```"

                self.documentation_manager.log_problem(issue, status, details)
        except Exception:  # pylint: disable=broad-except
            # Don't let logging errors break the application
            self.handleError(record)


def setup_logging(  # pylint: disable=too-many-arguments
    log_level: str = "INFO",
    log_dir: str = "logs",
    log_to_console: bool = True,
    log_to_file: bool = True,
    documentation_manager: Optional[Any] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up structured logging with rotation and DocumentationManager integration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files
        log_to_console: Whether to output logs to console
        log_to_file: Whether to output logs to file with rotation
        documentation_manager: Optional DocumentationManager for integration
        max_bytes: Maximum size of log file before rotation (default: 10 MB)
        backup_count: Number of backup log files to keep (default: 5)

    Returns:
        Configured logger instance
    """
    # Create root logger to capture all application logs
    logger = logging.getLogger()
    
    # Set levels for noisy libraries
    logging.getLogger("streamlit").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    logging.getLogger("watchdog").setLevel(logging.WARNING)
    
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatters
    detailed_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)8s] %(name)s - "
            "%(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    simple_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)8s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    if log_to_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)

    # File handler with rotation
    if log_to_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        # Create rotating log file
        log_file = log_path / "tcg_generator.log"

        rotating_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8"
        )
        rotating_handler.setLevel(logging.DEBUG)
        rotating_handler.setFormatter(detailed_formatter)
        logger.addHandler(rotating_handler)

        logger.info(
            "Logging to file: %s (max size: %d bytes, backups: %d)",
            log_file, max_bytes, backup_count
        )

    # DocumentationManager handler
    if documentation_manager:
        doc_handler = DocumentationManagerHandler(
            documentation_manager, level=logging.INFO
        )
        doc_handler.setFormatter(detailed_formatter)
        logger.addHandler(doc_handler)
        logger.info("DocumentationManager integration enabled")

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Logger name (defaults to tcg_content_generator)

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"tcg_content_generator.{name}")
    return logging.getLogger("tcg_content_generator")


def log_execution(logger: logging.Logger, component: str, operation: str) -> None:
    """
    Log component execution with timestamp.

    Args:
        logger: Logger instance
        component: Name of the component being executed
        operation: Description of the operation
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info("[%s] %s: %s", timestamp, component, operation)


def log_error_with_trace(
    logger: logging.Logger,
    error: Exception,
    context: str = ""
) -> None:
    """
    Log error with full stack trace.

    Args:
        logger: Logger instance
        error: Exception that occurred
        context: Additional context about where the error occurred
    """
    error_msg = f"{context}: {str(error)}" if context else str(error)
    logger.error(error_msg, exc_info=True)
