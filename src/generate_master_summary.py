import json
import os
import google.generativeai as genai

# 1. Paste your FREE Gemini API Key here
genai.configure(api_key="AIzaSyBM8mdPI6gOpKO520zJjOKGJP5FZlN_lgY")

# We are using gemini-1.5-pro for maximum medical reasoning
model = genai.GenerativeModel('gemini-2.5-flash')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    print("Loading the summarized patient timelines...")
    input_path = os.path.join(SCRIPT_DIR, '../data/processed/patient_timelines.json')
    try:
        with open(input_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading JSON: {e}")
        return

    # Combine all patient summaries into one giant text block
    print("Aggregating clinical narratives...")
    combined_text = ""
    for patient in data:
        combined_text += f"\n\n--- Patient {patient.get('RID', 'Unknown')} ---\n{patient.get('Timeline_Summary', '')}"

    prompt = f"""You are the Chief Medical Data Scientist presenting a global dataset analysis.
I am providing you with the longitudinal clinical timelines for a cohort of patients.

{combined_text}

Write a highly extensive, comprehensive Master Summary of the entire dataset. 
This summary will be used to generate a Knowledge Graph, so ensure you clearly detail the macroscopic relationships between:
- Demographics and baseline diagnoses (Normal Cognition vs. MCI vs. Dementia).
- The general rate of cognitive decline across the cohort (MMSE, ADAS13).
- Neurodegenerative structural changes observed (Hippocampus, Entorhinal, Ventricles, Whole Brain).
- The systemic impact of the APOE4 genetic risk factor across the population.

Format this as a cohesive, professional clinical report. Use distinct sections (e.g., Demographics, Cognitive Trends, Volumetric Trends, Genetic Impact) to ensure it is highly structured and easy to extract graph nodes from."""

    print("\nSending data to Gemini API to generate the Final Master Summary (this takes about 30 seconds)...")
    
    try:
        # One single massive call
        response = model.generate_content(prompt)
        
        # Save it!
        output_path = os.path.join(SCRIPT_DIR, '../data/processed/PROFESSOR_MASTER_SUMMARY.txt')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
            
        print(f"\nSUCCESS! The Professor's Master Summary is saved as '{output_path}'")
        
    except Exception as e:
        print(f"\nError generating summary: {e}")

if __name__ == "__main__":
    main()
