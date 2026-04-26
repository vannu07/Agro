# Documentation Generation Plan - Krishi Mitr

This plan outlines the creation of three comprehensive documentation files as requested by the user, covering system design, model performance, and data workflows.

## Proposed Documents

---

### [NEW] [Detailed_System_Design.md](file:///d:/Farm-IQ%20-%20Copy/docs/Detailed_System_Design.md)
This file will serve as the primary architectural document.
- **System Design & Architecture**: Overview of the "Decoupled Agentic Pattern".
- **Requirements**: Functional and Non-functional requirements (Hardware/Software).
- **Use Case Diagram**: Mermaid diagram showing actors (Farmer, Admin, Expert) and interactions.
- **Data Flow Diagrams (DFD)**: Level 0 and Level 1 DFDs using Mermaid.
- **Class Diagram**: High-level structure of `Orchestrator`, `BaseAgent`, and specific agents.
- **Project Structure**: A detailed tree or table of the directory organization.

---

### [NEW] [Model_Performance_Report.md](file:///d:/Farm-IQ%20-%20Copy/docs/Model_Performance_Report.md)
This file will focus on the machine learning aspect of the project.
- **Model Inventory**: List of all models (Crop, Hydration, Yield, Sustain, Disease).
- **Comparison Table**: Metrics (Accuracy, R2, etc.) extracted from the notebooks.
- **Champion Models**: Identification of the best performing models for each task.
- **Technical Logic**: Brief on algorithms used (Random Forest, ResNet9, XGBoost).

---

### [NEW] [Workflow_Data_Lifecycle.md](file:///d:/Farm-IQ%20-%20Copy/docs/Workflow_Data_Lifecycle.md)
This file will describe the operational flow of the system.
- **Data Ingestion**: How data comes from soil telemetry, images, and market APIs.
- **Agentic Loop**: Detailed explanation of the **P.A.O.R (Plan-Act-Observe-Reflect)** cycle.
- **Agent Orchestration**: How the `Orchestrator` passes context between agents (e.g., Crop Recommendation -> Fertilizer Suggestion).
- **Output Generation**: How the LLM reasons over agent outputs to provide natural language advice.

---

## Verification Plan

### Manual Verification
1. **Content Accuracy**: Cross-reference the generated DFDs and Class Diagrams with `orchestrator.py` and `app.py`.
2. **Metric Validation**: Ensure the accuracy numbers in the report match the findings in the Jupyter notebooks.
3. **Diagram Rendering**: Verify that Mermaid diagrams render correctly in a markdown viewer.
4. **Project Structure**: Confirm the project structure matches the current directory listing.
