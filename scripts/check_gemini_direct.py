import os
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print(f"Testing with key: {api_key[:10]}...")

try:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)
    res = llm.invoke("Say 'System Operational'")
    print(f"SUCCESS: {res.content}")
except Exception as e:
    print(f"FAILURE: {e}")
