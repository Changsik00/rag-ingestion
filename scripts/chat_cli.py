import requests
import json
import uuid

BASE_URL = "http://localhost:8005/v1/rag/sessions"
SESSION_ID = f"cli-session-{uuid.uuid4().hex[:6]}"

def chat():
    print(f"🤖 Agent CLI (Session: {SESSION_ID})")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break

        payload = {
            "message": user_input,
            "hitl_enabled": True
        }

        try:
            print("Thinking...", end="\r")
            response = requests.post(f"{BASE_URL}/{SESSION_ID}/ask", json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Extract the actual text answer
            # The API returns 'messages' list, the last one is usually the assistant response
            # Or use 'draft_content' / specific logic
            
            messages = data.get("messages", [])
            last_message = messages[-1] if messages else {}
            content = last_message.get("content", "")
            
            # Clean up newlines for display
            print(f"\nAgent: {content}\n")
            
            # Show intent (debug)
            intent = data.get("intent")
            if intent:
                print(f"[Debug: Intent='{intent}']")

        except Exception as e:
            print(f"\nError: {e}")

if __name__ == "__main__":
    chat()
