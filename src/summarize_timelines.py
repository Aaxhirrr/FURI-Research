import json
import time
import os
import concurrent.futures
import threading
from tqdm import tqdm
from openai import OpenAI
from collections import defaultdict

# 1. Setup your API Key
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
output_file = os.path.join(SCRIPT_DIR, '../data/processed/patient_timelines.json')
file_lock = threading.Lock()

def create_timeline_prompt(rid, visits):
    timeline_text = ""
    for v in visits:
        timeline_text += f"\n--- Visit: {v['VISCODE']} ---\n{v['Narrative']}\n"
        
    return f"""You are an expert neurologist. Review the following longitudinal clinical data for Patient {rid} across multiple visits.

{timeline_text}

Write a single, comprehensive 2-3 paragraph summary detailing this patient's disease progression over time. 
Specifically highlight:
1. Baseline status vs. their final recorded status.
2. The trajectory of their cognitive scores (MMSE, ADAS13).
3. The trajectory of their brain volumetrics (Hippocampus, Ventricles, etc.).
4. How their genetic risk (APOE4) aligns with their observed progression.

Do not list the visits one by one. Synthesize the data into a flowing clinical narrative of their overall disease trajectory."""

def process_patient_timeline(rid, visits):
    prompt = create_timeline_prompt(rid, visits)
    max_retries = 8  # We will try up to 8 times if we hit a rate limit
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=[
                    {"role": "system", "content": "You are an expert neurologist summarizing longitudinal patient data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                timeout=30.0  # <--- THIS IS THE MAGIC BULLET
            )
            return {
                "RID": rid,
                "Total_Visits": len(visits),
                "Timeline_Summary": response.choices[0].message.content
            }
        except Exception as e:
            if "Rate limit" in str(e) or "429" in str(e):
                # Exponential backoff: Sleep for 5s, then 10s, then 20s...
                sleep_time = 5 * (2 ** attempt) 
                time.sleep(sleep_time)
            else:
                print(f"\nFatal Error on RID {rid}: {e}")
                return None
                
    print(f"\nFailed on RID {rid} after {max_retries} retries.")
    return None

def main():
    print("Loading sorted patient narratives...")
    INPUT_PATH = os.path.join(SCRIPT_DIR, '../data/processed/patient_narratives_sorted.json')
    try:
        with open(INPUT_PATH, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find '{INPUT_PATH}'.")
        return
        
    patients = defaultdict(list)
    for row in data:
        patients[row['RID']].append(row)
        
    print(f"Grouped into {len(patients)} unique patient timelines.")
    
    results = []
    
    # Check if we are resuming
    processed_rids = set()
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r') as f:
                results = json.load(f)
                for r in results:
                    processed_rids.add(r['RID'])
            print(f"✅ Found existing save file. Safely loaded {len(results)} summarized patients.")
        except Exception as e:
            print(f"Warning: Could not read existing JSON. Error: {e}")

    patients_to_process = {rid: visits for rid, visits in patients.items() if rid not in processed_rids}
    print(f"🚀 Timelines to process: {len(patients_to_process)}")
    
    if not patients_to_process:
        print("You are already 100% done!")
        return
    
    # We lowered this to 5 to avoid smashing the 200k TPM rate limit
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        futures = {executor.submit(process_patient_timeline, rid, visits): rid for rid, visits in patients_to_process.items()}
        
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(patients_to_process), desc="Summarizing Timelines"):
            result = future.result()
            if result:
                with file_lock:
                    results.append(result)
                    if len(results) % 50 == 0:
                        os.makedirs(os.path.dirname(output_file), exist_ok=True)
                        with open(output_file, 'w') as f:
                            json.dump(results, f, indent=4)
                            
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=4)
        
    print(f"\n🎉 DONE! {len(patients)} patient timelines successfully summarized into {output_file}")

if __name__ == "__main__":
    main()
