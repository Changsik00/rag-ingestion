import asyncio
import os
import psycopg
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from dotenv import load_dotenv

load_dotenv()

async def inspect_session(thread_id: str):
    conn_str = f"host={os.getenv('POSTGRES_HOST')} port={os.getenv('POSTGRES_PORT')} dbname={os.getenv('POSTGRES_DB')} user={os.getenv('POSTGRES_USER')} password={os.getenv('POSTGRES_PASSWORD')}"
    
    try:
        async with await psycopg.AsyncConnection.connect(conn_str) as conn:
            checkpointer = AsyncPostgresSaver(conn)
            config = {"configurable": {"thread_id": thread_id}}
            state = await checkpointer.aget(config)
            
            if not state:
                print(f"❌ State not found for thread_id: {thread_id}")
                return
            
            # Extract values
            values = {}
            checkpoint = getattr(state, "checkpoint", None)
            if checkpoint:
                values = getattr(checkpoint, "channel_values", getattr(checkpoint, "values", {}))
            elif isinstance(state, dict):
                values = state.get("values", state.get("channel_values", {}))
            
            print(f"✅ State loaded for {thread_id}")
            print(f"Keys: {list(values.keys())}")
            
            if "rerank_log" in values:
                print(f"Rerank Log Count: {len(values['rerank_log'])}")
            else:
                print("⚠️ rerank_log is missing")
                
            if "context_data" in values:
                cd = values["context_data"]
                print(f"Context Data Keys: {list(cd.keys()) if isinstance(cd, dict) else 'Not a dict'}")
            else:
                print("⚠️ context_data is missing")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    # The user mentioned 'layground-cff9cc65' but likely meant 'playground-cff9cc65'
    tid = sys.argv[1] if len(sys.argv) > 1 else "playground-cff9cc65"
    asyncio.run(inspect_session(tid))
