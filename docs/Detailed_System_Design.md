# Detailed System Design & Architecture: Krishi Mitr 🌾

## 1. System Overview
**Krishi Mitr** is an Agentic AI ecosystem designed to bridge the digital divide in agriculture. Unlike traditional static platforms, it utilizes a multi-agent orchestration layer to provide reasoned, context-aware advice for crop selection, disease management, and yield optimization.

---

## 2. System Architecture
The system follows a **Decoupled Agentic Pattern**. A central `Orchestrator` acts as the brain, dispatching tasks to specialized "limbs" (agents) and reflecting on their outputs using a Large Language Model (LLM).

```mermaid
graph TD
    User((Farmer)) <--> UI[Flask Premium UI]
    UI <--> ORCH[Agentic Orchestrator]
    
    subgraph "Intelligent Agents"
        ORCH <--> CA[Crop Agent]
        ORCH <--> HA[Hydration Agent]
        ORCH <--> PA[Pathologist Agent]
        ORCH <--> YA[Yield Agent]
        ORCH <--> SA[Sustainability Agent]
        ORCH <--> CB[RAG Chatbot]
    end
    
    subgraph "Engines & Data"
        CA --> RF[Random Forest]
        PA --> RES[ResNet9 CNN]
        CB --> VEC[ChromaDB Vector Store]
        VEC --> OpenAI[GPT-4o / RAG]
    end
```

---

## 3. System Requirements

### Hardware Requirements
- **Server**: 4GB+ RAM, 2 vCPUs (recommended for model hosting).
- **Client**: Any device with a web browser and camera access for leaf disease scanning.

### Software Requirements
- **Backend**: Python 3.10+, Flask 3.0.x.
- **AI/ML**: Scikit-Learn, PyTorch, LangChain, OpenAI API.
- **Database**: ChromaDB (Vector Store), CSV/Pickle (Persistent Models).

---

## 4. Use Case Analysis
The system addresses three primary actors:
- **Farmer**: Seeks crop, fertilizer, and disease advice.
- **Agri-Expert**: Enriches the RAG knowledge base.
- **Admin**: Monitors system health and API performance.

```mermaid
useCaseDiagram
    actor Farmer
    actor Admin
    actor Expert
    
    Farmer --> (Predict Optimal Crop)
    Farmer --> (Diagnose Leaf Disease)
    Farmer --> (Consult AI Chatbot)
    Farmer --> (Check Market Trends)
    
    Expert --> (Upload Research Docs)
    Expert --> (Validate AI Advice)
    
    Admin --> (Manage API Keys)
    Admin --> (Analyze Metrics)
```

---

## 5. Data Flow Diagram (DFD Level 1)

```mermaid
graph LR
    F[Farmer] -- Soil Data --> CA[Crop Agency]
    CA -- Prediction --> OR[Orchestrator]
    F -- Leaf Image --> PA[Pathologist]
    PA -- Diagnosis --> OR
    OR -- Context --> LLM[OpenAI Reasoning]
    LLM -- Final Advice --> F
```

---

## 6. Project Structure

| Directory | Purpose |
| :--- | :--- |
| `app/` | Core Flask application logic and routes. |
| `app/agents/` | Implementation of specialized AI agents. |
| `models/` | Serialized machine learning models (`.pkl`, `.pth`). |
| `notebooks/` | R&D notebooks for model training and EDA. |
| `static/` | UI assets (Lottie, CSS, JS). |
| `chroma_db/` | Vectorized knowledge base for RAG functionality. |

---

## 7. Class Structure (High-Level)

```mermaid
classDiagram
    class Orchestrator {
        +dispatch(task_type)
        +reflect(agent_output)
        +manage_context()
    }
    class BaseAgent {
        +run(input_data)
        +validate()
    }
    class CropAgent {
        +predict_crop()
        -load_rf_model()
    }
    class ChatbotService {
        +query_rag()
        +stream_response()
    }
    
    Orchestrator *-- BaseAgent
    BaseAgent <|-- CropAgent
    Orchestrator o-- ChatbotService
```
