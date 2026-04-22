import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Apply beautiful, modern styling tailored for FURI (Using ASU-inspired colors and modern clinical blues)
sns.set_theme(style="white", context="talk")
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial']

# The FURI project data
models = ['C0 (Stateless)', 'C1 (Vector RAG)', 'C3 (Graph Swarm)']
acc_scores = [85.6, 86.2, 82.3]       # Diagnostic Accuracy
ece_scores = [3.7, 0.7, 5.2]          # Expected Calibration Error
toa_scores = [0.0, 0.0, 15.5]         # Temporal Order Accuracy
safe_scores = [100.0, 100.0, 94.6]    # Safety Compliance (100 - violation)

# Stunning Color Palettes
# We will use Muted Slate for the baselines, and a vivid Neon Cyan or Deep Crimson for our winning architecture!
col_baselines = "#94a3b8"  # Slate Gray
col_winner = "#0ea5e9"     # Medical Clinical Cyan

colors = [col_baselines, col_baselines, col_winner]

fig, axs = plt.subplots(2, 2, figsize=(16, 12), dpi=300)
fig.suptitle('Quantitative Evaluation of Alzheimer\'s Disease Forecasting Architectures', 
             fontsize=24, weight='bold', color='#1e293b', y=0.98)

# Helper function to add labels
def add_labels(ax, bars, is_percent=True, invert_y=False):
    for bar in bars:
        height = bar.get_height()
        label_text = f"{height:.1f}%" if is_percent else f"{height:.1f}"
        y_pos = height + 1 if not invert_y else height + 0.1
        ax.annotate(label_text,
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4),  
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=14, weight='bold', color='#334155')

# --- Plot 1: Diagnostic Accuracy ---
bars1 = axs[0, 0].bar(models, acc_scores, color=colors, edgecolor='none', width=0.6)
axs[0, 0].set_ylim(0, 100)
axs[0, 0].set_title('Diagnostic Accuracy', fontsize=18, weight='bold')
axs[0, 0].set_ylabel('Accuracy (%)', fontsize=14, weight='bold')
axs[0, 0].grid(axis='y', linestyle='--', alpha=0.4)
sns.despine(ax=axs[0,0])
add_labels(axs[0, 0], bars1)

# --- Plot 2: Temporal Order Accuracy (The Blind Test) ---
bars2 = axs[0, 1].bar(models, toa_scores, color=['#cbd5e1', '#94a3b8', '#8b5cf6'], edgecolor='none', width=0.6) # Highlight with Purple
axs[0, 1].set_ylim(0, 25)
axs[0, 1].set_title('Blind Temporal Sequencing (TOA)', fontsize=18, weight='bold')
axs[0, 1].set_ylabel('Sequential Accuracy (%)', fontsize=14, weight='bold')
axs[0, 1].grid(axis='y', linestyle='--', alpha=0.4)
sns.despine(ax=axs[0,1])
add_labels(axs[0, 1], bars2)
# Special note on TOA chart
axs[0, 1].text(1, 10, 'Models C0 and C1 completely failed\ntemporal reasoning when stripped\nof chronological timestamps.',
        bbox=dict(facecolor='red', alpha=0.1, edgecolor='none', boxstyle='round,pad=1'),
        ha='center', va='center', color='#991b1b', fontsize=11, weight='bold')


# --- Plot 3: FDA Safety Compliance ---
bars3 = axs[1, 0].bar(models, safe_scores, color=['#d1d5db', '#d1d5db', '#10b981'], edgecolor='none', width=0.6) # Highlight with Emerald Green
axs[1, 0].set_ylim(0, 110)
axs[1, 0].set_title('FDA Drug Safety Compliance', fontsize=18, weight='bold')
axs[1, 0].set_ylabel('Compliance Rate (%)', fontsize=14, weight='bold')
axs[1, 0].grid(axis='y', linestyle='--', alpha=0.4)
sns.despine(ax=axs[1,0])
add_labels(axs[1, 0], bars3)

# --- Plot 4: Expected Calibration Error ---
bars4 = axs[1, 1].bar(models, ece_scores, color=colors, edgecolor='none', width=0.6)
axs[1, 1].set_ylim(0, 10)
axs[1, 1].set_title('Expected Calibration Error (ECE)', fontsize=18, weight='bold')
axs[1, 1].set_ylabel('Error Score (Lower is Better)', fontsize=14, weight='bold')
axs[1, 1].grid(axis='y', linestyle='--', alpha=0.4)
sns.despine(ax=axs[1,1])
add_labels(axs[1, 1], bars4, is_percent=False)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('data/processed/full_quantitative_evaluation.png', transparent=False, facecolor='white', bbox_inches='tight')
print("✅ Output saved to: data/processed/full_quantitative_evaluation.png")
