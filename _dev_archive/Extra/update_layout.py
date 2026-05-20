import sys

with open(r'd:\Farm-IQ - Copy\app\templates\layout.html', 'r', encoding='utf-8') as f:
    text = f.read()

with open('widget_patch.html', 'r', encoding='utf-8') as f:
    widget = f.read()

start_marker = "<!-- FarmAI Chatbot Widget Link -->"
end_marker = """    appendMessage("FarmAI", "There was a problem reaching the assistant.");
  }
}
</script>"""

start_idx = text.find(start_marker)
end_idx = text.find(end_marker)

if start_idx != -1 and end_idx != -1:
    end_idx += len(end_marker)
    # Perform the replacement
    new_text = text[:start_idx] + widget + text[end_idx:]
    with open(r'd:\Farm-IQ - Copy\app\templates\layout.html', 'w', encoding='utf-8') as f:
        f.write(new_text)
    print("SUCCESS: layout.html has been updated with the premium chatbot widget.")
else:
    print(f"FAILED: Could not find markers. Start={start_idx}, End={end_idx}")
