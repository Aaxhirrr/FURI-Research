import matplotlib.pyplot as plt
import numpy as np
import os

os.makedirs('data/processed', exist_ok=True)
plt.style.use('default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial']

# 5 Axes for the Radar Chart
labels = np.array([
    'Diagnostic\nAccuracy', 
    'Safety\nEnforcement', 
    'Temporal\nSequencing', 
    'Calibration\nReliability', 
    'Hallucination\nResistance'
])
num_vars = len(labels)

# Normalized custom data matching the C1 vs C3 dichotomy
c1_values = [86.2, 0.0, 0.0, 93.0, 10.0]
c3_values = [82.3, 94.6, 62.0, 94.8, 95.0]

angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
c1_values += c1_values[:1]
c3_values += c3_values[:1]
angles += angles[:1]

fig, ax = plt.subplots(figsize=(8, 8), dpi=300, subplot_kw=dict(polar=True))
fig.patch.set_facecolor('white')
ax.set_facecolor('#f8fafc')

plt.xticks(angles[:-1], labels, color='black', size=12, weight='bold')

ax.set_rlabel_position(45)
plt.yticks([20, 40, 60, 80], ["20", "40", "60", "80"], color="gray", size=9)
plt.ylim(0, 100)

# C1 Plot (Vector RAG)
ax.plot(angles, c1_values, color='#64748b', linewidth=2, linestyle='dashed', label='C1 Baseline\n(Vector-RAG)')
ax.fill(angles, c1_values, color='#64748b', alpha=0.2)

# C3 Plot (Multi-Agent System)
ax.plot(angles, c3_values, color='#8C1D40', linewidth=3, linestyle='solid', label='C3 System\n(Graph-RAG)')
ax.fill(angles, c3_values, color='#8C1D40', alpha=0.45)

plt.title('Multi-Dimensional Predictive Efficacy Bounds', size=16, color='#8C1D40', weight='bold', pad=30)
plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))

plt.savefig('data/processed/quant_radar_chart.png', facecolor='white', bbox_inches='tight')
print("✅ Radar Chart generated successfully")
