import sys
import os
import json

# Add app to path
sys.path.append(os.path.join(os.getcwd(), 'app'))

try:
    from chatbot_logic import stream_chat_response
    print("--- LIVE GEMINI CHATBOT TEST ---")
    
    query = "Hi! Tell me one quick fact about rice farming."
    history = []
    
    for chunk in stream_chat_response(query, history):
        # We just print the raw chunks to prove it's alive
        print(chunk, end="", flush=True)

    print("\n-----------------------------")
    print("TEST COMPLETE: If you see 'data: [DONE]', the chatbot is working perfectly!")

except Exception as e:
    print(f"\nERROR: {e}")
