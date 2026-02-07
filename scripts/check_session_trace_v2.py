import json
import psycopg
from psycopg.rows import dict_row
import sys

def check_trace(thread_id):
    conn_info = "host=rag-postgres port=5432 dbname=checkpoints user=postgres password=postgres"
    
    try:
        with psycopg.connect(conn_info, row_factory=dict_row) as conn:
            with conn.cursor() as cur:
                # Get the latest checkpoint for the thread
                cur.execute("""
                    SELECT checkpoint 
                    FROM checkpoints 
                    WHERE thread_id = %s 
                    ORDER BY checkpoint_id DESC 
                    LIMIT 1
                """, (thread_id,))
                
                row = cur.fetchone()
                if not row:
                    print(f"No trace found for thread_id: {thread_id}")
                    return

                checkpoint = row['checkpoint']
                # LangGraph checkpoint often has 'channel_values' or similar
                values = checkpoint.get('channel_values', {})
                
                print(f"--- Trace for {thread_id} ---")
                print(f"Query: {values.get('query')}")
                print(f"Rewritten Query: {values.get('rewritten_query')}")
                print(f"Intent: {values.get('user_intent')}")
                
                log = values.get('reasoning_log', [])
                print("\n--- Reasoning Log ---")
                for entry in log:
                    print(f"- {entry}")
                
                v_chunks = values.get('vector_chunks', [])
                print(f"\nVector Chunks: {len(v_chunks)}")
                for i, c in enumerate(v_chunks[:2]):
                    # If it's a Chunk object, it might be serialized
                    print(f"  [{i}] ID: {getattr(c, 'id', 'N/A')}, Dist: {getattr(c, 'score', 'N/A')}")
                
                graph_data = values.get('graph_data', [])
                print(f"Graph Data: {len(graph_data)}")

                rerank_log = values.get('rerank_log', [])
                print("\n--- Rerank Log ---")
                for entry in rerank_log:
                    print(f"- {entry}")

                reranked = values.get('reranked_chunks', [])
                print(f"Reranked Chunks: {len(reranked) if reranked is not None else 0}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    tid = sys.argv[1] if len(sys.argv) > 1 else "playground-7ab731e6"
    check_trace(tid)
