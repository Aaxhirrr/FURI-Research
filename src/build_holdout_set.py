import pandas as pd
import json
import os
import random

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TABULAR_DATA_PATH = os.path.join(SCRIPT_DIR, "../data/processed/tadpole_clean.csv")
TIMELINES_PATH = os.path.join(SCRIPT_DIR, "../data/processed/CLEAN_1730_TIMELINES.json")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "../data/processed/D2_HOLDOUT_SET.json")

def build_holdout_set(sample_size=200):
    print("🔬 Isolating the Official D2 Holdout Set...")
    
    # 1. Load the tabular data to find D2 patients
    df = pd.read_csv(TABULAR_DATA_PATH, low_memory=False)
    
    if 'D2' not in df.columns:
        print("❌ Error: D2 column not found in tadpole_clean.csv")
        return
        
    # Get unique RIDs where D2 == 1 (Official Test Set)
    d2_rids = set(df[df['D2'] == 1]['RID'].unique())
    print(f"📊 Found {len(d2_rids)} unique patients in the official TADPOLE D2 Test Set.")
    
    # 2. Get the Final Ground Truth Label for each patient
    # We will grab the LAST recorded Label for each RID to serve as the prediction target
    ground_truths = {}
    for rid in d2_rids:
        patient_data = df[df['RID'] == rid].sort_values(by='Month', ascending=True)
        final_label = patient_data.iloc[-1]['Label']
        ground_truths[rid] = int(final_label) if pd.notna(final_label) else -1
        
    # 3. Load the pre-processed narrative timelines
    with open(TIMELINES_PATH, 'r', encoding='utf-8') as f:
        all_timelines = json.load(f)
        
    # Filter timelines to only those in the D2 set
    d2_timelines = [p for p in all_timelines if isinstance(p, dict) and p.get("RID") in d2_rids]
    
    # 4. Filter for valid patients (ensure they have a valid ground truth label 0, 1, or 2)
    valid_d2_timelines = [p for p in d2_timelines if ground_truths.get(p["RID"]) in [0, 1, 2]]
    
    print(f"✅ Found {len(valid_d2_timelines)} D2 patients with clean narrative timelines and ground truth labels.")
    
    # 5. Randomly sample the desired amount
    if len(valid_d2_timelines) < sample_size:
        print(f"⚠️ Warning: Only {len(valid_d2_timelines)} patients available. Taking all of them.")
        sample_size = len(valid_d2_timelines)
        
    holdout_sample = random.sample(valid_d2_timelines, sample_size)
    
    # Inject the Ground Truth Label into the payload for the evaluation script
    for p in holdout_sample:
        p["Ground_Truth_Label"] = ground_truths[p["RID"]]
        # We will also inject a "Restricted_Drug_Prompt" boolean for 50% of the set
        # This will be used to trigger the Safety Violation test
        p["Test_Safety_Violation"] = random.choice([True, False])
        
    # Save the locked holdout set
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(holdout_sample, f, indent=4)
        
    print(f"💾 Locked and saved {len(holdout_sample)} patients to '{OUTPUT_PATH}'.")
    
    # Distribution Check
    label_0 = sum(1 for p in holdout_sample if p["Ground_Truth_Label"] == 0)
    label_1 = sum(1 for p in holdout_sample if p["Ground_Truth_Label"] == 1)
    label_2 = sum(1 for p in holdout_sample if p["Ground_Truth_Label"] == 2)
    safety_tests = sum(1 for p in holdout_sample if p["Test_Safety_Violation"])
    
    print("\n--- Holdout Set Distribution ---")
    print(f"NL (0): {label_0}")
    print(f"MCI (1): {label_1}")
    print(f"AD (2): {label_2}")
    print(f"Safety Tests Triggered: {safety_tests}/{sample_size}")

if __name__ == "__main__":
    build_holdout_set(200)
    
