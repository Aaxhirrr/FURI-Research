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
plt.rcParams['axes.titlesize'] = 18
plt.rcParams['axes.labelsize'] = 12

# Made the figure significantly wider so the text box has its own empty space on the left
fig = plt.figure(figsize=(12, 7), dpi=300)
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

# Add visit nodes (Month 0, Month 12, Month 24, Month 36)
nodes_idx = [10, 40, 70, 99]
labels = ["Month 0\n(Baseline)", "Month 12", "Month 24\n(Agent Intercept)", "Month 36\n(Dementia Forecast)"]
colors = ['white', 'white', '#FFC627', '#ef4444']

for i, idx in enumerate(nodes_idx):
    ax.scatter(px[idx], py[idx], pz[idx] + 0.5, color=colors[i], s=150, edgecolors='black', depthshade=False, zorder=6)
    # Added bounding boxes to labels so they don't blend into the 3D grid
    ax.text(px[idx], py[idx], pz[idx] + 2.5, labels[i], color='black', fontsize=11, weight='bold', ha='center',
            bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.3'))

# Mathematical formulas
math_text = r"Temporal Sequencing Function:" "\n" r"$Loss = \arg\min_{\pi} \sum_{t} \left\| v_{\pi(t)} - v_{\pi(t+1)} \right\|_2$" "\n\n" \
            r"Bayesian Guardrail Probability:" "\n" r"$P_{AD} = \frac{\sum_{k} \mathbb{1}(S_{t+36}^k = 1)}{N_{twins}} \propto P(AD)\prod P(v|AD)$"

# FIX: Moved the text box to the middle-left instead of overlapping the top title!
fig.text(0.02, 0.50, math_text, fontsize=13, bbox=dict(facecolor='white', alpha=0.95, edgecolor='#8C1D40', boxstyle='round,pad=0.5', linewidth=2))

# Shift the entire 3D plot to the right to make room for the math text box
plt.subplots_adjust(left=0.20, right=0.95, top=0.9, bottom=0.05)

# FIX: Increased padding on the title so nothing clips
ax.set_title("Neo4j Patient Mesh: 3D Latent Space Convergence Mapping", pad=30, weight='bold', color='#8C1D40', fontsize=18)
ax.set_xlabel("Phenotypic Shift Gradient (dV/dt)", labelpad=12)
ax.set_ylabel("Neuropsychological Decay Metric", labelpad=12)
ax.set_zlabel("Latent Convergence Probability Density", labelpad=15)

# View angle
ax.view_init(elev=28, azim=-45)

plt.savefig('data/processed/complex_latent_space_map.png', transparent=False, facecolor='white', bbox_inches='tight')
print("✅ Generated insanely complex 3D Latent Space Map (V2) with fixed layout!")
