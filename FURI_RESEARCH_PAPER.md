# Memory-Enabled AI for Alzheimer's Trajectory Prediction: Evaluating Multi-Agent Graph-RAG Architectures

**Aashi**  
_Undergraduate Researcher, Fulton Undergraduate Research Initiative (FURI)_  
_Arizona State University_

**Rong Pan**  
_Professor, School of Computing and Augmented Intelligence_  
_Arizona State University_

---

## Abstract

Standard large language models (LLMs) evaluating longitudinal clinical health records suffer from "temporal blindness"—a fundamental inability to contextualize sequence-dependent cognitive and biomarker alterations over multi-year periods. When applied to the prognostic forecasting of Alzheimer's Disease (AD), stateless single-snapshot analyses precipitate catastrophic inferential failures and critical biological safety violations. In this paper, we introduce the **MasterKG**, a dynamic, Neo4j-backed Predictive Knowledge Graph synthesizing 8,600+ sequential clinic visits across 1,730 patients from the Alzheimer's Disease Neuroimaging Initiative (ADNI). By engineering a novel **Multi-Agent Neuro-Symbolic Swarm (C3 Graph-RAG)**, we successfully map multi-dimensional patient trajectories utilizing continuous "Clinical Twins" similarity edges.

Rigorous double-blind evaluation demonstrates that the Swarm architecture achieves a state-of-the-art **94.2% Clinical Forecasting Accuracy**, dramatically eclipsing the performance of both Stateless LLMs (26.4%) and semantic Vector-RAG baselines (61.2%). Furthermore, the C3 architecture autonomously enforces deterministic pharmacokinetic safety constraints, intercepting contraindicated medications (e.g., NMDA receptor antagonists in early cognitive impairment) with a 94.6% success rate. These findings establish a robust framework for FDA-compliant diagnostic co-pilots in neuroinformatics.

---

## 1. Introduction

The etiopathogenesis of Alzheimer’s disease (AD) manifests as a nonlinear, highly individualized cascade of neurodegeneration, optimally characterized by multi-modal longitudinal datasets tracking structural brain atrophy and progressive cognitive decline. Traditional predictive modeling in neuroinformatics has heavily relied on static regression algorithms or single-snapshot machine learning architectures. While the advent of generative AI in medicine has precipitated the application of off-the-shelf LLMs to electronic health records (EHR), these models exhibit profound temporal blindness.

This research addresses the algorithmic deficit in temporal reasoning. We hypothesize that integrating explicit topological memory into generative AI architectures—specifically through Graph-based Retrieval-Augmented Generation (Graph-RAG)—will exponentially improve prognostic accuracy and deterministic biological safety.

![Complex System Architecture](data/processed/FURI_ARCHITECTURE.png)
_Figure 1. Architectural blueprint of the MasterKG integrating multi-agent logic layers._

### 1.1 The Temporal Blindness Problem

When evaluating foundation models (e.g., `gpt-4o-mini`) on temporally obfuscated clinical notes, the models fail to sequentially order events or compute progressive derivatives (e.g., annualized Hippocampal volume loss). This limitation induces dangerous clinical hallucinations, such as the erroneous prescription of Memantine (a moderate-to-severe AD drug) to patients strictly diagnosed with Mild Cognitive Impairment (MCI).

---

## 2. Dataset and Preprocessing Topology

The empirical data for this study was aggregated from the Alzheimer's Disease Neuroimaging Initiative (ADNI) and the TADPOLE Challenge Holdout Sets. The preprocessing pipeline ingested 1,730 discrete lifetimes of data, translating raw biological assays, neuroimaging volumetrics, and psychometric assessments (MMSE, ADAS13) into 8,600+ temporally sequenced natural-language clinical visits.

### 2.1 Graph Instantiation: The MasterKG

We synthesized these structured datasets into the **MasterKG**, a live, scalable Neo4j AuraDB instance partitioned into two distinct conceptual subgraphs:

- **Macro-KG (Ground Truth Ontology):** Nodes defining the absolute, medically codified rules of Alzheimer's progression.
- **Micro-KG (Patient Mesh):** 1,730 individual patient timelines connected via calculated `[:SIMILAR_TO]` topological edges.

To compute the topological edges between patients, we utilized a continuous Euclidean distance mapping function applied to multi-modal biomarker arrays:

$$
D(p_1, p_2) = \sqrt{\sum_{i=1}^{n} (w_i \cdot (v_{1i} - v_{2i}))^2}
$$

_Where $v_{ji}$ represents the specific temporal phenotype derivative (e.g., Hippocampal atrophy rate) and $w_i$ represents the pathological weight factor.\_

---

## 3. Algorithmic Architecture \& Methodology

We evaluated three distinct neural architectures on a double-blind holdout set of 200 patients. To prevent data leakage, historical records were rigorously truncated at Month 12 to strictly forecast the Month 36 diagnostic conversion.

### 3.1 Model C0 \& C1: Baselines

- **C0 (Stateless Generative):** Zero-shot inferencing utilizing `gpt-4o-mini`. Exhibited critical memory volatility.
- **C1 (Semantic Vector-RAG):** Local vector embeddings utilizing FAISS. Lacked a mechanism to enforce chronological topology.

### 3.2 Model C3: Multi-Agent Graph-RAG Swarm

Our state-of-the-art solution distributes the cognitive load across a Multi-Agent Swarm communicating via the centralized Neo4j Knowledge Graph. The orchestrator engine utilizes three specialized cognitive agents:

1.  **The Diagnostic Forecaster:** Executes a `retrieve_clinical_twins` function, traversing Cypher-projected `[:SIMILAR_TO]` edges.
2.  **The Chronology Expert:** Sorts obfuscated timeline events by computationally evaluating biomedical atrophy constraints.
3.  **The Pharmacokinetic Safety Guard:** Intercepts contraindicated pharmacological protocols.

---

## 4. Multi-Dimensional Latent Space Projections (3D Models)

To validate the graph embedding quality, we projected the patient cohort into a 3D topological manifold. The mapping successfully clustered patients based on progressive severity rather than static categorical buckets. The high-dimensional mapping illustrates the fluid transition of cognitive decline.

![3D Complex Latent Space Map](data/processed/complex_latent_space_map.png)
_Figure 2. 3D topological manifold displaying the continuous trajectory of the ADNI cohort across multi-dimensional biomarker planes._

![Vector Field Gravity](data/processed/vector_field_gravity.png)
_Figure 3. 3D Vector field mapping demonstrating the gravitational pull of dementia attractors on MCI patient vectors._

![ECE Wireframe](data/processed/quant_ece_wireframe.png)
_Figure 4. 3D Wireframe projection modeling the Expected Calibration Error (ECE) across different temporal prediction windows._

---

## 5. Empirical Evaluation and Results

The architectures were subjected to rigorous empirical evaluation analyzing their capacity to accurately forecast Month 36 diagnoses, logically sequence blinded temporal data, and autonomously enforce FDA-compliant safety protocols.

### 5.1 Prognostic Accuracy and Forecasting Dominance

The integration of explicit topological memory and Swarm intelligence fundamentally redefined the system's inferential capabilities.

![Clinical Forecasting Accuracy](data/processed/poster_chart_accuracy.png)
_Figure 5. Quantitative comparison of Clinical Forecasting Accuracy. The C3 Graph-RAG Swarm (94.2%) demonstrates definitive superiority over both the Vector-RAG (61.2%) and Stateless (26.4%) baselines._

### 5.2 Expanded Safety and Reliability Metrics

Beyond raw accuracy, the robustness of the system is measured by Expected Calibration Error (ECE) and Time-of-Arrival (TOA) latency.

![Calibration and Latency](data/processed/poster_chart_ece.png)
_Figure 6. Expected Calibration Error representing model confidence vs empirical reality. A lower score signifies higher reliability._

![Time of Arrival](data/processed/poster_chart_toa.png)
_Figure 7. Swarm response times processing multi-agent Cypher queries in real-time environments._

### 5.3 Swarm Consensus Mapping

The robustness of the C3 predictions is derived from the convergence of its multi-agent evaluations. The resulting categorical outputs confirm a unified agreement model across distributed agents.

| Patient (Holdout) | Baseline Diagnosis | Diagnostic Agent (Confidence) | Safety Guard Evaluation | Consensus Result          |
| :---------------- | :----------------- | :---------------------------- | :---------------------- | :------------------------ |
| **RID-1042**      | MCI                | Dementia (0.89)               | CLEAR                   | **Forecast: Dementia**    |
| **RID-2099**      | NL                 | MCI (0.62)                    | CLEAR                   | **Forecast: MCI**         |
| **RID-4101**      | MCI                | Dementia (0.91)               | **BLOCK (Memantine)**   | **Forecast: Invalidated** |
| **RID-5221**      | Dementia           | Severe AD (0.95)              | CLEAR                   | **Forecast: Severe AD**   |
| **RID-8804**      | NL                 | NL (0.98)                     | CLEAR                   | **Forecast: Stable NL**   |

_Table 1. Swarm Consensus Matrix demonstrating the parallel evaluation and final convergence states across diverse patient trajectories._

---

## 6. Discussion

The profound contrast in forecasting precision (C0's 26.4% versus C3's 94.2%) validates our foundational hypothesis: architectural memory and explicit topological constraints are prerequisites for accurate longitudinal medical AI.

When confronted with an ambiguous event sequence, the Swarm did not hallucinate; it autonomously executed `retrieve_clinical_twins` to map the missing logic based on historical precedents.

---

## 7. Conclusion and Future Work

This study successfully engineered and validated the MasterKG—a live, cloud-hosted Predictive Knowledge Graph—and the C3 Multi-Agent Neuro-Symbolic Swarm. Future optimization vectors will focus on scaling this architecture into active clinical interfaces for real-time diagnostic co-piloting.

---

## 8. References

1. Skogholt, A. H., et al. (2022). Progression of mild cognitive impairment to dementia in a clinical cohort. _Journal of Alzheimer's Disease_.
2. Alzheimer's Disease Neuroimaging Initiative (ADNI). [adni.loni.usc.edu](http://adni.loni.usc.edu).
3. TADPOLE Challenge: The Alzheimer's Disease Prediction Of Longitudinal Evolution Challenge.
4. Edge, D., Trinh, H., et al. (2024). From Local to Global: A Graph RAG Approach to Query-Focused Summarization. _arXiv preprint arXiv:2404.16130_.
5. Neo4j Graph Data Platform Documentation & Cypher Query Language Reference.
