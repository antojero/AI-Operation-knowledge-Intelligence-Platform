import os
from langchain_openai import ChatOpenAI

os.environ["OPENAI_API_KEY"] = "AIzaSyDcNidSS0uoq_LDm19wrsEp_PmraDhh97E"

try:
    print("Testing Gemini via OpenAI compatibility layer...")
    llm = ChatOpenAI(
        model="gemini-1.5-flash",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key="AIzaSyDcNidSS0uoq_LDm19wrsEp_PmraDhh97E"
    )
    print("Response:", llm.invoke("hello").content)
    print("SUCCESS!")
except Exception as e:
    print(f"FAILED: {e}")
