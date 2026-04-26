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
        ORCH <--> FA[Fertilizer Agent]
        ORCH <--> HA[Hydration Agent]
        ORCH <--> PA[Pathologist Agent]
        ORCH <--> YA[Yield Agent]
        ORCH <--> SA[Sustain Agent]
        ORCH <--> CB[RAG Chatbot]
    end
    
    subgraph "Engines & Model Intelligence"
        CA --> CA_M[Random Forest Classifier]
        FA --> FA_M[Expert System CSV Logic]
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

### 5.2 DFD Level 1: Functional Decomposition of Krishi Mitr
The Level 1 diagram breaks down the system into its operational components, showing how data flows through the specialized **Agentic Intelligence Layer**.

```mermaid
graph TD
    %% Entities
    User[Farmer/Admin]
    Expert[Agri-Expert]
    
    %% Main Control Processes
    P1[1.0 Request Ingestion & Parsing]
    P2[2.0 Task Orchestration - P.A.O.R Loop]
    
    %% Specialized Agent Sub-Processes
    subgraph "Agentic Intelligence Layer"
        A1[3.1 Pathologist - Image Analysis]
        A2[3.2 Crop Advisor - Soil Metrics]
        A3[3.3 Fertilizer - NPK Gap Analysis]
        A4[3.4 Hydration - Moisture Prediction]
        A5[3.5 Yield Forecasting - History Analysis]
        A6[3.6 Sustain Master - Health Check]
    end
    
    %% Synthesis & Output
    P4[4.0 Knowledge Retrieval - RAG]
    P5[5.0 LLM Reflection & report Synthesis]

    %% Data Stores
    D1[(System Databases - SQLite/CSV)]
    D2[(Model Registry - .pkl/.pth)]
    D3[(ChromaDB Vector Store)]

    %% High-Fidelity Data Flows
    User -- Soil/Image/Query --> P1
    P1 -- Normalized Data --> P2
    P2 <--> D1
    
    %% Orchestration Dispatch
    P2 -- Dispatch --> A1
    P2 -- Dispatch --> A2
    P2 -- Dispatch --> A3
    P2 -- Dispatch --> A4
    P2 -- Dispatch --> A5
    P2 -- Dispatch --> A6
    
    %% Intelligence Feedback
    A1 <--> D2
    A2 <--> D2
    A3 <--> D2
    A4 <--> D2
    A5 <--> D2
    A6 <--> D2
    
    A1 & A2 & A3 & A4 & A5 & A6 -- Agent Insights --> P2
    
    %% RAG Enrichment
    Expert -- Guidelines/Research --> P4
    P4 <--> D3
    P2 -- Semantic Request --> P4
    P4 -- Domain Context --> P2
    
    %% Final Output Flow
    P2 -- Aggregated Context --> P5
    P5 -- Actionable Agri-Report --> User
```

#### Detailed Process Descriptions (For Teacher Discussion):
- **1.0 Request Ingestion**: Captures multi-modal inputs (GPS, Soil NPK, Leaf Images). It performs data validation before passing it to the brain.
- **2.0 Orchestrator (P.A.O.R)**: This is the central controller. It **Plans** which agents to call, **Acts** by dispatching tasks, **Observes** the results, and **Reflects** using an LLM to ensure accuracy.
- **3.x Agent Sub-processes**: These are the engine rooms. They load specific ML models from `D2: Model Registry` to perform inference. This separation allows the system to scale—adding a new "Market Agent" simply requires adding another sub-process here.
- **4.0 RAG Retrieval**: This process connects the system to the real world. It pulls information from authorized research papers (stored as vectors) to ground the AI's advice in science.
- **5.0 Output Synthesis**: The final stage where complex mathematical predictions are translated into human-readable, multilingual agricultural advice.

---

## 6. Entity Relationship Diagram (ERD)
The logical data model illustrates how user profiles, field sensor telemetry, and AI-driven predictions are interconnected within the **Krishi Mitr** ecosystem.

```mermaid
erDiagram
    USER ||--o{ FARM_PROFILE : "manages"
    FARM_PROFILE ||--o{ SENSOR_READING : "produces"
    USER ||--o{ PREDICTION_HISTORY : "initiates"
    PREDICTION_HISTORY ||--|| RECOMMENDATION_REPORT : "generates"
    
    USER {
        int id PK
        string username
        string region
        string created_at
    }
    
    FARM_PROFILE {
        int id PK
        int user_id FK
        string soil_type
        float area_hectares
        string previous_crops
    }
    
    SENSOR_READING {
        int id PK
        int profile_id FK
        float N
        float P
        float K
        float pH
        float moisture
        datetime timestamp
    }
    
    PREDICTION_HISTORY {
        int id PK
        int user_id FK
        string agent_type
        json input_payload
        json output_result
        float confidence
        datetime timestamp
    }
    
    RECOMMENDATION_REPORT {
        int id PK
        int prediction_id FK
        text explanation
        text immediate_actions
        string status
    }
```

---

## 7. Project Structure

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
