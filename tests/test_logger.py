"""
Unit tests for logging configuration.
"""

import logging
import pytest
import tempfile
from pathlib import Path
from src.utils.logger import (
    setup_logging, 
    get_logger, 
    log_execution, 
    log_error_with_trace,
    DocumentationManagerHandler
)
from src.utils.documentation_manager import DocumentationManager


def test_setup_logging_creates_logger():
    """Test that setup_logging creates a logger instance."""
    logger = setup_logging(log_level="INFO", log_to_file=False)
    assert logger is not None
    assert isinstance(logger, logging.Logger)
    assert logger.name == "tcg_content_generator"


def test_setup_logging_sets_correct_level():
    """Test that setup_logging sets the correct logging level."""
    logger = setup_logging(log_level="DEBUG", log_to_file=False)
    assert logger.level == logging.DEBUG
    
    logger = setup_logging(log_level="WARNING", log_to_file=False)
    assert logger.level == logging.WARNING


def test_get_logger_returns_logger():
    """Test that get_logger returns a logger instance."""
    logger = get_logger()
    assert logger is not None
    assert isinstance(logger, logging.Logger)


def test_get_logger_with_name():
    """Test that get_logger with name creates namespaced logger."""
    logger = get_logger("test_module")
    assert logger.name == "tcg_content_generator.test_module"


def test_setup_logging_with_file_rotation():
    """Test that setup_logging creates rotating file handler."""
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = setup_logging(
            log_level="INFO",
            log_dir=tmpdir,
            log_to_console=False,
            log_to_file=True,
            max_bytes=1024,
            backup_count=3
        )
        
        # Check that log file was created
        log_file = Path(tmpdir) / "tcg_generator.log"
        assert log_file.exists()
        
        # Check that rotating handler was added
        rotating_handlers = [
            h for h in logger.handlers 
            if isinstance(h, logging.handlers.RotatingFileHandler)
        ]
        assert len(rotating_handlers) == 1
        assert rotating_handlers[0].maxBytes == 1024
        assert rotating_handlers[0].backupCount == 3
        
        # Close all handlers to release file locks
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)


def test_setup_logging_with_documentation_manager():
    """Test that setup_logging integrates with DocumentationManager."""
    with tempfile.TemporaryDirectory() as tmpdir:
        doc_manager = DocumentationManager(docs_dir=tmpdir)
        logger = setup_logging(
            log_level="INFO",
            log_to_file=False,
            documentation_manager=doc_manager
        )
        
        # Check that DocumentationManagerHandler was added
        doc_handlers = [
            h for h in logger.handlers 
            if isinstance(h, DocumentationManagerHandler)
        ]
        assert len(doc_handlers) == 1


def test_log_execution():
    """Test that log_execution logs with timestamp."""
    logger = setup_logging(log_level="INFO", log_to_file=False)
    
    # This should not raise an exception
    log_execution(logger, "TestComponent", "test operation")


def test_log_error_with_trace():
    """Test that log_error_with_trace logs errors with stack trace."""
    logger = setup_logging(log_level="ERROR", log_to_file=False)
    
    try:
        raise ValueError("Test error")
    except ValueError as e:
        # This should not raise an exception
        log_error_with_trace(logger, e, "Test context")


def test_documentation_manager_handler_logs_events():
    """Test that DocumentationManagerHandler logs events to DOCUMENTATION.md."""
    with tempfile.TemporaryDirectory() as tmpdir:
        doc_manager = DocumentationManager(docs_dir=tmpdir)
        logger = setup_logging(
            log_level="INFO",
            log_to_file=False,
            log_to_console=False,
            documentation_manager=doc_manager
        )
        
        # Log an info message
        logger.info("Test event message")
        
        # Check that it was logged to DOCUMENTATION.md
        doc_file = Path(tmpdir) / "DOCUMENTATION.md"
        assert doc_file.exists()
        content = doc_file.read_text()
        assert "Test event message" in content
        
        # Close all handlers
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)


def test_documentation_manager_handler_logs_errors():
    """Test that DocumentationManagerHandler logs errors to PROBLEMS.md."""
    with tempfile.TemporaryDirectory() as tmpdir:
        doc_manager = DocumentationManager(docs_dir=tmpdir)
        logger = setup_logging(
            log_level="ERROR",
            log_to_file=False,
            log_to_console=False,
            documentation_manager=doc_manager
        )
        
        # Log an error with exception
        try:
            raise RuntimeError("Test error")
        except RuntimeError:
            logger.error("Test error occurred", exc_info=True)
        
        # Check that it was logged to PROBLEMS.md
        problems_file = Path(tmpdir) / "PROBLEMS.md"
        assert problems_file.exists()
        content = problems_file.read_text()
        assert "Test error occurred" in content
        assert "Stack Trace" in content
        
        # Close all handlers
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
