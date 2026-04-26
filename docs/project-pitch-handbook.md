# Farm-IQ Pitch Handbook

## 1) One-line Pitch
Farm-IQ is an AI-powered agriculture decision platform that combines six specialized agents, machine learning models, deep learning disease diagnosis, and Gemini + RAG chatbot support to help farmers make better crop, fertilizer, irrigation, yield, and sustainability decisions.

## 2) Problem Statement
Indian farmers often make high-impact decisions (crop choice, irrigation timing, fertilizer use, disease response, selling strategy) with fragmented information.
Farm-IQ solves this by combining:
- Structured ML predictions for farm operations
- Visual disease diagnosis with deep learning
- Market and advisory pages for practical action
- A domain-restricted chatbot with project-aware RAG

## 3) Solution Overview
Farm-IQ is a Flask-based platform with:
- Multi-agent orchestration layer
- Service pages for each agricultural workflow
- Data-backed market trends and live-style insights
- RAG chatbot using Gemini + vector retrieval

Main app entry and routes live in app/app.py.

## 4) Core Services (6 Agents)

### 4.1 Crop Advisor Agent
Goal:
- Recommend best crop from NPK + weather + pH + rainfall inputs.

Model used:
- RandomForest model artifact: models/RandomForest.pkl
- Runtime loader: app/models_registry.py (get_crop_model)
- Agent logic: app/agents/crop_agent.py

Fallback:
- If model not available, Gemini text fallback in agent.

Output:
- Top crop recommendation
- Confidence and explanation
- Memory write for downstream agents (recommended_crop)

### 4.2 Fertilizer Agent (Nutrient Lab)
Goal:
- Identify nutrient imbalance and suggest fertilizer strategy.

Method used:
- Dataset logic over Data-processed/fertilizer.csv
- Rule + lookup based on nutrient gap and crop profile
- Agent file: app/agents/fertilizer_agent.py

Fallbacks:
- If crop not found in CSV, Gemini fallback recommendation
- If dataset unavailable, error-safe response

Output:
- Fertilizer type / NPK formula
- Dosage guidance
- Action notes

### 4.3 Disease Agent (Plant Pathologist)
Goal:
- Diagnose plant disease from leaf image or symptom text.

Models used:
- Primary image model: ResNet9 weights in models/plant_disease_model.pth
- Runtime loader: app/models_registry.py (get_disease_model)
- Agent file: app/agents/disease_agent.py

Fallback path:
- If image not provided, symptom-based Gemini text diagnosis path.

Output:
- Disease class
- Treatment advice from disease dictionary
- Severity guidance

### 4.4 Yield Agent (Precision Yield)
Goal:
- Estimate expected yield for crop-state-season.

Current runtime strategy:
- Primary logic from historical data utility: app/utils/yield_logic.py
- Data source file: Data-raw/crop_yield.csv
- Agent wrapper: app/agents/yield_agent.py

Model artifacts present:
- models/XGBoost.pkl and precision yield artifacts in models/

Fallback:
- If historical filter fails, Gemini fallback estimate.

Output:
- Yield per hectare
- Total projected production
- Grade/comparison summary

### 4.5 Sustainability Agent (Sustain Master)
Goal:
- Suggest crop rotation and long-term soil health strategy.

Method:
- Hybrid approach in app/utils/sustainability.py
- Tries ML artifacts first
- Falls back to strong heuristic rotation logic if artifacts not available

Artifacts expected by utility:
- sustain_recommend_model.pkl, sustain_yield_model.pkl, scalers/encoders/features

Current repository note:
- models folder includes sustain_master_* artifacts
- Utility currently expects sustain_recommend_* naming
- If expected files are absent, heuristic fallback is used (safe behavior)

Output:
- Next crop suggestion
- Soil analysis explanation
- Sustainability tips

### 4.6 Irrigation Agent (Hydration Agent)
Goal:
- Predict irrigation urgency and water requirement.

Model and pipeline:
- ML artifacts loaded in app/utils/irrigation.py:
  - models/hydration_model.pkl
  - models/hydration_scaler.pkl
  - models/hydration_encoders.pkl
  - models/hydration_features.pkl
- Agent logic in app/agents/irrigation_agent.py

Design detail:
- Uses model status classes (immediate/moderate/no irrigation)
- Then applies deterministic water estimator for fast liters/day output

Fallback:
- If model inference fails, fallback rule-based irrigation recommendation.

Output:
- Daily water liters
- Frequency and time window
- Status severity and action notes

## 5) Orchestration and Agentic Loop
Orchestrator:
- File: app/orchestrator.py
- Supports direct dispatch, smart dispatch, and auto-trigger chaining

Agentic lifecycle (all agents):
- PLAN -> ACT -> OBSERVE -> REFLECT
- Implemented in app/agents/base.py

Shared memory:
- AgentMemory singleton stores cross-agent context:
  - recommended crop
  - soil context
  - fertilizer/irrigation advice

Auto chaining behavior:
- After crop recommendation, orchestrator can trigger fertilizer + irrigation in background.

## 6) Chatbot + RAG Workflow (Complete Pipeline)
Chatbot engine:
- File: app/chatbot_logic.py

LLM:
- Chat model: Gemini flash variant via langchain_google_genai
- Embeddings: models/gemini-embedding-001

RAG knowledge sources:
- app/chatbot_docs/*.txt
- auto-generated project route and agent knowledge text

Vector store strategy:
- Preferred: Chroma persistent DB at chroma_db/chatbot_rag
- Fallback: FAISS in-memory index

Retrieval flow:
1. User query comes to /api/chatbot/stream
2. Retriever gets top-k chunks (k=3)
3. Context + chat history are injected into system prompt
4. Gemini streams response token-by-token

Operational observability:
- /api/chatbot/status returns:
  - gemini_configured
  - rag_ready
  - vector_backend (chroma/faiss)
  - doc_count and paths

Domain safety behavior:
- Prompt restricts bot to agriculture-related topics.

## 7) Data Sources and Dataset Lineage

### Primary documented sources
From README.md:
- Crop recommendation dataset: Kaggle crop recommendation dataset
- Disease dataset: New Plant Diseases Dataset (Kaggle)
- Fertilizer dataset: project dataset CSV

### Additional repository data sources
- Data-raw/crop_yield.csv used by yield utility
- Data-processed/fertilizer.csv used by fertilizer agent
- Data-processed/cropdata_updated.csv used in hydration training scripts
- Data-processed/market_trend.csv and related files used for market features

### Data acquisition helper scripts
- Extra/download_data.py
- Extra/organize_data.py

## 8) Model Selection and "Failed Model -> Final Model" Narrative
This is the exact story you can pitch confidently:

1. Multi-model benchmarking for hydration:
- Script compares RandomForest, GradientBoosting, and XGBoost
- Champion selected based on best accuracy/F1
- Exported as hydration_model.pkl with scaler/encoders/features
- Scripts: Extra/train_hydration.py and Extra/train_hydration_v2.py

2. Crop model standardization:
- Repository contains multiple classical artifacts (DecisionTree, NB, SVM, RF)
- Runtime selected RandomForest as stable production default
- If model artifact is missing, Gemini fallback prevents hard failure

3. Disease model choice:
- ResNet9 selected for leaf image classification on 38 classes
- If image flow is unavailable, text-symptom fallback ensures continuity

4. Yield reliability strategy:
- Utility-first historical regression logic used for robust structured output
- Optional model artifacts available, AI fallback for sparse coverage

5. Sustainability resilience:
- ML-first attempt when expected artifacts are present
- Heuristic fallback ensures advisory continuity if artifact mismatch/absence occurs

6. RAG backend resilience:
- Chroma preferred for persistence and continuity
- FAISS fallback if Chroma init fails

This gives strong production reliability: no single-model hard dependency for core user journeys.

## 9) Feature Set You Can Pitch
- Modern web platform with dedicated pages for all services
- Premium services page aggregating all 6 agents
- Dashboard and market trends with dynamic summaries
- Agri-tech news page with live-feed capable pipeline + fallback
- Case studies and about page with dynamic counters/signals
- Global chatbot widget with shortcut and status indicators
- API endpoints for agent invocation and chatbot streaming

## 10) API and Workflow Surface
Main functional patterns:
- Page routes for user journeys
- POST prediction routes for each domain
- Agent APIs:
  - /api/agent/<agent_name>
  - /api/agent/smart
- Chat APIs:
  - /api/chatbot/status
  - /api/chatbot/stream
  - /api/chatbot/feedback

## 11) Stack Summary
Backend:
- Python, Flask
- Pandas, NumPy, scikit-learn, XGBoost
- PyTorch + torchvision for disease model

AI layer:
- Gemini via Google GenAI SDK (routing + reflection + fallbacks)
- LangChain for chat + embeddings + retrieval
- Chroma/FAISS vector store

Frontend:
- Jinja templates + HTML/CSS/JS
- Bootstrap + animation-rich UI patterns

Data + persistence:
- CSV data lake style in Data-raw and Data-processed
- Chroma persistent index directory

## 12) End-to-End Pipeline (Simple Pitch Version)
1. User provides farm inputs or image
2. Orchestrator dispatches to the relevant agent
3. Agent executes PLAN/ACT/OBSERVE/REFLECT loop
4. Model or heuristic returns actionable recommendation
5. Shared memory updates context for next agents
6. Optional chained agents run for fuller analysis
7. User sees recommendation + explanation + immediate actions
8. Chatbot can answer follow-up via Gemini + RAG context

## 13) Risk Management and Reliability Design
- Multi-level fallback strategy in every critical service
- Model artifact lazy loading to reduce startup load
- Safe behavior when data subset is empty
- Vector backend fallback (Chroma -> FAISS)
- Chatbot status endpoint for runtime diagnostics

## 14) Known Gaps You Can Transparently Mention
- Some artifact naming conventions in sustainability path should be aligned
- Confidence values are partly heuristic placeholders in some agents
- Production-grade monitoring and CI can be expanded
- Certain legacy imports (openai) are optional and can be cleaned

## 15) High-value Q&A Prep (Ready Answers)

Q1. Why multi-agent instead of one giant model?
A. It improves modularity, debuggability, and fallback control. Each domain has specialized logic and can degrade gracefully independently.

Q2. How do you prevent total failure if one model breaks?
A. Every critical path has fallback logic: alternate ML path, heuristic path, or Gemini path. Chat RAG also has vector backend fallback.

Q3. Why Chroma and FAISS both?
A. Chroma gives persistence across restarts; FAISS provides robust fallback so retrieval remains available even if persistent DB init fails.

Q4. How do you handle data sparsity for yield prediction?
A. Progressive filtering (state+crop+season -> state+crop -> crop-only) and a fallback estimate path ensure output continuity.

Q5. How do you keep recommendations explainable?
A. Each agent returns reflection with key factors, immediate actions, and warnings in addition to the primary prediction.

Q6. Is this only prototype-level or production-aware?
A. It started as POC but now has production-aware architecture patterns: orchestrator, resilient fallbacks, health endpoints, and modular services.

## 16) Demo Flow for Presentation (5-7 Minutes)
1. Open Home and show Services page navigation.
2. Run Crop recommendation input and show result.
3. Show Fertilizer and Irrigation continuity.
4. Show Disease image diagnosis output.
5. Open Market Trends and Agri-tech News.
6. Open chatbot and ask project-specific query.
7. Show /api/chatbot/status for backend trust.

## 17) Suggested Next Upgrades (If Asked)
- Add API-keyed premium news providers and caching
- Standardize sustainability artifact names and retrain pipeline
- Add structured experiment tracking for model comparisons
- Add formal model confidence calibration and drift alerts
- Add unit/integration tests for all agent fallbacks

---
This handbook is designed so you can answer both technical and product questions confidently during project pitching, reviews, viva, or interviews.
