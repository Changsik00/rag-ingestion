import logging
import re
from typing import TYPE_CHECKING, Annotated, Any, Literal, TypedDict

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph, add_messages

from app.core.config import get_settings
from app.domain.entities.job import JobStatus

if TYPE_CHECKING:
    from app.application.services.ingestion import Ingestion
    from app.application.services.rag import RAG

logger = logging.getLogger(__name__)
