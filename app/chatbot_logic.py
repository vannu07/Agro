import os
import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import TextLoader, DirectoryLoader
from langchain_community.vectorstores import FAISS, Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

DOCS_DIR = os.path.join(os.path.dirname(__file__), "chatbot_docs")
os.makedirs(DOCS_DIR, exist_ok=True)
CHROMA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "chroma_db", "chatbot_rag"))
os.makedirs(CHROMA_DIR, exist_ok=True)

default_doc = os.path.join(DOCS_DIR, "system_info.txt")
if not os.path.exists(default_doc):
    with open(default_doc, "w") as f:
        f.write("Krishi Mitr is an advanced agricultural smart agent platform. It helps farmers with crop recommendations, smart irrigation, and disease detection. The chatbot is designed to provide actionable agricultural insights.\\n\\nTECHNICAL ARCHITECTURE:\\n- Backend: Python Flask (app/app.py)\\n- Frontend: HTML/CSS/Vanilla JS with Glassmorphism (app/templates/layout.html, index.html)\\n- AI Intelligence: Google Gemini Langchain RAG with FAISS vector store (app/chatbot_logic.py)\\n- Agents: Multiple specialized agents exist in app/agents/ including sustainability_agent.py, crop_recommendation.py, etc.\\n- The chatbot UI is a premium floating widget integrated directly into layout.html, allowing it to seamlessly persist across all pages.")

vector_store = None
vector_backend = "none"


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
    gemini_configured = bool(os.environ.get("GEMINI_API_KEY"))
    doc_files = []
    if os.path.isdir(DOCS_DIR):
        doc_files = [f for f in os.listdir(DOCS_DIR) if f.lower().endswith(".txt")]

    rag_ready = False
    rag_error = None
    try:
        _ = get_retriever()
        rag_ready = True
    except Exception as exc:
        rag_error = str(exc)

    return {
        "gemini_configured": gemini_configured,
        "rag_ready": rag_ready,
        "vector_backend": vector_backend,
        "doc_count": len(doc_files),
        "docs_dir": DOCS_DIR,
        "chroma_dir": CHROMA_DIR,
        "error": rag_error,
    }

def get_retriever():
    global vector_store, vector_backend
    if vector_store is None:
        documents = _collect_project_documents()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(documents)
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=os.environ.get("GEMINI_API_KEY"))
        if not chunks:
            chunks = text_splitter.create_documents(["Krishi Mitr agricultural platform information."])

        # Prefer persistent Chroma DB to keep project knowledge indexed between runs.
        try:
            vector_store = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                persist_directory=CHROMA_DIR,
                collection_name="krishi_mitr_chatbot",
            )
            vector_backend = "chroma"
        except Exception:
            vector_store = FAISS.from_documents(chunks, embeddings)
            vector_backend = "faiss"
    return vector_store.as_retriever(search_kwargs={"k": 3})

system_prompt = """You are Krishi Mitr, the specialized AI Agricultural Chatbot for the Krishi Mitr platform.
You possess vast general knowledge about agriculture, farming, crops, soil, irrigation, and diseases. You MUST use your own extensive knowledge to answer ANY question related to agriculture, farming, or crops.
You MUST strictly ONLY answer questions related to agriculture, farming, crop recommendations, diseases, irrigation, and the Krishi Mitr platform itself.
If a user asks a question that is NOT related to agriculture (e.g., coding, math, geography, politics, etc.), you MUST politely decline to answer, stating that you are an agricultural assistant designed exclusively for agricultural topics.
The provided Context below contains some specific dynamic Krishi Mitr internal data. Use it if relevant, but do not restrict yourself to ONLY the context. Your primary job is to be an expert agronomist for the user.
CRITICAL INSTRUCTION: DO NOT use any markdown formatting, bolding (**), asterisks (*), or headers (###) in your response. Output pure conversational plain text ONLY. Use simple numbers for lists.

Context (Krishi Mitr Specific DB Data):
{context}

Current Conversation:
{chat_history}
Human: {input}
AI:"""

def stream_chat_response(query: str, history: list):
    llm = ChatGoogleGenerativeAI(
        model="gemini-flash-latest",
        google_api_key=os.environ.get("GEMINI_API_KEY"),
        temperature=0.3
    )
    
    retriever = get_retriever()
    try:
        context_docs = retriever.invoke(query)
        context_text = "\n".join([doc.page_content for doc in context_docs])
    except Exception as e:
        context_text = f"Error retrieving context: {str(e)}"
    
    prompt_formatted = system_prompt.format(
        context=context_text,
        chat_history="\n".join([f"Human: {m.get('human', '')}\nAI: {m.get('ai', '')}" for m in history]),
        input=query
    )

    try:
        for chunk in llm.stream(prompt_formatted):
            if chunk.content:
                text_chunk = ""
                if isinstance(chunk.content, list):
                    for part in chunk.content:
                        if isinstance(part, dict) and "text" in part:
                            text_chunk += part["text"]
                        elif isinstance(part, str):
                            text_chunk += part
                else:
                    text_chunk = str(chunk.content)
                
                if text_chunk:
                    yield f"data: {json.dumps({'token': text_chunk})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'token': f'Error generating response: {str(e)}'})}\n\n"
        
    yield "data: [DONE]\n\n"
