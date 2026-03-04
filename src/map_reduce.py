import json
import os
import google.generativeai as genai
from tqdm import tqdm

# 1. SETUP: Using Gemini 1.5 Pro ($14.19 credit)
genai.configure(api_key="AIzaSyBj-033GCRbvuZRvSnsV2KlFzhPFZYoF2g")
model = genai.GenerativeModel('gemini-2.5-pro')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(SCRIPT_DIR, '../data/processed/CLEAN_1730_TIMELINES.json')
# THE DUMP FILE: Saves the 18 regional summaries
dump_file = os.path.join(SCRIPT_DIR, '../data/processed/chunk_summaries_dump.json')
output_report = os.path.join(SCRIPT_DIR, 'FINAL_1730_COHORT_REPORT.md')

def process_chunk(chunk_data, chunk_id):
    """Reduction Phase 1: Summarize a batch of 100 patients."""
    summaries = [item['Timeline_Summary'] for item in chunk_data if item and 'Timeline_Summary' in item]
    if not summaries:
        return None
        
    text_block = "\n\n".join(summaries)
    prompt = f"Analyze these 100 Alzheimer's patient timelines (Chunk {chunk_id}). Extract: 1. Avg MMSE drop, 2. % MCI-to-Dementia, 3. Hippocampal loss trends."
    
    try:
        response = model.generate_content(prompt)
        return {"chunk_id": chunk_id, "summary": response.text}
    except Exception as e:
        return {"chunk_id": chunk_id, "error": str(e)}

def main():
    print(f"🧬 Loading dataset from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    data = [item for item in raw_data if item is not None and 'RID' in item]
    data.sort(key=lambda x: x['RID'])
    
    chunk_size = 100
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]
    print(f"📦 Created {len(chunks)} chunks. Processing...")
    
    intermediate_results = []
    for i, chunk in enumerate(tqdm(chunks)):
        res = process_chunk(chunk, i+1)
        if res: intermediate_results.append(res)
    
    # --- THE DUMP LINE: Save the 18 chunk summaries to a separate JSON ---
    with open(dump_file, 'w', encoding='utf-8') as f:
        json.dump(intermediate_results, f, indent=4)
    print(f"💾 CHUNK DUMP SAVED: {dump_file}")

    # FINAL GLOBAL REDUCTION
    print("🌍 Performing Final Global Reduction...")
    final_context = "\n\n".join([r['summary'] for r in intermediate_results if 'summary' in r])
    
    master_prompt = f"""You are the Lead Clinical Data Architect. 
    Analyze these 18 regional summaries from our 1,730-patient study.
    {final_context}
    GENERATE THE GLOBAL 1,730-PATIENT KG MASTER REPORT:
    1. Scale: N=1730 with 100% integrity.
    2. Stats: Final MCI-to-Dementia and NL-to-MCI transition rates.
    3. Biomarkers: Correlation between hippocampal atrophy and MMSE decline.
    4. KG Nodes: Top 10 predictive clinical findings for Neo4j.
    """
    
    final_report = model.generate_content(master_prompt)
    with open(output_report, 'w', encoding='utf-8') as f:
        f.write(final_report.text)
    
    print(f"🎉 MASTER REPORT COMPLETE! Saved to: {output_report}")

if __name__ == "__main__":
    main()