import torch
import pandas as pd
import numpy as np
import os
from torch_geometric.data import HeteroData

# ==========================================
# CONFIGURATION
# ==========================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_PATH = os.path.join(SCRIPT_DIR, "../data/processed/tadpole_clean.csv")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, "../data/processed/tadpole_graph.pt")

def build_graph():
    print("Building Knowledge Graph...")
    
    # 1. Load Data
    if not os.path.exists(INPUT_PATH):
        print(f"Error: {INPUT_PATH} not found.")
        return
    df = pd.read_csv(INPUT_PATH)
    
    # 2. Initialize Graph Storage
    data = HeteroData()
    
    # 3. Create Mappings (RID -> Node Index)
    unique_rids = df['RID'].unique()
    rid_to_index = {rid: i for i, rid in enumerate(unique_rids)}
    
    print(f"   - Processing {len(unique_rids)} unique patients...")

    # 4. Storage Lists
    patient_feats = []
    visit_feats = []
    visit_labels = []   # The Answer Key (0, 1, 2)
    
    # Edge Lists (Source -> Target)
    patient_to_visit_src = []
    patient_to_visit_dst = []
    visit_to_visit_src = []
    visit_to_visit_dst = []

    visit_count = 0 

    # 5. LOOP: Process Every Patient
    grouped = df.groupby('RID')
    
    for rid, group in grouped:
        # Sort by time to ensure logical flow
        group = group.sort_values('Month')
        
        # --- A. PATIENT NODE (Static) ---
        # Take features from the baseline (first) visit
        first_visit = group.iloc[0]
        
        # Feature Vector: [Age, Gender(0/1), Education, APOE4]
        # Safety check: Ensure Gender is numeric
        gender = 1 if first_visit['PTGENDER'] == 'Female' else 0
        
        p_vec = [
            float(first_visit['AGE']), 
            float(gender),
            float(first_visit['PTEDUCAT']),
            float(first_visit['APOE4'])
        ]
        patient_feats.append(p_vec)
        p_idx = rid_to_index[rid]

        # --- B. VISIT NODES (Dynamic) ---
        previous_visit_idx = None
        
        for _, row in group.iterrows():
            current_visit_idx = visit_count
            
            # NORMALIZATION: Divide Volumes by ICV (Head Size)
            # This makes the data "comparable" across patients
            icv = row['ICV'] if row['ICV'] > 0 else 1.0 
            
            v_vec = [
                row['Hippocampus'] / icv,
                row['Ventricles'] / icv,
                row['WholeBrain'] / icv,
                row['Entorhinal'] / icv,
                row['Fusiform'] / icv,
                row['MidTemp'] / icv,
                row['MMSE'],   # Scores are standard, no div needed
                row['ADAS13'],
                row['FDG'],
                row['AV45']
            ]
            visit_feats.append(v_vec)
            visit_labels.append(int(row['Label']))
            
            # --- C. CREATE EDGES ---
            # Edge 1: Patient -> Visit (Ownership)
            patient_to_visit_src.append(p_idx)
            patient_to_visit_dst.append(current_visit_idx)
            
            # Edge 2: Visit -> Next Visit (Temporal Flow)
            if previous_visit_idx is not None:
                visit_to_visit_src.append(previous_visit_idx)
                visit_to_visit_dst.append(current_visit_idx)
            
            # Update state
            previous_visit_idx = current_visit_idx
            visit_count += 1

    # 6. CONVERT TO PYTORCH TENSORS
    # Nodes
    data['patient'].x = torch.tensor(patient_feats, dtype=torch.float)
    data['visit'].x = torch.tensor(visit_feats, dtype=torch.float)
    data['visit'].y = torch.tensor(visit_labels, dtype=torch.long) # The Target
    
    # Edges
    # P -> V
    data['patient', 'has_visit', 'visit'].edge_index = torch.tensor(
        [patient_to_visit_src, patient_to_visit_dst], dtype=torch.long
    )
    # V -> V (Next Visit)
    data['visit', 'next_visit', 'visit'].edge_index = torch.tensor(
        [visit_to_visit_src, visit_to_visit_dst], dtype=torch.long
    )

    # 7. SAVE
    torch.save(data, OUTPUT_PATH)
    print("-" * 40)
    print(f"GRAPH BUILT & SAVED: {OUTPUT_PATH}")
    print(f"   - Patients: {data['patient'].num_nodes}")
    print(f"   - Visits:   {data['visit'].num_nodes}")
    print(f"   - Edges (P->V): {data['patient', 'has_visit', 'visit'].num_edges}")
    print(f"   - Edges (V->V): {data['visit', 'next_visit', 'visit'].num_edges}")
    print("-" * 40)

if __name__ == "__main__":
    build_graph()
