import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

class FeedbackService:
    def __init__(self, feedback_file: str = "feedback.jsonl"):
        self.feedback_file = feedback_file

    def save_feedback(self, data: Dict[str, Any]) -> bool:
        """
        Save feedback to a JSONL file.
        Appends timestamp if not present.
        """
        try:
            if "timestamp" not in data:
                data["timestamp"] = datetime.now().isoformat()
            
            with open(self.feedback_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
            return True
        except Exception as e:
            print(f"Error saving feedback: {e}")
            return False

    def get_recent_feedback(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retrieve recent feedback from the JSONL file.
        Returns entries in reverse chronological order (newest first).
        """
        try:
            with open(self.feedback_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
            # Parse lines
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
