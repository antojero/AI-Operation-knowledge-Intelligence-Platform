from typing import TypedDict, Annotated, List, Union
from typing_extensions import TypedDict
from langchain_ollama import ChatOllama
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
import operator
from dotenv import load_dotenv
import os

from app.tools.search import search_tool
from app.tools.scrape import scrape_tool
from app.tools.retrieve import retrieval_tool

load_dotenv()

# Define State
class AgentState(TypedDict):
    task: str
    messages: Annotated[List[BaseMessage], operator.add]
    final_response: str
    plan: str
    revision_number: int
    max_revisions: int

# Define Tools
tools = [search_tool, scrape_tool, retrieval_tool]

# Define Model
# Check for Gemini API Key first
google_api_key = os.environ.get("GOOGLE_API_KEY")

if google_api_key:
    from langchain_google_genai import ChatGoogleGenerativeAI, HarmBlockThreshold, HarmCategory
    print("[INFO] Using Google Gemini Flash (Latest)")
    
    system_instruction_text = """You are a highly efficient AI Research Agent. 
    Your goal is to answer the user's task accurately using the tools provided.
    
    AVAILABLE TOOLS:
    1. retrieve_memory: ALWAYS use this first if the query is about company-specific files, internal documents, or something that sounds like it should be in the knowledge base (e.g., "hrms file", "policy", "project x").
    2. search_tool: Use this for general web information, current events, or public data.
    3. scrape_tool: Use this to get detailed content from a specific URL.
    
    GUIDELINES:
    - **PRIORITY 1:** ALWAYS check `retrieve_memory` FIRST. The user implies "from this file" or "database", so you MUST look there.
    - **PRIORITY 2:** Only use `search_tool` (Web) if `retrieve_memory` yields absolutely NO results after a good attempt.
    - **CITATION:** In your final answer, explicitly state: "Based on the file [Document Title]..." if you found it in memory.
    - If the tool returns "No relevant documents found", inform the user you checked the database but found nothing, then ask if they want a web search.
    - Do NOT call the same tool with the same query repeatedly.
    - Provide a final answer immediately after finding the data.
    """
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-001",
        google_api_key=google_api_key,
        temperature=0.1,
        max_retries=5,
        system_instruction=system_instruction_text,
        safety_settings={
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        }
    )
else:
    # Ensure OLLAMA_BASE_URL is accessible (e.g. host.docker.internal)
    # Using Qwen2.5:3b - smaller, faster, and supports tool calling
    print("[INFO] Using Local Ollama (Qwen2.5:3b)")
    ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
    llm = ChatOllama(model="qwen2.5:3b", temperature=0, base_url=ollama_base_url) 

model = llm.bind_tools(tools)

def filter_messages(messages: List[BaseMessage]) -> List[BaseMessage]:
    """
    Ensure strict Gemini message history format:
    - User must start (if implicit system ignored).
    - Checks for consecutive AI messages and merges them if possible.
    - Ensures proper turn taking.
    """
    if not messages:
        return []
        
    valid_messages = []
    
    for msg in messages:
        # If list is empty, just add
        if not valid_messages:
            valid_messages.append(msg)
            continue
            
        last_msg = valid_messages[-1]
        
        # Check for consecutive AI messages
        if isinstance(msg, AIMessage) and isinstance(last_msg, AIMessage):
            # Merge logic
            new_content = last_msg.content
            if msg.content:
                if isinstance(new_content, str) and isinstance(msg.content, str):
                    new_content += "\n" + msg.content
                else:
                    new_content = msg.content # Prefer newer if complex? safely fallback
            
            # Merge tool calls
            new_tool_calls = (last_msg.tool_calls or []) + (msg.tool_calls or [])
            
            # Create consolidated message
            merged_msg = AIMessage(
                content=new_content,
                tool_calls=new_tool_calls,
                id=last_msg.id,
                response_metadata=msg.response_metadata or last_msg.response_metadata
            )
            # Replace the last one
            valid_messages[-1] = merged_msg
            print(f"[DEBUG] Merged consecutive AIMessages. Tool Calls: {len(new_tool_calls)}")
        else:
            valid_messages.append(msg)
            
    return valid_messages

# Nodes
def call_agent(state: AgentState):
    messages = state.get('messages', [])
    
    # Add system prompt if not present
    # Init messages if empty
    if not messages:
        messages = [HumanMessage(content=state['task'])]
    
    # Pre-flight sanitation for Gemini 400 error
    # ensure no malformed tool sequences
    final_messages = filter_messages(messages)
     
    print(f"[DEBUG] Calling model with {len(final_messages)} messages")
    # Debug print
    # for i, m in enumerate(final_messages):
    #     print(f"  [{i}] {type(m)} {str(m.content)[:30]}...")

    response = model.invoke(final_messages)
    print(f"[DEBUG] Model response - Tool calls: {len(response.tool_calls) if response.tool_calls else 0}, Content length: {len(response.content) if response.content else 0}")
    
    # Update state
    res_update = {"messages": [response]}
    
    # If the model gives a final answer (no tool calls), populate final_response
    if not response.tool_calls:
        res_update["final_response"] = response.content
        print(f"[DEBUG] Final response set: {response.content[:100]}...")
        
    return res_update

def should_continue(state: AgentState):
    last_message = state['messages'][-1]
    if last_message.tool_calls:
        print(f"[DEBUG] Continuing to tools - {len(last_message.tool_calls)} tool calls")
        return "continue"
    print("[DEBUG] Ending workflow")
    return "end"

# Graph Construction
workflow = StateGraph(AgentState)

workflow.add_node("agent", call_agent)
workflow.add_node("tools", ToolNode(tools))

workflow.set_entry_point("agent")

workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tools",
        "end": END
    }
)

workflow.add_edge("tools", "agent")

# Checkpointer (using memory for now, PostgreCheckpointer in main.py)
from langgraph.checkpoint.memory import MemorySaver
checkpointer = MemorySaver()

# Add recursion limit to prevent infinite loops
app = workflow.compile(checkpointer=checkpointer, debug=True)
