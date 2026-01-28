import os
from langchain_google_genai import ChatGoogleGenerativeAI

os.environ["GOOGLE_API_KEY"] = "AIzaSyDcNidSS0uoq_LDm19wrsEp_PmraDhh97E"

try:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
    print(llm.invoke("hello").content)
    print("Success with gemini-1.5-flash")
except Exception as e:
    print(f"Failed gemini-1.5-flash: {e}")

try:
    llm = ChatGoogleGenerativeAI(model="gemini-pro")
    print(llm.invoke("hello").content)
    print("Success with gemini-pro")
except Exception as e:
    print(f"Failed gemini-pro: {e}")
