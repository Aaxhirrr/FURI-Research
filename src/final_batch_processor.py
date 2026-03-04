import json
import os
import concurrent.futures
from tqdm import tqdm
from openai import OpenAI
from collections import defaultdict
import time
import random

# 1. SETUP
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
raw_input = os.path.join(SCRIPT_DIR, '../data/processed/patient_narratives_sorted.json')
current_progress = os.path.join(SCRIPT_DIR, '../data/processed/patient_final_timelines_v2.json')
final_clean_output = os.path.join(SCRIPT_DIR, '../data/processed/CLEAN_1730_TIMELINES.json')

def fetch_summary_with_retry(rid, visits, retries=3):
    timeline_text = "".join([f"\n--- Visit: {v['VISCODE']} ---\n{v['Narrative']}\n" for v in visits])
    prompt = f"Analyze clinical data for Patient {rid}:\n{timeline_text}\nWrite a 2-paragraph clinical summary."
    
    for i in range(retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}]
            )
            return {
                "RID": rid, 
                "Total_Visits": len(visits), 
                "Timeline_Summary": response.choices[0].message.content
            }
        except Exception as e:
            if "429" in str(e):
                # Wait 5-10 seconds and try again
                wait_time = (2 ** i) + random.random() * 5
                time.sleep(wait_time)
                continue
            return {"RID": rid, "ERROR_MESSAGE": f"Failed after retries: {str(e)}"}

def main():
    with open(raw_input, 'r') as f:
        raw_data = json.load(f)
    patient_map = defaultdict(list)
    for row in raw_data: patient_map[row['RID']].append(row)

    with open(current_progress, 'r') as f:
        existing_results = json.load(f)

    # Filter: Keep the good Gemini summaries, fix everything else
    good_results = [item for item in existing_results if "Timeline_Summary" in item]
    rids_to_fix = [item['RID'] for item in existing_results if "ERROR_MESSAGE" in item]
    
    # Catch any missed RIDs
    processed_rids = {item['RID'] for item in existing_results}
    missing_rids = [rid for rid in patient_map.keys() if rid not in processed_rids]
    
    total_to_process = rids_to_fix + missing_rids
    print(f"✅ Keeping {len(good_results)} successful summaries.")
    print(f"🛠️  Cleaning remaining {len(total_to_process)} patients (Throttled Mode)...")

    final_results = good_results

    # Dropped to 3 workers to stay under the 30k Token Limit
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = {executor.submit(fetch_summary_with_retry, rid, patient_map[rid]): rid for rid in total_to_process}
        
        for future in tqdm(concurrent.futures.as_completed(futures), total=len(total_to_process)):
            res = future.result()
            final_results.append(res)
            
            if len(final_results) % 10 == 0:
                with open(final_clean_output, 'w') as f:
                    json.dump(final_results, f, indent=4)

    with open(final_clean_output, 'w') as f:
        json.dump(final_results, f, indent=4)
    print(f"\n🎉 DONE! All 1,730 patients clean in {final_clean_output}")

if __name__ == "__main__":
    main()