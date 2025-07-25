"""
Logger module for BCP Calculator

This module provides logging functionality for the BCP Calculator application.
"""

import logging
import sys
from typing import Optional

def setup_logger(log_level: int = logging.INFO) -> logging.Logger:
    """
    Set up and configure the logger.
    
    Args:
        log_level: The logging level to use (default: INFO)
        
    Returns:
        A configured logger instance
    """
    # Create logger
    logger = logging.getLogger("bcp_calculator")
    logger.setLevel(log_level)
    
    # Create console handler and set level
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(log_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add formatter to console handler
    console_handler.setFormatter(formatter)
    
    # Add console handler to logger
    logger.addHandler(console_handler)
    
    return logger

class StepLogger:
    """
    Logger wrapper for tracking steps in the BCP calculation process.
    """
    
    def __init__(self, logger: logging.Logger, step_name: str):
        """
        Initialize a step logger.
        
        Args:
            logger: The parent logger
            step_name: The name of the step being logged
        """
        self.logger = logger
        self.step_name = step_name
    
    def info(self, message: str) -> None:
        """Log an info message with step context."""
        self.logger.info(f"[{self.step_name}] {message}")
    
    def debug(self, message: str) -> None:
        """Log a debug message with step context."""
        self.logger.debug(f"[{self.step_name}] {message}")
    
    def warning(self, message: str) -> None:
        """Log a warning message with step context."""
        self.logger.warning(f"[{self.step_name}] {message}")
    
    def error(self, message: str) -> None:
        """Log an error message with step context."""
        self.logger.error(f"[{self.step_name}] {message}")
    
    def critical(self, message: str) -> None:
        """Log a critical message with step context."""
        self.logger.critical(f"[{self.step_name}] {message}")