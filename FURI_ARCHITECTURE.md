```mermaid
flowchart TD
    %% Styling
    classDef input fill:#e2e8f0,stroke:#64748b,stroke-width:2px,color:black,font-weight:bold;
    classDef agent fill:#8C1D40,stroke:#FFC627,stroke-width:3px,color:white,font-weight:bold;
    classDef neo4j fill:#008CC1,stroke:#005571,stroke-width:3px,color:white,font-weight:bold;
    classDef kg fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:black;
    classDef output fill:#10b981,stroke:#047857,stroke-width:3px,color:white,font-weight:bold;
    classDef alert fill:#ef4444,stroke:#991b1b,stroke-width:3px,color:white,font-weight:bold;

    subgraph Data Ingestion
        A["Patient Month 12 Data\n(MMSE, MRI Atrophy, Drugs)"]:::input
    end

    subgraph The Multi-Agent Swarm (C3)
        A2["Agent 2: Chronology Expert\n(Resolves Temporal Blindness)"]:::agent
        A1["Agent 1: Diagnostician\n(Finds Clinical Twins)"]:::agent
        A3["Agent 3: Pharma Guard\n(Safety Interception)"]:::agent
    end

    subgraph Dual Graph Architecture (Neo4j)
        N["Neo4j Graph Database"]:::neo4j
        
        N_Micro["Micro-KG (Patient Mesh)\n[:SIMILAR_TO] Trajectories"]:::kg
        N_Macro["Macro-KG (Global Rules)\ne.g., 46% MCI→AD Rate"]:::kg
        
        N --> N_Micro
        N --> N_Macro
    end

    %% Flow
    A -->|"Raw Timeline"| A2
    A2 -->|"Chronologically Sorted Phenotypes"| A1
    
    A1 <-->|"Queries 'Similar To' Nodes"| N_Micro
    
    A1 -->|"Proposes Month 36 Forecast\n+ Medication Plan"| A3
    
    A3 <-->|"Validates against\nBiological Guardrails"| N_Macro
    
    A3 -->|"Pass: Safe Validation"| O_Safe["Output:\nMonth 36 AD Forecast"]:::output
    A3 -->|"Fail: Contraindication\n(e.g., Memantine for MCI)"| O_Alert["Hard Stop Intercepted\n(94.6% Success)"]:::alert
    
    O_Alert -.->|"Reroutes"| A1
```
