# Alzheimer's Research Project

## Data Access
This project uses data from the Alzheimer's Disease Neuroimaging Initiative (ADNI). Due to data privacy agreements, the dataset cannot be shared publicly.

### Instructions to Reproduce:

1. Request access at [adni.loni.usc.edu](http://adni.loni.usc.edu).
2. Download `TADPOLE_D1_D2.csv` and `ADNIMERGE.csv`.
3. Place them in the `data/raw/` folder.
4. Run `python src/1_preprocess_data.py`.

---

> **Note:** The following is a progress check and not the final README.

# FURI Mid-Semester Progress Report: Memory-Enabled AI for Alzheimer's Trajectory Prediction
**Prepared by:** Aashi  
**Project:** FURI (Fulton Undergraduate Research Initiative)

---

## 🚀 The Vision & Where We Are Today
For the first half of my FURI research this semester, my core objective was to prove a huge hypothesis: **Standard AI models are "temporally blind."** When you ask ChatGPT or standard clinical models to predict Alzheimer's disease progression, they fail because they only look at a single snapshot of a patient's most recent visit. 

I set out to build an AI architecture equipped with **longitudinal memory** and backed by a **Predictive Knowledge Graph** to drastically improve prognostic accuracy.

We are officially at the halfway mark of the semester, and **we have completely crushed the data infrastructure and baseline evaluation phases.** Here is an insane breakdown of exactly what I’ve achieved so far.

---

## 📊 Phase 1: What We Have Achieved (The Accomplishments)

### 1. Synthesizing 1,730 Lifetimes of Data
I didn't want to use simple structured spreadsheets; I wanted this AI to read real clinical notes. 
* **The Metric:** I processed the massive TADPOLE dataset and translated raw biomarkers and cognitive tests into **8,600+ sequential natural-language clinic visits** across **1,730 real ADNI patients**. 
* **The Tech:** Using multithreaded pipelines running OpenAI’s `gpt-4o` and Google's `gemini-2.5-flash`, I summarized these visits into cohesive timelines mapping structural brain changes (Hippocampal Atrophy) and cognitive decline (MMSE drops). 

### 2. Building the First Longitudinal Clinical Graph
Most medical Knowledge Graphs (like PrimeKG or AlzKB) are just molecular dictionaries linking proteins to drugs. I built something fundamentally different: a **Patient-Trajectory Knowledge Graph** housed in a live Neo4j AuraDB cloud instance.
* **Macro-KG (The Ground Truth):** I extracted the absolute rules of the cohort directly into the graph. It mathematically tracks the global benchmarks.
* **Micro-KG (The Patient Mesh):** I securely injected all 1,730 patient timelines into the graph.
* **The "Clinical Twins" Engine (Step 1c):** I engineered a Cypher projection to draw `[:SIMILAR_TO]` predictive edges between patients. If Patient A and Patient B both declined from MCI to Dementia with identical biomarker atrophy, the graph links them as clinical twins. This allows the AI to predict future trajectories by analyzing patients with identical pasts.

### 3. Bulletproof Validation Against Global Standards
To prove my graph works, I benchmarked my extraction metrics against massive, established Alzheimer's network graphs and leading literature. My pipeline hit the bullseye:
* **MCI-to-Dementia Conversion:** I extracted a **46.0%** rate over 4.1 years. (Validated against the Skogholt 2022 pan-ADNI baseline of 47.3%).
* **Annual Hippocampal Atrophy:** I extracted **3.9%**. (Validated cleanly within the expected 3.6% - 4.6% window for MCI-to-AD progressors).
* **Biomarker-Cognition Correlation (r = 0.73):** Proving a massively strong link between brain volume loss and MMSE cognitive decline.

### 4. Proving The Thesis: The C0 vs C1 Baseline Test
The biggest milestone so far was proving that *memory actually matters*. I built a rigorous testbed to evaluate two AI architectures on the exact same patient data:
* **C0 (Stateless Baseline):** I purposely gave the AI only the *latest* visit text. **Result: It failed.** The AI hallucinated or stated, *"I do not have enough information to calculate the clinical change."*
* **C1 (Memory Baseline):** I fed the AI the patient's past history vectors plus the latest visit. **Result: Huge Success.** The AI explicitly calculated the exact cognitive drop (e.g., retrieving the old 23.0 MMSE score vs the current state) and accurately mapped the progression from MCI to Dementia. 

**Conclusion:** I successfully captured the hard evidence required for the "Baselines and first task results collected" milestone!

---

## ⚡ What's Next? (The Second Half of the Semester)

Now that the graph is live, the CLI is built, and the linear baselines (C0 vs C1) are tested, the second half of the semester shifts entirely to **Graph-RAG and Agentic Autonomy.**

### 1. The C2 Architecture (Graph-RAG)
Right now, the C1 model just reads a timeline like a book. In the next few weeks, I will launch the **C2 Model**. This AI won't just look backward at the patient's linear history; it will actively query the Neo4j **FuriMasterKG**. If the patient is faltering, the C2 model will find the patient's node, traverse the `[:SIMILAR_TO]` edges to fetch their "Clinical Twins," and use the historical outcomes of those twins to predict what will happen to the current patient.

### 2. The C3 Architecture (Fully Agentic Diagnostic Co-pilot)
The final architecture. I will give the AI agency. It will be able to autonomously decide when to look at the timeline vector, when to run a Cypher query on the Neo4j Clinical Twin mesh, and when to synthesize it all together to output a highly accurate longitudinal prognosis. 

### 3. The Final Presentation & Pitch
I will wrap up all computational analysis into the final FURI poster and deliverable report. We went from messy, raw clinical numbers to a live, cloud-hosted predictive graph predicting cognitive decline. The final demo will concretely show a doctor uploading a patient's chart, and the FURI agent instantly matching it to ADNI historical twins to chart the path forward.
