from langchain_community.tools import DuckDuckGoSearchRun
import traceback

print("Testing DuckDuckGoSearchRun...")
try:
    tool = DuckDuckGoSearchRun()
    res = tool.invoke("test")
    print(f"Result: {res[:100]}...")
except Exception:
    traceback.print_exc()
