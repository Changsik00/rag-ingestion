import asyncio
import os
import psycopg
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from dotenv import load_dotenv

load_dotenv()

async def debug_state(thread_id: str):
    # Connect to Postgres
    conn_str = f"host={os.getenv('POSTGRES_HOST')} port={os.getenv('POSTGRES_PORT')} dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')}"
    
    try:
        async with await psycopg.AsyncConnection.connect(conn_str) as conn:
            checkpointer = AsyncPostgresSaver(conn)
            config = {"configurable": {"thread_id": thread_id}}
            state = await checkpointer.aget(config)
            
            if not state:
                print(f"State not found for {thread_id}")
                return
                
            # For newer LangGraph, state might have channel_values
            # but usually it has 'values' when retrieved via aget
            values = state.get("channel_values", state.get("values", {}))
            print(f"Keys in values: {list(values.keys())}")
            
            rerank_log = values.get("rerank_log")
            print(f"rerank_log type: {type(rerank_log)}")
            if rerank_log is not None:
                print(f"rerank_log count: {len(rerank_log)}")
                if len(rerank_log) > 0:
                    import json
                    # Print first item as JSON to check if it's a dict
                    print(f"First item: {rerank_log[0]}")
            else:
                print("rerank_log is missing (None)")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    tid = sys.argv[1] if len(sys.argv) > 1 else "playground-7dfcc551"
    asyncio.run(debug_state(tid))
