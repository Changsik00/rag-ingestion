import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool

from app.interfaces.mcp.server import ingest_url, search_knowledge_base

# Load Env
load_dotenv()

# Wrapper to make FastMCP tools compatible with LangChain Agent for testing
# FastMCP decorators might return objects that are not directly callable or need unwrapping
# But usually the original function is accessible or the wrapper is callable.
# Let's clean wrap them.

@tool
async def agent_ingest_url(url: str) -> str:
    """Ingest a web URL into the knowledge base."""
    # Direct call to the async function defined in server.py
    # Note: ingest_url in server.py is decorated with @mcp.tool()
    return await ingest_url(url)

@tool
async def agent_search(query: str) -> str:
    """Search the knowledge base."""
    return await search_knowledge_base(query)

async def main():
    print("--- Starting Agentic Verification ---")
    
    # 1. Setup LLM
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("Error: GEMINI_API_KEY not found in .env")
        return

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp", 
        temperature=0,
        google_api_key=gemini_key
    )
    
    # 2. Bind Tools
    tools = [agent_ingest_url, agent_search]
    llm_with_tools = llm.bind_tools(tools)
    print(f"Tools bound: {[t.name for t in tools]}")
    
    # 3. Scenario: Ingest a URL and asking about it
    test_url = "https://news.ycombinator.com"
    query = f"Rules: You MUST use the 'agent_ingest_url' tool to fetch the real-time content. Do not use internal knowledge.\nTask: Read {test_url} and list the top 3 headlines."
    
    print(f"\nUser: {query}")
    
    # 4. Agent Loop (Manual)
    messages = [HumanMessage(content=query)]
    
    # Turn 1: LLM decides to call tool
    ai_msg_1 = await llm_with_tools.ainvoke(messages)
    messages.append(ai_msg_1)
    
    if ai_msg_1.tool_calls:
        print(f"\nAI decided to call tools: {ai_msg_1.tool_calls}")
        
        for tool_call in ai_msg_1.tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["args"]
            
            tool_output = "Unknown Tool"
            if tool_name == "agent_ingest_url":
                print(f"Executing ingest_url({tool_args})...")
                tool_output = await agent_ingest_url.ainvoke(tool_args)
            elif tool_name == "agent_search":
                print(f"Executing search({tool_args})...")
                tool_output = await agent_search.ainvoke(tool_args)
                
            print(f"Tool Output: {tool_output}")
            
            # Append Tool Message
            from langchain_core.messages import ToolMessage
            messages.append(ToolMessage(tool_call_id=tool_call["id"], content=str(tool_output)))
            
        # Turn 2: LLM generates answer based on tool output
        ai_msg_2 = await llm_with_tools.ainvoke(messages)
        print(f"\nFinal Answer: {ai_msg_2.content}")
    else:
        print("AI did not call any tools.")

if __name__ == "__main__":
    asyncio.run(main())
