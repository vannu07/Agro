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

## 5. Data Flow Diagrams (DFD)

### 5.1 DFD Level 0: Context Diagram
The Level 0 diagram shows the system as a single process and its interaction with external entities (Farmers, Admins, and External APIs).

```mermaid
graph LR
    User[Farmer/User] -- Soil Data, Images, Queries --> KM((0.0 Krishi Mitr System))
    KM -- Agricultural Advice & Reports --> User
    Admin[Administrator] -- API Keys & Config --> KM
    KM -- System Metrics & Logs --> Admin
    API[Market/Weather APIs] -- Live Data Streams --> KM
    Expert[Agri-Expert] -- Research Documents --> KM
```

### 5.2 DFD Level 1: Detailed Functional Decomposition
The Level 1 diagram breaks down the "Krishi Mitr System" into its core sub-processes, identifying the flow of data between internal logic and data stores.

```mermaid
graph TD
    %% Entities
    F[Farmer]
    EX[Agri-Expert]
    
    %% Processes
    P1[1.0 User Profiling & Auth]
    P2[2.0 Input Processing & Vectorization]
    P3[3.0 Agentic Orchestration Layer]
    P4[4.0 Model Inference Engine]
    P5[5.0 Knowledge Retrieval - RAG]
    P6[6.0 report Generation & LLM Reasoning]

    %% Data Stores
    D1[(User Database)]
    D2[(Model Store - .pkl/.pth)]
    D3[(ChromaDB Vector Store)]
    D4[(Agricultural Knowledge Base)]

    %% Connections
    F -- Credentials --> P1
    P1 <--> D1
    
    F -- Soil/Image/Text --> P2
    P2 -- Cleaned Data --> P3
    
    EX -- Research Docs --> P2
    P2 -- Embeddings --> D3
    
    P3 -- Task Assignment --> P4
    P4 <--> D2
    P4 -- Prediction Result --> P3
    
    P3 -- Semantic Query --> P5
    P5 <--> D3
    P5 <--> D4
    P5 -- Contextual Data --> P3
    
    P3 -- Raw Data + Context --> P6
    P6 -- Final Actionable Advice --> F
```

#### Process Descriptions for Your Teacher:
- **Process 1.0**: Manages user sessions and personalized farm profiles.
- **Process 2.0**: Handles multi-modal inputs. It normalizes sensor data and converts research papers into vector embeddings.
- **Process 3.0**: The "Orchestrator" which uses the P.A.O.R loop to decide which agents (Crop, Disease, etc.) should handle the request.
- **Process 4.0**: Execution of the machine learning models (Random Forest, ResNet9).
- **Process 5.0**: Retrieves domain-specific knowledge from the local vector database (RAG) to ensure the advice is factually correct.
- **Process 6.0**: Uses an LLM to synthesize all technical outputs into easy-to-read advice for the farmer.

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
