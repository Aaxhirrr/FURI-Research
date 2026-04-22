import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import os

os.makedirs('data/processed', exist_ok=True)
plt.style.use('default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial']

fig = plt.figure(figsize=(10, 7), dpi=300)
ax = fig.add_subplot(111, projection='3d')
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

# Generate a complex loss/calibration surface
X = np.linspace(20, 100, 50) # Accuracy Density
Y = np.linspace(20, 100, 50) # Confidence Density
X, Y = np.meshgrid(X, Y)

# Expected Calibration Error formula penalty landscape
# ECE penalty spikes when Confidence is high but Accuracy is low (Hallucination Zone)
Z = np.abs(X - Y) * (Y*0.015)**2 

# Plot wireframe landscape
surf = ax.plot_wireframe(X, Y, Z, color='#94a3b8', linewidth=0.7, alpha=0.8)

# The Ideal Calibration Trench (Where Acc == Conf)
t = np.linspace(20, 100, 100)
ideal = np.zeros_like(t)
ax.plot(t, t, ideal, color='#10b981', linewidth=4, label='Ideal Calibration Boundary (ECE=0)')

# Map the Models into the landscape.
# C0: 85.6% Acc, highly overconfident (e.g. 98%), ECE penalty is very high
acc_c0, conf_c0, penalty_c0 = 85.6, 99.0, abs(85.6-99.0)*(99.0*0.015)**2
ax.scatter(acc_c0, conf_c0, penalty_c0, color='#ef4444', s=150, edgecolors='black', zorder=10)
# Use a white bounding box for readability
ax.text(acc_c0, conf_c0, penalty_c0 + 5, "C0 Baseline\n(Hallucination Zone)", color='#991b1b', weight='bold',
        bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.2'))
ax.plot([acc_c0, acc_c0], [conf_c0, conf_c0], [0, penalty_c0], color='#ef4444', linestyle='--', linewidth=2)

# C3: 82.3% Acc, highly calibrated confidence (84.0%), ECE penalty very low
acc_c3, conf_c3, penalty_c3 = 82.3, 84.0, abs(82.3-84.0)*(84.0*0.015)**2
ax.scatter(acc_c3, conf_c3, penalty_c3, color='#FFC627', s=200, edgecolors='black', zorder=10)
ax.text(acc_c3-5, conf_c3-10, penalty_c3 + 5, "C3 System\n(Safely Calibrated)", color='#8C1D40', weight='bold',
        bbox=dict(facecolor='white', alpha=0.8, edgecolor='none', boxstyle='round,pad=0.2'))
ax.plot([acc_c3, acc_c3], [conf_c3, conf_c3], [0, penalty_c3], color='#FFC627', linestyle='--', linewidth=2)

# Add Math Box
math_text = r"Calibration Error Constraint Loss:" "\n" r"$\mathcal{L}_{ECE} = \sum_{m} \frac{|B_m|}{N} \left| acc(B_m) - conf(B_m) \right|$"
fig.text(0.05, 0.75, math_text, fontsize=12, bbox=dict(facecolor='white', alpha=0.9, edgecolor='black', boxstyle='round,pad=0.5'))

plt.subplots_adjust(left=0.05, right=0.95, top=0.92, bottom=0.05)

ax.set_title("Expected Calibration Error (ECE): Hallucination Penalty Landscape", pad=20, weight='bold', color='black', fontsize=14)
ax.set_xlabel("\nModel Objective Accuracy (%)", fontsize=11, weight='bold')
ax.set_ylabel("\nInternal Self-Confidence (%)", fontsize=11, weight='bold')
ax.set_zlabel("ECE Loss Penalty Variance", fontsize=11, weight='bold')

ax.view_init(elev=20, azim=-40)

plt.legend(loc='lower left')
plt.savefig('data/processed/quant_ece_wireframe.png', transparent=False, facecolor='white', bbox_inches='tight')
print("✅ ECE Wireframe generated successfully")
