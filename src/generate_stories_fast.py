import pandas as pd
import json
import time
import os
import threading
import concurrent.futures
from openai import OpenAI
from tqdm import tqdm

# 1. Setup your API Key
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 2. NEW OUTPUT FILE NAME (Leaves your old backup alone)
output_file = os.path.join(SCRIPT_DIR, '../data/processed/patient_narratives_fast_4omini.json')

# This lock ensures our 10 concurrent threads don't corrupt the JSON file when saving
file_lock = threading.Lock()

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

def process_patient(row):
    prompt = create_patient_prompt(row)
    max_retries = 5
    
    for attempt in range(max_retries):
        try:
            # Using gpt-4o-mini: faster, smarter, cheaper
            response = client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=[
                    {"role": "system", "content": "You are an expert neurologist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2 
            )
            narrative = response.choices[0].message.content
            return {
                "RID": row['RID'],
                "VISCODE": row['VISCODE'],
                "Narrative": narrative
            }
        except Exception as e:
            # If we go too fast and OpenAI gets mad, tell the thread to chill for a few seconds
            if "Rate limit" in str(e) or "429" in str(e):
                time.sleep(4 * (attempt + 1)) 
            else:
                print(f"Error on RID {row['RID']}: {e}")
                return None
    return None

def main():
    print("Loading datasets...")
    CSV_PATH = os.path.join(SCRIPT_DIR, '../data/processed/clean_patient_data.csv')
    df = pd.read_csv(CSV_PATH)
    
    results = []
    processed_keys = set()
    
    # Check if we are resuming from THIS new file
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r') as f:
                results = json.load(f)
                for r in results:
                    processed_keys.add(f"{r['RID']}_{r['VISCODE']}")
            print(f"✅ Found existing save file. Safely loaded {len(results)} patients.")
        except Exception as e:
            print(f"Warning: Could not read existing JSON. Error: {e}")
            
    # Filter out rows we've already done
    rows_to_process = []
    for _, row in df.iterrows():
        if f"{row['RID']}_{row['VISCODE']}" not in processed_keys:
            rows_to_process.append(row)
            
    print(f"🚀 Patients to process: {len(rows_to_process)}")
    if len(rows_to_process) == 0:
        print("You are already 100% done!")
        return

    print("Starting Multi-Threaded Generation (10 Workers)...")
    
    # 10 workers running at the same time
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_patient, row): row for row in rows_to_process}
        
        # tqdm progress bar
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(rows_to_process), desc="Fast Generating"):
            result = future.result()
            if result:
                with file_lock:
                    results.append(result)
                    # Auto-save every 100 patients
                    if len(results) % 100 == 0:
                        os.makedirs(os.path.dirname(output_file), exist_ok=True)
                        with open(output_file, 'w') as f:
                            json.dump(results, f, indent=4)
                            
    # Final cleanup save
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)
        
    print(f"\n🎉 DONE! All patients saved to {output_file}")

if __name__ == "__main__":
    main()
