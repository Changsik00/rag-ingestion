import logging
import sys


def setup_logger(name: str) -> logging.Logger:
    """
    Configure and return a logger instance with standard formatting.
    Target: stdout for container logs.
    """
    logger = logging.getLogger(name)

    # Always set the level to DEBUG as per instruction
    logger.setLevel(logging.DEBUG)

    # Prevent adding handlers multiple times
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Prevent propagation to root logger to avoid double logging if root is configured
        logger.propagate = False

    return logger
