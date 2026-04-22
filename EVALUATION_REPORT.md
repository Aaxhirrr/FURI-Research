# FURI Architecture: Quantitative Evaluation Report

## Overview
This report encapsulates the quantitative evaluation of three model architectures operating on the official TADPOLE Challenge Holdout Data (D2=1). The objective is to evaluate the predictive accuracy and clinical safety of the Baseline Stateless LLM (C0), Baseline Vector-RAG (C1), and the proposed Hybrid Graph-RAG (C3) architecture.

## 1. Summary Metrics

| Metric | Model C0 (Stateless) | Model C1 (Semantic RAG) | Model C3 (Graph-RAG) |
|---|---|---|---|
| **Sample Size (N)** | 181 | 181 | 181 |
| **Diagnostic Accuracy** | 0.856 | 0.862 | 0.823 |
| **Expected Calibration Error (ECE)** | 0.037 | 0.007 | 0.052 |
| **Temporal Order Accuracy (TOA)** | 0.000 | 0.000 | 0.155 |
| **Safety Violation Rate** | 0.000 | 0.000 | 0.054 |

## 2. Metric Definitions
- **Diagnostic Accuracy:** Ratio of correct MCI/AD conversion classifications matching ground truth TADPOLE data. Measures the architecture's capability to accurately deduce decline trajectory.
- **Expected Calibration Error (ECE):** A measure of how closely self-reported confidence scores align with actual diagnostic accuracy. A lower score indicates superior probabilistic calibration, representing a model less susceptible to "overconfident" hallucination.
- **Temporal Order Accuracy (TOA):** Proportion of cases where the model successfully organized randomized clinical timelines into the correct sequential order (e.g., bl, m06, m12). Measures longitudinal comprehension.
- **Safety Violation Rate:** Percentage of test cases involving a highly-restricted contraindicated medication (Memantine for generic MCI cases) where the model failed to issue a clinical block. A lower score represents superior clinical adherence.
