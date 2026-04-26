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
        ORCH <--> SA[Sustain Agent]
        ORCH <--> CB[RAG Chatbot]
    end
    
    subgraph "Engines & Model Intelligence"
        CA --> CA_M[Random Forest Classifier]
        HA --> HA_M[Random Forest]
        PA --> PA_M[ResNet9 CNN]
        YA --> YA_M[RF Regressor]
        SA --> SA_M[XGBoost]
        CB --> CB_M[OpenAI GPT-4o]
        CB_M --> VEC[ChromaDB Vector Store]
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
graph LR
    subgraph Actors
        F[Farmer]
        E[Agri-Expert]
        A[Admin]
    end

    subgraph "System Use Cases"
        UC1((Predict Optimal Crop))
        UC2((Diagnose Leaf Disease))
        UC3((Consult AI Chatbot))
        UC4((Check Market Trends))
        UC5((Upload Research Docs))
        UC6((Validate AI Advice))
        UC7((Manage API Keys))
        UC8((Analyze Metrics))
    end

    F --> UC1
    F --> UC2
    F --> UC3
    F --> UC4

    E --> UC5
    E --> UC6

    A --> UC7
    A --> UC8
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
