import sys
import os
import json

# Add app to path
sys.path.append(os.path.join(os.getcwd(), 'app'))

try:
    from chatbot_logic import stream_chat_response
    print("--- Testing Gemini Chatbot Streaming ---")
    
    query = "What is Farm-IQ and how does it help with irrigation?"
    history = []
    
    response_started = False
    full_response = ""
    
    for chunk in stream_chat_response(query, history):
        if chunk.startswith("data: "):
            data_str = chunk[6:].strip()
            if data_str == "[DONE]":
                break
            try:
                token_raw = data.get("token", "")
                token_text = ""
                if isinstance(token_raw, str):
                    token_text = token_raw
                elif isinstance(token_raw, list) and len(token_raw) > 0:
                    token_text = token_raw[0].get("text", "")
                elif isinstance(token_raw, dict):
                    token_text = token_raw.get("text", "")

                if token_text:
                    if not response_started:
                        print("Response started: ", end="", flush=True)
                        response_started = True
                    print(token_text, end="", flush=True)
                    full_response += token_text
            except:
                pass
                
    print("\n\n--- Verification Summary ---")
    if len(full_response) > 50:
        print("STATUS: PASSED (Robust response received)")
        print(f"Response Length: {len(full_response)} characters")
    else:
        print("STATUS: FAILED (Response too short or empty)")
        sys.exit(1)

except Exception as e:
    print(f"CRITICAL FAILURE: {e}")
    sys.exit(1)
