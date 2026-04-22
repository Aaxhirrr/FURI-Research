import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm
import os

# Ensure processed directory exists
os.makedirs('data/processed', exist_ok=True)

# Set styling
plt.style.use('default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial']
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['axes.labelsize'] = 11

# Compact, almost square figure (less "long" and cuts dead space)
fig = plt.figure(figsize=(8, 8), dpi=300)
ax = fig.add_subplot(111, projection='3d')

# Generate a complex 3D mathematical manifold representing the Patient Mesh Latent Space
X = np.linspace(-5, 5, 80)
Y = np.linspace(-5, 5, 80)
X, Y = np.meshgrid(X, Y)

# Complex biological probability topology equation
R = np.sqrt(X**2 + Y**2)
Z = (np.sin(R) / (R + 0.1)) * 10 - ((X**2 + Y**2) * 0.05)

# Plot the 3D surface
surf = ax.plot_surface(X, Y, Z, cmap=cm.inferno, linewidth=0.2, antialiased=True, alpha=0.85, edgecolor='black')

# Simulate a "Patient Trajectory" tracking through the topology (MCI to AD progression)
t = np.linspace(-4, 3, 100)
px = t
py = t + np.sin(t*3)*1
pz = (np.sin(np.sqrt(px**2 + py**2)) / (np.sqrt(px**2 + py**2) + 0.1)) * 10 - ((px**2 + py**2) * 0.05)

# Plot the trajectory line and highlight nodes (visits)
ax.plot(px, py, pz + 0.5, color='#0ea5e9', linewidth=4, label='Patient Multi-Modal Trajectory', zorder=5)

# Add visit nodes 
nodes_idx = [10, 40, 70, 99]
labels = ["Month 0\n(Baseline)", "Month 12", "Month 24\n(Agent Intercept)", "Month 36\n(Dementia Forecast)"]
colors = ['white', 'white', '#FFC627', '#ef4444']

for i, idx in enumerate(nodes_idx):
    ax.scatter(px[idx], py[idx], pz[idx] + 0.5, color=colors[i], s=150, edgecolors='black', depthshade=False, zorder=6)
    ax.text(px[idx], py[idx], pz[idx] + 2.5, labels[i], color='black', fontsize=10, weight='bold', ha='center',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.2'))

# Mathematical formulas (Slightly smaller text to fit beautifully inside the boundaries)
math_text = r"Temporal Sequencing Function:" "\n" r"$Loss = \arg\min_{\pi} \sum_{t} \left\| v_{\pi(t)} - v_{\pi(t+1)} \right\|_2$" "\n\n" \
            r"Bayesian Guardrail Probability:" "\n" r"$P_{AD} = \frac{\sum_{k} \mathbb{1}(S_{t+36}^k = 1)}{N_{twins}} \propto P(AD)\prod P(v|AD)$"

# Place floating inside the plot area's top left empty space to completely eliminate the wasted horizontal canvas
fig.text(0.12, 0.78, math_text, fontsize=11, bbox=dict(facecolor='white', alpha=0.9, edgecolor='#8C1D40', boxstyle='round,pad=0.5', linewidth=1.5))

# Subplot adjustment to keep the 3D axis tight to the edges
plt.subplots_adjust(left=0.02, right=0.98, top=0.92, bottom=0.02)

ax.set_title("Neo4j Patient Mesh: 3D Latent Space Convergence Mapping", pad=20, weight='bold', color='#8C1D40', fontsize=16)
ax.set_xlabel("Phenotypic Shift Gradient (dV/dt)", labelpad=10)
ax.set_ylabel("Neuropsychological Decay Metric", labelpad=10)
ax.set_zlabel("Latent Convergence Probability Density", labelpad=15)

# View angle tweaked slightly to show off depth better with the new square format
ax.view_init(elev=30, azim=-40)

# Save to NEW file
plt.savefig('data/processed/complex_latent_space_map_compact.png', transparent=False, facecolor='white', bbox_inches='tight')
print("✅ Generated intensely complex 3D Latent Space Map (Compact)")
