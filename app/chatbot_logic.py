import os
import json
import re
from dotenv import load_dotenv

try:
    from langchain_ollama import ChatOllama, OllamaEmbeddings
    _OLLAMA_IMPORT_ERROR = None
except Exception as exc:
    ChatOllama = None
    OllamaEmbeddings = None
    _OLLAMA_IMPORT_ERROR = str(exc)

load_dotenv()

# local Ollama configurations tailored for 4GB GPU (GTX 1650 Ti) and 8GB RAM
OLLAMA_LLM_MODEL = "gemma2:2b"
OLLAMA_EMBED_MODEL = "nomic-embed-text"
OLLAMA_HOST = "http://localhost:11434"

DOCS_DIR = os.path.join(os.path.dirname(__file__), "chatbot_docs")
os.makedirs(DOCS_DIR, exist_ok=True)
CHROMA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "chroma_db", "chatbot_rag_local"))
os.makedirs(CHROMA_DIR, exist_ok=True)

default_doc = os.path.join(DOCS_DIR, "system_info.txt")
if not os.path.exists(default_doc):
    with open(default_doc, "w") as f:
        f.write("Krishi Mitr is an advanced agricultural smart agent platform. It helps farmers with crop recommendations, smart irrigation, and disease detection. The chatbot is designed to provide actionable agricultural insights.\\n\\nTECHNICAL ARCHITECTURE:\\n- Backend: Python Flask (app/app.py)\\n- Frontend: HTML/CSS/Vanilla JS with Glassmorphism (app/templates/layout.html, index.html)\\n- AI Intelligence: Google Gemini Langchain RAG with FAISS vector store (app/chatbot_logic.py)\\n- Agents: Multiple specialized agents exist in app/agents/ including sustainability_agent.py, crop_recommendation.py, etc.\\n- The chatbot UI is a premium floating widget integrated directly into layout.html, allowing it to seamlessly persist across all pages.")

vector_store = None
vector_backend = "none"
retriever_cache = None


def _extract_project_routes() -> list:
    app_file = os.path.join(os.path.dirname(__file__), "app.py")
    try:
        with open(app_file, "r", encoding="utf-8") as f:
            content = f.read()
        routes = re.findall(r"@app\.route\('([^']+)'", content)
        return sorted(set(routes))
    except Exception:
        return []


def _collect_project_documents() -> list:
    try:
        from langchain_community.document_loaders import TextLoader, DirectoryLoader
    except Exception:
        return []

    routes = _extract_project_routes()
    agent_dir = os.path.join(os.path.dirname(__file__), "agents")
    agent_files = []
    if os.path.isdir(agent_dir):
        for name in os.listdir(agent_dir):
            if name.endswith("_agent.py"):
                agent_files.append(name)

    generated_doc = (
        "PROJECT NAVIGATION KNOWLEDGE\n"
        "These routes are available in Krishi Mitr:\n"
        + "\n".join([f"- {r}" for r in routes[:250]])
        + "\n\nPROJECT AGENTS\n"
        + "\n".join([f"- {a}" for a in sorted(agent_files)])
        + "\n\nKEY PAGE MAPPINGS\n"
        "- Open irrigation agent: /agent/irrigation\n"
        "- Open crop recommendation: /agent/crop\n"
        "- Open fertilizer recommendation: /agent/fertilizer\n"
        "- Open disease prediction: /disease-predict\n"
        "- Open yield page: /yield\n"
        "- Open market trends: /market-trends\n"
        "- Open agri-tech news: /agri-tech-news\n"
        "- Open case studies: /case-studies\n"
        "- Open dashboard: /dashboard\n"
    )

    generated_doc_file = os.path.join(DOCS_DIR, "generated_project_knowledge.txt")
    try:
        with open(generated_doc_file, "w", encoding="utf-8") as f:
            f.write(generated_doc)
    except Exception:
        pass

    documents = []
    try:
        loader = DirectoryLoader(DOCS_DIR, glob="**/*.txt", loader_cls=TextLoader)
        documents.extend(loader.load())
    except Exception:
        documents = []

    return documents


def get_chatbot_status():
    """Return runtime health indicators for chatbot connectivity and RAG readiness."""
    ollama_ready = ChatOllama is not None and OllamaEmbeddings is not None
    
    # Check if local Ollama port is open
    import socket
    ollama_active = False
    try:
        with socket.create_connection(("localhost", 11434), timeout=1):
            ollama_active = True
    except Exception:
        ollama_active = False

    doc_files = []
    if os.path.isdir(DOCS_DIR):
        doc_files = [f for f in os.listdir(DOCS_DIR) if f.lower().endswith(".txt")]

    rag_ready = bool(
        vector_store is not None
        or os.path.exists(os.path.join(CHROMA_DIR, "chroma.sqlite3"))
    )

    return {
        "gemini_configured": ollama_active, # Maps to "Connected OK" in UI if local Ollama port is open!
        "genai_sdk_available": ollama_ready,
        "rag_ready": rag_ready,
        "vector_backend": vector_backend,
        "doc_count": len(doc_files),
        "docs_dir": DOCS_DIR,
        "chroma_dir": CHROMA_DIR,
        "error": _OLLAMA_IMPORT_ERROR or (None if ollama_active else "Ollama service is not running on localhost:11434. Please start Ollama!"),
    }

def get_retriever():
    global vector_store, vector_backend, retriever_cache
    if OllamaEmbeddings is None:
        raise RuntimeError(
            f"Ollama SDK unavailable: {_OLLAMA_IMPORT_ERROR or 'import failed'}"
        )

    try:
        from langchain_community.vectorstores import FAISS, Chroma
        from langchain_text_splitters import RecursiveCharacterTextSplitter
    except Exception as exc:
        raise RuntimeError(f"LangChain components unavailable: {exc}")

    if retriever_cache is not None:
        return retriever_cache

    if vector_store is None:
        # Swap Google embeddings to local Ollama embeddings
        embeddings = OllamaEmbeddings(
            model=OLLAMA_EMBED_MODEL,
            base_url=OLLAMA_HOST
        )
        
        # 1. Try to load existing Chroma index first (avoid re-indexing)
        if os.path.exists(os.path.join(CHROMA_DIR, "chroma.sqlite3")):
            try:
                print(f"[ChatbotLogic] Loading existing local Chroma index from {CHROMA_DIR}...")
                vector_store = Chroma(
                    persist_directory=CHROMA_DIR,
                    embedding_function=embeddings,
                    collection_name="krishi_mitr_local_rag"
                )
                vector_backend = "chroma"
                retriever_cache = vector_store.as_retriever(search_kwargs={"k": 3})
                return retriever_cache
            except Exception as e:
                print(f"[ChatbotLogic] Failed to load existing index: {e}")

        # 2. Fallback: Create index if missing
        print("[ChatbotLogic] Creating new local vector index (First time initialization)...")
        documents = _collect_project_documents()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=80)
        chunks = text_splitter.split_documents(documents)
        if not chunks:
            chunks = text_splitter.create_documents(["Krishi Mitr agricultural platform information."])

        try:
            vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=CHROMA_DIR,
                collection_name="krishi_mitr_local_rag",
            )
            vector_backend = "chroma"
        except Exception as e:
            print(f"[ChatbotLogic] Chroma creation failed, failing back to FAISS: {e}")
            vector_store = FAISS.from_documents(chunks, embeddings)
            vector_backend = "faiss"
            
    retriever_cache = vector_store.as_retriever(search_kwargs={"k": 3})
    return retriever_cache

system_prompt = """You are "Krishi Mitr" — a helpful, practical assistant for farmers and general users.

YOUR PERSONALITY:
- You talk like a warm, experienced farmer elder who genuinely cares about the person asking.
- Use simple, easy Hindi-English (Hinglish) naturally — like "Haan bhai", "Bilkul", "Dekho", "Arre wah".
- Be encouraging: "Bahut accha sawaal hai!", "Tension mat lo, hum hain na!"
- Keep answers practical and actionable — farmers need solutions, not lectures.
- Use farming analogies and relatable language.
- Address the user as "bhai", "dost", or "kisan saathi" naturally.
- Sprinkle relevant emojis sparingly: 🌾 🌱 💧 🐄 🌤️ 🚜

YOUR RESPONSE RULES:
1. Answer the user's question directly and clearly.
2. If the question is about farming, use practical agricultural advice.
3. If the question is outside farming, still answer it instead of refusing.
4. If the user asks for a result, give the result first, then brief context.
5. Avoid extra warnings or repeated disclaimers unless something is genuinely uncertain.

YOUR EXPERTISE AREAS:
- Crop recommendation (which crop for which soil, season, region)
- Soil health (NPK, pH, organic matter, testing)
- Irrigation planning (drip, sprinkler, flood, water management)
- Disease & pest identification and treatment
- Fertilizer guidance (organic and chemical)
- Yield prediction and optimization
- Sustainable farming practices
- Government schemes for farmers (PM-KISAN, MSP, subsidies)
- Market prices and mandi information
- Livestock and dairy basics
- Post-harvest storage and processing
- Weather impact on farming

FORMATTING RULES:
- DO NOT use markdown, bold (**), asterisks (*), or headers (###).
- Write in plain conversational text ONLY.
- Use simple numbers (1, 2, 3) for lists.
- Keep responses concise but thorough — like talking to a friend on the phone.

Context (Krishi Mitr Platform Data):
{context}

Conversation History:
{chat_history}
Human: {input}
AI:"""

import requests
from utils.weather import weather_fetch  # We'll use the robust Open-Meteo powered fetcher

def stream_chat_response(query: str, history: list):
    if ChatOllama is None:
        msg = "Arre bhai, abhi local model setup nahi ho paaya. Langchain Ollama packages install kijiye! 🌾"
        yield f"data: {json.dumps({'token': msg})}\n\n"
        yield "data: [DONE]\n\n"
        return

    # --- WEATHER INJECTION: If query asks about weather, get real-time Open-Meteo data ---
    weather_context = ""
    weather_keywords = ["weather", "mausam", "baarish", "rain", "temperature", "tapman", "humidity"]
    if any(kw in query.lower() for kw in weather_keywords):
        # Default to a general location or try to extract city (simplified for now)
        # In a real app, we'd use NER to find the city. Here we'll default to a regional context if none found.
        temp, hum, is_fallback = weather_fetch("Delhi") # Sample regional context
        if not is_fallback:
            weather_context = f"\nREAL-TIME WEATHER DATA: Current Temperature is {temp}°C and Humidity is {hum}%. Use this data to advise the farmer."

    # Instantiate local Ollama chat model running fully on GPU
    llm = ChatOllama(
        model=OLLAMA_LLM_MODEL,
        base_url=OLLAMA_HOST,
        temperature=0.4
    )
    
    retriever = get_retriever()
    try:
        context_docs = retriever.invoke(query)
        context_text = "\n".join([doc.page_content for doc in context_docs]) + weather_context
    except Exception as e:
        context_text = f"Error retrieving context: {str(e)}" + weather_context
    
    prompt_formatted = system_prompt.format(
        context=context_text,
        chat_history="\n".join([f"Human: {m.get('human', '')}\nAI: {m.get('ai', '')}" for m in history]),
        input=query
    )

    try:
        # Stream response locally
        for chunk in llm.stream(prompt_formatted):
            if chunk.content:
                yield f"data: {json.dumps({'token': chunk.content})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'token': f'Error generating response: {str(e)}'})}\n\n"
        
    yield "data: [DONE]\n\n"
