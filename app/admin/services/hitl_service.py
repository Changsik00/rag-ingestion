import logging
from typing import Any

import requests

logger = logging.getLogger(__name__)


class HitlService:
    BASE_URL = "http://localhost:8000/jobs"  # Assuming default port

    def list_threads(self, limit: int = 10) -> list[dict[str, Any]]:
        """List active threads from the backend."""
        try:
            response = requests.get(f"{self.BASE_URL}/active/threads", params={"limit": limit})
            if response.status_code == 200:
                return response.json()
            logger.error(f"Failed to list threads: {response.text}")
            return []
        except Exception as e:
            logger.error(f"Error listing threads: {e}")
            return []

    def get_thread_status(self, thread_id: str) -> str:
        """Get status of a specific thread."""
        try:
            response = requests.get(f"{self.BASE_URL}/{thread_id}/status")
            if response.status_code == 200:
                return response.json().get("status", "Unknown")
            return "Error"
        except Exception as e:
            logger.error(f"Error getting status for {thread_id}: {e}")
            return "Error"

    def get_thread_trace(self, thread_id: str) -> dict[str, Any]:
        """Get execution trace (snapshot) of a thread."""
        try:
            response = requests.get(f"{self.BASE_URL}/{thread_id}/trace")
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception as e:
            logger.error(f"Error getting trace for {thread_id}: {e}")
            return {}

    def resume_thread(self, thread_id: str, input_data: dict[str, Any]) -> bool:
        """Resume an interrupted thread with new input."""
        try:
            response = requests.post(f"{self.BASE_URL}/{thread_id}/resume", json={"input": input_data})
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error resuming thread {thread_id}: {e}")
            return False
