import torch
import networkx as nx
import matplotlib.pyplot as plt
import os
from torch_geometric.data import HeteroData

# PATHS
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GRAPH_PATH = os.path.join(SCRIPT_DIR, "../data/processed/tadpole_graph.pt")
OUTPUT_IMG_PATH = os.path.join(SCRIPT_DIR, "../data/processed/patient_timeline_bridge.png")

CONCEPTS = {
    0: "Atrophy",
    1: "Cognitive Decline",
    2: "Genetic Risk (APOE4)",
    3: "Amyloid Positive"
}

def visualize_patient_timeline(patient_idx=0):
    print(f"Inspect Graph for Patient #{patient_idx}...")
    
    # 1. Load the Graph
    if not os.path.exists(GRAPH_PATH):
        print("Graph file not found. Run 2_build_graph.py first.")
        return
    
    # Fix for newer PyTorch versions
    try:
        data = torch.load(GRAPH_PATH, weights_only=False)
    except TypeError:
        data = torch.load(GRAPH_PATH)
    
    # 2. Initialize Drawing Canvas
    G = nx.DiGraph() 
    
    # 3. Add the Patient Node (Center)
    p_feat = data['patient'].x[patient_idx].tolist()
    gender = "F" if p_feat[1] == 1.0 else "M"
    p_node_id = f"Patient_{patient_idx}"
    G.add_node(p_node_id, label=f"Patient {patient_idx}\n({gender})", color='red', shape='s')
    
    # 4. Find Connected Visits
    src, dst = data['patient', 'has_visit', 'visit'].edge_index
    visit_indices = dst[src == patient_idx].tolist()
    print(f"   - Found {len(visit_indices)} visits.")
    
    # 5. Add Visit Nodes & Edges
    previous_node = None
    visit_node_ids = []

    for v_idx in visit_indices:
        # Get Diagnosis
        label = data['visit'].y[v_idx].item()
        dx_map = {0: 'CN', 1: 'MCI', 2: 'AD'}
        dx_str = dx_map.get(label, '?')
        
        node_name = f"Visit_{v_idx}"
        visit_node_ids.append(v_idx)
        G.add_node(node_name, label=f"Visit {v_idx}\n[{dx_str}]", color='skyblue', shape='o')
        
        # Edge: Patient -> Visit
        G.add_edge(p_node_id, node_name)
        
        # Edge: Visit -> Next Visit
        if previous_node:
            G.add_edge(previous_node, node_name, label="NEXT")
        
        previous_node = node_name

    # 6. BRIDGING: Add Concept Connections
    print("   - Adding Bridge Connections...")
    
    # A. Patient -> Concept (Genetics)
    if ('patient', 'has_risk', 'concept') in data.edge_types:
        p_src, c_dst = data['patient', 'has_risk', 'concept'].edge_index
        # Find concepts connected to THIS patient
        patient_risks = c_dst[p_src == patient_idx].tolist()
        
        for c_idx in patient_risks:
            c_name = CONCEPTS.get(c_idx, f"Concept {c_idx}")
            c_node_id = f"Concept_{c_idx}"
            if not G.has_node(c_node_id):
                G.add_node(c_node_id, label=c_name, color='orange', shape='d') # d=diamond
            G.add_edge(p_node_id, c_node_id, color='orange')

    # B. Visit -> Concept (Atrophy, Decline, Amyloid)
    if ('visit', 'shows_signs_of', 'concept') in data.edge_types:
        v_src, c_dst = data['visit', 'shows_signs_of', 'concept'].edge_index
        
        # We only care about edges starting from OUR visits
        for v_idx in visit_node_ids:
            # Find concepts for this specific visit
            # Boolean mask for source node match
            concepts_for_visit = c_dst[v_src == v_idx].tolist()
            
            for c_idx in concepts_for_visit:
                c_name = CONCEPTS.get(c_idx, f"Concept {c_idx}")
                c_node_id = f"Concept_{c_idx}"
                v_node_id = f"Visit_{v_idx}"
                
                if not G.has_node(c_node_id):
                    G.add_node(c_node_id, label=c_name, color='orange', shape='d')
                
                G.add_edge(v_node_id, c_node_id, color='orange', style='dashed')
    
    # 7. DRAW IT
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, seed=42, k=1.5) # k controls spacing
    
    # Nodes
    colors = [nx.get_node_attributes(G, 'color').get(n, 'gray') for n in G.nodes()]
    nx.draw(G, pos, with_labels=False, node_color=colors, node_size=2500, edge_color='gray')
    
    # Labels
    labels = nx.get_node_attributes(G, 'label')
    nx.draw_networkx_labels(G, pos, labels, font_size=9)
    
    plt.title(f"Professor's Bridge: Patient {patient_idx} Connectivity")
    plt.axis('off')
    
    plt.savefig(OUTPUT_IMG_PATH)
    print(f"Plot saved to {OUTPUT_IMG_PATH}")
    print("Plot generated.")

if __name__ == "__main__":
    visualize_patient_timeline(patient_idx=0)
