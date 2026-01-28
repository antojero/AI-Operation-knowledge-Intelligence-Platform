import os
from langchain_google_genai import ChatGoogleGenerativeAI

os.environ["GOOGLE_API_KEY"] = "AIzaSyDcNidSS0uoq_LDm19wrsEp_PmraDhh97E"

try:
    print("Testing gemini-1.5-flash-001...")
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-001")
    print("Response:", llm.invoke("hello").content)
    print("SUCCESS!")
except Exception as e:
    print(f"FAILED: {e}")
