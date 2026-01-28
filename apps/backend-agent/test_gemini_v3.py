import os
from langchain_google_genai import ChatGoogleGenerativeAI

os.environ["GOOGLE_API_KEY"] = "AIzaSyDcNidSS0uoq_LDm19wrsEp_PmraDhh97E"

try:
    print("Testing gemini-2.0-flash-exp...")
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp")
    print("Response:", llm.invoke("hello").content)
    print("SUCCESS!")
except Exception as e:
    print(f"FAILED: {e}")
