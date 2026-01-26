import json
from datetime import datetime
from typing import Any


class FeedbackService:
    """사용자 피드백을 저장하고 조회하는 서비스 (JSONL 기반)"""

    def __init__(self, feedback_file: str = "feedback.jsonl"):
        self.feedback_file = feedback_file

    def save_feedback(self, data: dict[str, Any]) -> bool:
        try:
            if "timestamp" not in data:
                data["timestamp"] = datetime.now().isoformat()

            with open(self.feedback_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
            return True
        except Exception as e:
            print(f"Error saving feedback: {e}")
            return False

    def get_recent_feedback(self, limit: int = 50) -> list[dict[str, Any]]:
        try:
            with open(self.feedback_file, encoding="utf-8") as f:
                lines = f.readlines()

            entries = []
            for line in reversed(lines):
                if len(entries) >= limit:
                    break
                try:
                    entries.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue

            return entries
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"Error reading feedback: {e}")
            return []
