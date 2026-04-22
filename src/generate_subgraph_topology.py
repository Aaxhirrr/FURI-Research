import matplotlib.pyplot as plt
import networkx as nx
import os

os.makedirs('data/processed', exist_ok=True)
plt.style.use('default')
plt.rcParams['font.family'] = 'sans-serif'

# 1. Create a simulated graph of "Clinical Twins" (Micro-KG)
G = nx.barabasi_albert_graph(250, 2)
pos = nx.spring_layout(G, k=0.15, iterations=40, seed=42)

fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
# Make the background of the figure white so it drops onto the poster natively
fig.patch.set_facecolor('white')
# But the graph itself has a deep computational dark background
ax.set_facecolor('#0f172a') 

active_patient = 0
twins = list(G.neighbors(active_patient))
subgraph_nodes = twins + [active_patient]
background_nodes = [n for n in G.nodes() if n not in subgraph_nodes]

# Draw dark isolated background patients
nx.draw_networkx_nodes(G, pos, nodelist=background_nodes, node_color='#334155', node_size=15, alpha=0.3, ax=ax)
nx.draw_networkx_edges(G, pos, alpha=0.05, edge_color='#475569', ax=ax)

# Draw the Clinical Twins Cluster
nx.draw_networkx_nodes(G, pos, nodelist=twins, node_color='#FFC627', node_size=80, edgecolors='white', ax=ax)
edges = [(active_patient, twin) for twin in twins]
nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color='#0ea5e9', width=2.5, alpha=0.9, ax=ax)

# Active Patient
nx.draw_networkx_nodes(G, pos, nodelist=[active_patient], node_color='#8C1D40', node_size=250, edgecolors='white', linewidths=2.5, ax=ax)

# Labels
ax.text(pos[active_patient][0], pos[active_patient][1] + 0.1, 'Active Patient\n(Querying Twin Embeddings)', color='white', weight='bold', ha='center', fontsize=11)
ax.text(pos[twins[0]][0], pos[twins[0]][1] - 0.1, 'Localized "Clinical Twin" Mesh Boundary', color='#FFC627', weight='bold', ha='center', fontsize=11)

# Math block
text_str = r"$\bf{Micro}$-$\bf{KG}$ $\bf{Patient}$ $\bf{Mesh}$ $\bf{Topology}$" "\n" \
           r"$d(v_{active}, v_{twin}) = \sqrt{\sum w_i (v_{active,i} - v_{twin,i})^2} \leq \tau$" "\n" \
           r"$\text{Forecast} \propto \frac{1}{K} \sum_{k \in Twins} \mathbb{1}(S^k_{t+36} = AD)$"

# Placed into the top left over the dark background
fig.text(0.15, 0.82, text_str, color='white', fontsize=13, bbox=dict(facecolor='#1e293b', alpha=0.9, edgecolor='#0ea5e9', boxstyle='round,pad=0.5'))

ax.set_title("Algorithmic Manifold of Micro-KG Clinical Twins", color='black', weight='bold', fontsize=18, pad=20)
ax.axis('off')

# Ensure the plot edges align smoothly on the white figure
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.spines['left'].set_visible(False)

plt.subplots_adjust(left=0.05, right=0.95, top=0.90, bottom=0.05)
plt.savefig('data/processed/quant_subgraph_topology.png', facecolor='white', bbox_inches='tight')
print("✅ Sub-Graph Topology generated successfully")
