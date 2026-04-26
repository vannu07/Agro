# \ud83d\udcc1 Logical ER Diagram: Krishi Mitr

This diagram represents the logical schema of the Krishi Mitr ecosystem in **Chen's Notation**, emphasizing the relationships and attributes of each entity.

```mermaid
graph TD
    %% Entities (Rectangles)
    FARMER[FARMER]
    PROFILE[FARM PROFILE]
    SENSOR[SENSOR DATA]
    PRED[AGENT PREDICTION]
    REPORT[REPORT]

    %% Relationships (Diamonds)
    MANAGES{Manages}
    PRODUCES{Produces}
    INITIATES{Initiates}
    GENERATES{Generates}

    %% Attributes for Farmer (Ovals)
    F1((Id)) --- FARMER
    F2((Username)) --- FARMER
    F3((Region)) --- FARMER

    %% Attributes for Profile (Ovals)
    P1((Id)) --- PROFILE
    P2((Soil Type)) --- PROFILE
    P3((Area)) --- PROFILE

    %% Attributes for Sensor Data
    S1((Id)) --- SENSOR
    S2((N-P-K)) --- SENSOR
    S3((pH)) --- SENSOR
    S4((Moisture)) --- SENSOR

    %% Attributes for Prediction
    PR1((Id)) --- PRED
    PR2((Agent Type)) --- PRED
    PR3((Confidence)) --- PRED

    %% Attributes for Report
    R1((Id)) --- REPORT
    R2((Advice)) --- REPORT
    R3((Actions)) --- REPORT

    %% Relationships Mapping
    FARMER --- MANAGES
    MANAGES --- PROFILE
    
    PROFILE --- PRODUCES
    PRODUCES --- SENSOR
    
    FARMER --- INIT_REL{Initiates}
    INIT_REL --- PRED
    
    PRED --- GEN_REL{Generates}
    GEN_REL --- REPORT

    %% Styling
    style FARMER fill:#fff,stroke:#000,stroke-width:2px
    style PROFILE fill:#fff,stroke:#000,stroke-width:2px
    style SENSOR fill:#fff,stroke:#000,stroke-width:2px
    style PRED fill:#fff,stroke:#000,stroke-width:2px
    style REPORT fill:#fff,stroke:#000,stroke-width:2px
    
    style MANAGES fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style PRODUCES fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style INIT_REL fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style GEN_REL fill:#e1f5fe,stroke:#01579b,stroke-width:2px
```

### Diagram Explanation:
- **Rectangles**: Represent the major Entities (Users, Profiles, Sensors, AI Predictions).
- **Diamonds**: Represent the Relationships between these entities (e.g., A Farmer **Manages** a Farm Profile).
- **Ovals**: Represent the specific Attributes (data fields) belonging to each entity.

---
**File:** Logical_ER_Diagram.md | **Project:** Krishi Mitr
