import asyncio
import httpx
import json
import uuid

BACKEND_URL = "http://localhost:8000/v1"

async def test_config(name, top_k, temperature, query="일론 머스크에 대해서 알려줘"):
    thread_id = f"eval-{uuid.uuid4().hex[:8]}"
    payload = {
        "message": query,
        "filters": {},
        "hitl_enabled": False,
        "advanced_settings": {
            "top_k": top_k,
            "temperature": temperature,
            "search_strategy": "hybrid"
        }
    }
    
    print(f"\n{'='*50}")
    print(f"TEST CASE: {name}")
    print(f"CONFIG: top_k={top_k}, temperature={temperature}")
    print(f"{'='*50}")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(f"{BACKEND_URL}/rag/sessions/{thread_id}/ask", json=payload)
            response.raise_for_status()
            result = response.json()
            
            # 1. Answer Quality
            answer = ""
            if result.get("messages"):
                # Map 'assistant' (fastapi) or 'ai' (internal)
                answer = next((m["content"] for m in reversed(result["messages"]) if m["role"] in ["ai", "assistant"]), "No response")
            
            # 2. Retrieval Stats
            context_data = result.get("context_data") or {}
            v_chunks = context_data.get("vector_chunks", [])
            k_chunks = context_data.get("keyword_chunks", [])
            g_chunks = context_data.get("graph_data", [])
            
            v_titles = [c.get("metadata", {}).get("title", "No Title") for c in v_chunks]
            
            print(f"[*] Rewritten Query: {result.get('context_data', {}).get('rewritten_query', 'N/A')}")
            print(f"[*] Retrieval: Vector({len(v_chunks)}), Keyword({len(k_chunks)}), Graph({len(g_chunks)})")
            print(f"[*] Sample Vector Titles: {v_titles}")
            print(f"[*] Answer: {answer[:300]}...")
            
            # Check for citations
            citations = context_data.get("citations", [])
            print(f"[*] Citations: {len(citations)}")
            
            return {
                "name": name,
                "answer": answer,
                "retrieval": {"vector": len(v_chunks), "keyword": len(k_chunks), "graph": len(g_chunks)},
                "rewritten": result.get("context_data", {}).get("rewritten_query", "None"),
                "citations": len(citations),
                "titles": v_titles
            }
            
        except Exception as e:
            print(f"[!] Error: {str(e)}")
            return None

async def main():
    test_cases = [
        {"name": "LOW (Deteriministic)", "top_k": 3, "temperature": 0.0},
        {"name": "MEDIUM (Balanced)", "top_k": 5, "temperature": 0.5},
        {"name": "HIGH (Creative/Broad)", "top_k": 10, "temperature": 1.0},
    ]
    
    summary = []
    for tc in test_cases:
        res = await test_config(tc["name"], tc["top_k"], tc["temperature"])
        if res:
            summary.append(res)
            
    print("\n\n" + "#" * 50)
    print("FINAL EVALUATION SUMMARY")
    print("#" * 50)
    for s in summary:
        print(f"[{s['name']}] Rewritten: {s['rewritten']} | Context: V:{s['retrieval']['vector']}, K:{s['retrieval']['keyword']} | Citations: {s['citations']}")

if __name__ == "__main__":
    asyncio.run(main())
