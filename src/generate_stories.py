import pandas as pd
import json
import time
import os
from openai import OpenAI
from tqdm import tqdm # The progress bar!

# 1. Setup your API Key
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, "../data/processed/clean_patient_data.csv")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "../data/processed/FULL_patient_narratives.json")

def create_patient_prompt(row):
    return f"""You are an expert neurologist. Please write a detailed clinical narrative summary for the following patient based on their medical data. 

Patient Data:
- Patient ID (RID): {row.get('RID')}
- Visit: {row.get('VISCODE')} (Month {row.get('Month')})
- Age: {row.get('AGE')}
- Gender: {row.get('PTGENDER')}
- Diagnosis (DX): {row.get('DX')}
- APOE4 Genetic Marker: {row.get('APOE4')}
- Cognitive Scores: MMSE = {row.get('MMSE')}, ADAS13 = {row.get('ADAS13')}
- Brain Volumes: Hippocampus = {row.get('Hippocampus')} mm³, Ventricles = {row.get('Ventricles')} mm³, Whole Brain = {row.get('WholeBrain')} mm³, Entorhinal = {row.get('Entorhinal')} mm³
- PET Scan (FDG): {row.get('FDG')}

Write a 2-3 paragraph natural language summary describing this patient's demographic profile, their cognitive state, their brain volumetrics, and their overall risk or presentation of Alzheimer's Disease or cognitive decline."""

def main():
    print("Loading full dataset...")
    df = pd.read_csv(DATA_PATH)
    
    results = []
    
    print(f"Starting LLM generation for {len(df)} patients...\n")
    
    # Wrap df.iterrows() in tqdm for a sweet progress bar
    for index, row in tqdm(df.iterrows(), total=len(df), desc="Generating Stories"):
        prompt = create_patient_prompt(row)
        
        try:
            # Using gpt-4o-mini as it's the newer, cheaper, better fast model from OpenAI
            response = client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=[
                    {"role": "system", "content": "You are an expert neurologist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2 
            )
            
            narrative = response.choices[0].message.content
            
            results.append({
                "RID": row['RID'],
                "VISCODE": row['VISCODE'],
                "Narrative": narrative
            })
            
            # AUTO-SAVE CHECKPOINT: Save every 100 rows
            if (index + 1) % 100 == 0:
                os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
                with open(OUTPUT_PATH, 'w') as f:
                    json.dump(results, f, indent=4)
            
            time.sleep(0.5) # Slight pause for API limits
            
        except Exception as e:
            print(f"\nError on row {index} (RID {row['RID']}): {e}")
            # If it hits a rate limit, pause for 10 seconds and keep going
            if "Rate limit" in str(e) or "429" in str(e):
                print("Sleeping for 10 seconds to recover from rate limit...")
                time.sleep(10)
            
    # Final Save
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(results, f, indent=4)
        
    print(f"\nSUCCESS! All {len(df)} patient narratives saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
