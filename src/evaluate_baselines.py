import json
import os
import sys
import google.generativeai as genai

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# 1. SETUP: API
genai.configure(api_key=os.environ.get("GEMINI_API_KEY")) # INSERT YOUR KEY HERE
model = genai.GenerativeModel('gemini-2.5-flash')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(SCRIPT_DIR, '../data/processed/CLEAN_1730_TIMELINES.json')

def get_patient_split(rid, data):
    """Physically splits the timeline to enforce C0's amnesia."""
    for patient in data:
        if patient and patient.get('RID') == rid:
            summary = patient.get('Timeline_Summary', '')
            
            # Split by sentences to cleanly separate the past from the present
            sentences = [s.strip() + '.' for s in summary.split('.') if s.strip()]
            
            if len(sentences) < 3:
                return None, None
                
            # C0 only gets the last 2 sentences (The "Latest Visit" state)
            # C1 gets everything (The "Full Memory")
            past_history = " ".join(sentences[:-2])
            latest_visit = " ".join(sentences[-2:])
            
            return past_history, latest_visit
    return None, None

def run_c0_stateless(latest_visit):
    """C0: Single-visit baseline. No memory."""
    print("\n" + "🔴"*20)
    print(" C0 MODEL (STATELESS / NO MEMORY)")
    print("🔴"*20)
    print(f"[SYSTEM PROMPT]: You only see this data: '{latest_visit}'\n")
    
    prompt = f"""
    You are an AI evaluating an Alzheimer's patient. 
    You only have access to their MOST RECENT clinical status:
    "{latest_visit}"
    
    Task: What exactly changed in the patient's cognitive scores (like MMSE) or diagnosis since their LAST visit? 
    If you do not have enough information to calculate a change, state that explicitly.
    """
    response = model.generate_content(prompt)
    print(f">> OUTPUT:\n{response.text}\n")

def run_c1_memory(past_history, latest_visit):
    """C1: Vector/Memory baseline. Remembers past visits."""
    print("\n" + "🟢"*20)
    print(" C1 MODEL (VECTOR / FULL MEMORY)")
    print("🟢"*20)
    print(f"[SYSTEM PROMPT]: You have retrieved the patient's past history.\n")
    
    prompt = f"""
    You are an AI evaluating an Alzheimer's patient. 
    You have retrieved their PAST HISTORY from the vector database:
    "{past_history}"
    
    And you have their MOST RECENT clinical status:
    "{latest_visit}"
    
    Task: What exactly changed in the patient's cognitive scores (like MMSE) or diagnosis since their LAST visit? 
    Calculate the exact delta or progression based on the memory provided.
    """
    response = model.generate_content(prompt)
    print(f">> OUTPUT:\n{response.text}\n")

def main():
    # RID 4022 is a solid test subject, but you can change this to any RID from your CLI
    TARGET_RID = 4022 
    
    print(f"🧬 Loading 1,730-patient graph data...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    past, latest = get_patient_split(TARGET_RID, data)
    
    if past and latest:
        print(f"✅ Data successfully split for Patient {TARGET_RID}!")
        run_c0_stateless(latest)
        run_c1_memory(past, latest)
    else:
        print(f"❌ Failed to split data for RID {TARGET_RID}. They might not have enough longitudinal visits. Try another RID.")

if __name__ == "__main__":
    main()
