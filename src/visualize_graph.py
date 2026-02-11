import torch
import networkx as nx
import matplotlib.pyplot as plt
import os
from torch_geometric.data import HeteroData

# PATHS
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GRAPH_PATH = os.path.join(SCRIPT_DIR, "../data/processed/tadpole_graph.pt")
OUTPUT_IMG_PATH = os.path.join(SCRIPT_DIR, "../data/processed/patient_timeline_preview.png")

def visualize_patient_timeline(patient_idx=0):
    print(f"Inspect Graph for Patient #{patient_idx}...")
    
    
    # 1. Load the Graph
    if not os.path.exists(GRAPH_PATH):
        print("Graph file not found. Run 2_build_graph.py first.")
        return
    
    # Fix for newer PyTorch versions requiring explicit weights_only param
    try:
        data = torch.load(GRAPH_PATH, weights_only=False)
    except TypeError:
        # Fallback for older PyTorch versions
        data = torch.load(GRAPH_PATH)
    
    # 2. Initialize Drawing Canvas
    G = nx.DiGraph() # Directed Graph
    
    # 3. Add the Patient Node (Center)
    # We grab the raw features to show info (e.g., Gender)
    p_feat = data['patient'].x[patient_idx].tolist()
    gender = "F" if p_feat[1] == 1.0 else "M"
    G.add_node(f"Patient_{patient_idx}", label=f"Patient {patient_idx}\n({gender})", color='red', shape='s')
    
    # 4. Find Connected Visits
    # Look at edge list: ('patient', 'has_visit', 'visit')
    src, dst = data['patient', 'has_visit', 'visit'].edge_index
    
    # Filter edges where source == patient_idx
    visit_indices = dst[src == patient_idx].tolist()
    
    print(f"   - Found {len(visit_indices)} visits.")

    # 5. Add Visit Nodes & Edges
    previous_node = None
    
    for v_idx in visit_indices:
        # Get Diagnosis Label (0=CN, 1=MCI, 2=AD)
        label = data['visit'].y[v_idx].item()
        dx_map = {0: 'CN', 1: 'MCI', 2: 'AD'}
        dx_str = dx_map.get(label, '?')
        
        node_name = f"Visit_{v_idx}"
        G.add_node(node_name, label=f"Visit {v_idx}\n[{dx_str}]", color='skyblue', shape='o')
        
        # Edge: Patient -> Visit
        G.add_edge(f"Patient_{patient_idx}", node_name)
        
        # Edge: Visit -> Next Visit (Temporal)
        if previous_node:
            G.add_edge(previous_node, node_name, label="NEXT")
        
        previous_node = node_name

    # 6. DRAW IT
    plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(G, seed=42) # Layout algorithm
    
    # Draw Nodes
    colors = [nx.get_node_attributes(G, 'color')[n] for n in G.nodes()]
    nx.draw(G, pos, with_labels=False, node_color=colors, node_size=3000, edge_color='gray')
    
    # Draw Labels
    labels = nx.get_node_attributes(G, 'label')
    nx.draw_networkx_labels(G, pos, labels, font_size=10)
    
    plt.title(f"Knowledge Graph Fragment: Patient {patient_idx}")
    plt.axis('off')
    
    # Save before showing
    plt.savefig(OUTPUT_IMG_PATH)
    print(f"Plot saved to {OUTPUT_IMG_PATH}")
    
    # plt.show() # Commented out to prevent blocking in automation. Uncomment to see window.
    print("Plot generated. Check the output file.")

if __name__ == "__main__":
    # You can change this number to see different patients!
    visualize_patient_timeline(patient_idx=0)
