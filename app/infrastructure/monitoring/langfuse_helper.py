"""
LangFuse Helper Module.
Wraps LangfuseCallbackHandler creation to handle conditional initialization logic.
"""

import logging
import os
from typing import Optional

# Conditional import to prevent crashes if package is missing
try:
    from langfuse.callback import LangfuseCallbackHandler

    HAS_LANGFUSE = True
except ImportError:
    HAS_LANGFUSE = False

logger = logging.getLogger(__name__)


def get_langfuse_handler(
    user_id: str | None = None,
    session_id: str | None = None,
    trace_name: str | None = None,
) -> Optional["LangfuseCallbackHandler"]:
    """
    Creates and returns a LangfuseCallbackHandler instance if configured.

    Env Vars required:
      - LANGFUSE_SECRET_KEY
      - LANGFUSE_PUBLIC_KEY
      - LANGFUSE_HOST

    Args:
        user_id (str, optional): User Identifier for tracing.
        session_id (str, optional): Session Identifier.
        trace_name (str, optional): Name of the trace.

    Returns:
        LangfuseCallbackHandler | None: Handler instance or None if not configured.
    """
    if not HAS_LANGFUSE:
        logger.debug("LangFuse package not found. Skipping observability.")
        return None

    secret_key = os.getenv("LANGFUSE_SECRET_KEY")
    public_key = os.getenv("LANGFUSE_PUBLIC_KEY")
    host = os.getenv("LANGFUSE_HOST")

    # Basic validation (placeholders usually start with sk-lf-..., but check non-empty)
    if not secret_key or not public_key or not host:
        logger.debug("LangFuse environment variables not set. Skipping observability.")
        return None

    if "sk-lf-..." in secret_key or "pk-lf-..." in public_key:
        logger.debug("LangFuse environment variables are placeholders. Skipping observability.")
        return None

    try:
        handler = LangfuseCallbackHandler(
            secret_key=secret_key,
            public_key=public_key,
            host=host,
            user_id=user_id,
            session_id=session_id,
            trace_name=trace_name,
        )
        logger.info(f"LangFuse Observability Enabled. Host: {host}")
        return handler
    except Exception as e:
        logger.error(f"Failed to initialize LangFuse Handler: {e}")
        return None
