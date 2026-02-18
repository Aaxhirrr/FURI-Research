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
OUTPUT_PT_PATH = os.path.join(SCRIPT_DIR, "../data/processed/tadpole_graph.pt")
NEO4J_EXPORT_DIR = os.path.join(SCRIPT_DIR, "../data/processed/neo4j_import") # We prep this for later

# ==========================================
# LANE 1: THE BRIDGE RULES (From your Data Profiling)
# ==========================================
# These are the "Judge" values we found in Week 2
STATS = {
    'HIPPOCAMPUS_ATROPHY_THRESH': 5600,  # Mean - 1 StdDev
    'MMSE_DECLINE_THRESH': 24,           # Clinical Cutoff
    'HEAD_SIZE_MIN': 1100000             # For check (not used in logic yet)
}

# ==========================================
# LANE 2: THE CONCEPTS (External Knowledge)
# ==========================================
# These are the "Universal Truths" we are connecting to
CONCEPTS = {
    0: "Concept:Brain_Atrophy",
    1: "Concept:Cognitive_Decline",
    2: "Concept:Genetic_Risk_APOE4",
    3: "Concept:Amyloid_Positive"
}

def build_graph():
    print("🏗️ Building 'Converged' Knowledge Graph (The Professor's Bridge)...")
    
    if not os.path.exists(INPUT_PATH):
        print(f"❌ Error: {INPUT_PATH} not found.")
        return
    df = pd.read_csv(INPUT_PATH)
    
    # Initialize Graph
    data = HeteroData()
    
    # Mappings
    unique_rids = df['RID'].unique()
    rid_to_idx = {rid: i for i, rid in enumerate(unique_rids)}
    
    # Storage for Neo4j (We build this simultaneously)
    neo4j_nodes = []
    neo4j_edges = []

    # --- 1. CREATE CONCEPT NODES (LANE 2) ---
    for cid, cname in CONCEPTS.items():
        neo4j_nodes.append({'id': f"C_{cid}", 'type': 'Concept', 'name': cname, 'features': ''})

    # --- 2. PREPARE STORAGE ---
    patient_feats = []
    visit_feats = []
    visit_labels = []
    
    # Edge Lists
    p_to_v_src, p_to_v_dst = [], [] # Patient -> Visit
    v_to_v_src, v_to_v_dst = [], [] # Visit -> Next Visit
    
    # THE CONVERGENCE EDGES (The Bridge)
    v_to_c_src, v_to_c_dst = [], [] # Visit -> Concept
    p_to_c_src, p_to_c_dst = [], [] # Patient -> Concept

    visit_count = 0
    grouped = df.groupby('RID')

    print(f"   - Processing {len(unique_rids)} patients...")

    for rid, group in grouped:
        group = group.sort_values('Month')
        
        # --- PATIENT NODE ---
        first = group.iloc[0]
        # Feature Vector: [Age, Gender, Education, APOE4]
        gender = 1 if first['PTGENDER'] == 'Female' else 0
        p_vec = [float(first['AGE']), float(gender), float(first['PTEDUCAT']), float(first['APOE4'])]
        patient_feats.append(p_vec)
        p_idx = rid_to_idx[rid]
        
        neo4j_nodes.append({'id': f"P_{p_idx}", 'type': 'Patient', 'name': f"Patient_{rid}", 'features': str(p_vec)})

        # === BRIDGE LOGIC 1: GENETICS ===
        # If Data (Lane 1) has APOE4 -> Link to Knowledge (Lane 2)
        if first['APOE4'] > 0:
            p_to_c_src.append(p_idx)
            p_to_c_dst.append(2) # Concept 2: Genetic Risk
            neo4j_edges.append({'src': f"P_{p_idx}", 'dst': "C_2", 'type': 'HAS_RISK'})

        previous_v_idx = None
        
        for _, row in group.iterrows():
            current_v_idx = visit_count
            
            # Normalization (Crucial Step)
            icv = row['ICV'] if row['ICV'] > 0 else 1.0
            v_vec = [
                row['Hippocampus'] / icv, row['Ventricles'] / icv, row['WholeBrain'] / icv,
                row['Entorhinal'] / icv, row['Fusiform'] / icv, row['MidTemp'] / icv,
                row['MMSE'], row['ADAS13'], row['FDG'], row['AV45']
            ]
            visit_feats.append(v_vec)
            visit_labels.append(int(row['Label']))
            
            neo4j_nodes.append({'id': f"V_{current_v_idx}", 'type': 'Visit', 'name': f"Visit_{current_v_idx}_M{row['Month']}", 'features': str(v_vec)})

            # Standard Edges
            p_to_v_src.append(p_idx)
            p_to_v_dst.append(current_v_idx)
            neo4j_edges.append({'src': f"P_{p_idx}", 'dst': f"V_{current_v_idx}", 'type': 'HAS_VISIT'})

            if previous_v_idx is not None:
                v_to_v_src.append(previous_v_idx)
                v_to_v_dst.append(current_v_idx)
                neo4j_edges.append({'src': f"V_{previous_v_idx}", 'dst': f"V_{current_v_idx}", 'type': 'NEXT_VISIT'})

            # === BRIDGE LOGIC 2: ATROPHY ===
            # If Hippocampus < 5600 (Data) -> Link to Atrophy (Knowledge)
            if row['Hippocampus'] < STATS['HIPPOCAMPUS_ATROPHY_THRESH']:
                v_to_c_src.append(current_v_idx)
                v_to_c_dst.append(0) # Concept 0: Atrophy
                neo4j_edges.append({'src': f"V_{current_v_idx}", 'dst': "C_0", 'type': 'SHOWS_SIGNS_OF'})

            # === BRIDGE LOGIC 3: COGNITIVE DECLINE ===
            # If MMSE < 24 (Data) -> Link to Decline (Knowledge)
            if row['MMSE'] < STATS['MMSE_DECLINE_THRESH']:
                v_to_c_src.append(current_v_idx)
                v_to_c_dst.append(1) # Concept 1: Decline
                neo4j_edges.append({'src': f"V_{current_v_idx}", 'dst': "C_1", 'type': 'SHOWS_SIGNS_OF'})

            # === BRIDGE LOGIC 4: AMYLOID ===
            if row['AV45'] > 1.11:
                v_to_c_src.append(current_v_idx)
                v_to_c_dst.append(3) # Concept 3: Amyloid Positive
                neo4j_edges.append({'src': f"V_{current_v_idx}", 'dst': "C_3", 'type': 'SHOWS_SIGNS_OF'})

            previous_v_idx = current_v_idx
            visit_count += 1

    # --- SAVE PYTORCH GRAPH (For the AI) ---
    data['patient'].x = torch.tensor(patient_feats, dtype=torch.float)
    data['visit'].x = torch.tensor(visit_feats, dtype=torch.float)
    data['visit'].y = torch.tensor(visit_labels, dtype=torch.long)
    data['concept'].x = torch.eye(len(CONCEPTS))

    # Add Edges to Data Object
    data['patient', 'has_visit', 'visit'].edge_index = torch.tensor([p_to_v_src, p_to_v_dst], dtype=torch.long)
    data['visit', 'next_visit', 'visit'].edge_index = torch.tensor([v_to_v_src, v_to_v_dst], dtype=torch.long)
    data['visit', 'shows_signs_of', 'concept'].edge_index = torch.tensor([v_to_c_src, v_to_c_dst], dtype=torch.long)
    data['patient', 'has_risk', 'concept'].edge_index = torch.tensor([p_to_c_src, p_to_c_dst], dtype=torch.long)

    torch.save(data, OUTPUT_PT_PATH)
    print(f"✅ CONVERGED GRAPH SAVED: {OUTPUT_PT_PATH}")

    # --- SAVE NEO4J FILES (For the next step) ---
    os.makedirs(NEO4J_EXPORT_DIR, exist_ok=True)
    pd.DataFrame(neo4j_nodes).to_csv(os.path.join(NEO4J_EXPORT_DIR, "nodes.csv"), index=False)
    pd.DataFrame(neo4j_edges).to_csv(os.path.join(NEO4J_EXPORT_DIR, "edges.csv"), index=False)
    print(f"✅ NEO4J BRIDGE READY: {NEO4J_EXPORT_DIR}")

if __name__ == "__main__":
    build_graph()
