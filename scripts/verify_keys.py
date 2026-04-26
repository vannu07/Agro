import os
import sys
from langchain_openai import ChatOpenAI
import google.generativeai as genai

OPENAI_KEY = "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"
GEMINI_KEY = "AIzaSyABJFCFHk7epX29t6RAfiZGCL-GCJRkHRk"

def verify_openai():
    print("[TESTING] OpenAI Key...")
    try:
        llm = ChatOpenAI(openai_api_key=OPENAI_KEY, model="gpt-3.5-turbo")
        response = llm.invoke("Hi")
        print("PASSED: OpenAI Key is valid.")
        return True
    except Exception as e:
        print(f"FAILED: OpenAI Key invalid: {e}")
        return False

def verify_gemini():
    print("[TESTING] Gemini Key...")
    try:
        genai.configure(api_key=GEMINI_KEY)
        print("Available models:")
        models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        for m in models:
            print(f" - {m}")
        
        # Try a standard one
        test_model = "models/gemini-1.5-flash" if "models/gemini-1.5-flash" in models else models[0]
        print(f"Trying model: {test_model}")
        model = genai.GenerativeModel(test_model)
        response = model.generate_content("Hi")
        print("PASSED: Gemini Key is valid.")
        return True
    except Exception as e:
        print(f"FAILED: Gemini Key invalid: {e}")
        return False

if __name__ == "__main__":
    verify_openai()
    verify_gemini()
