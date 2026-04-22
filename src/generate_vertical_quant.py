import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import os

os.makedirs('data/processed', exist_ok=True)

# --- THEME CONFIGURATION ---
plt.style.use('default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Inter', 'Segoe UI', 'Arial']
ASU_MAROON = "#8C1D40"
ASU_GOLD = "#FFC627"
SLATE_DARK = "#0f172a"
SLATE_MED = "#334155"
GLOW_COLOR = "#FFD700"

# --- DATA ---
models = ['C0 Baseline', 'C1 Vector', 'C3 Swarm']
metrics = {
    'Accuracy': {
        'data': [26.4, 61.2, 94.2],
        'ylim': [0, 100],
        'unit': '%',
        'formula': r'$Acc = \frac{TP+TN}{N}$',
        'title': 'System Diagnostic Accuracy'
    },
    'TOA': {
        'data': [0.0, 0.0, 15.5],
        'ylim': [0, 25],
        'unit': '%',
        'formula': r'$P_{toa} = \mathbb{1}(\Delta t \geq 0)$',
        'title': 'Temporal Order Reasoning'
    },
    'Safety': {
        'data': [0.0, 0.0, 94.6],
        'ylim': [0, 110],
        'unit': '%',
        'formula': r'$\Gamma_{guard} = \prod p(v \notin \mathcal{T})$',
        'title': 'Swarm Safety Guardrails'
    },
    'Calibration': {
        'data': [3.7, 0.7, 5.2],
        'ylim': [0, 8],
        'unit': '',
        'formula': r'$\mathcal{L}_{ece} = \sum \frac{|B_m|}{N} |acc - conf|$',
        'title': 'Expected Calibration Error'
    }
}

# --- HELPER: GRADIENT BARS ---
def draw_gradient_bar(ax, x, y, width, bottom=0, base_color="#cbd5e1"):
    # Create a gradient from light grey to the color
    cmap = LinearSegmentedColormap.from_list("custom_grad", [base_color, "#ffffff"], N=100)
    for i in range(100):
        slice_height = y / 100
        ax.add_patch(patches.Rectangle((x - width/2, bottom + i*slice_height), width, slice_height, 
                                       facecolor=cmap(i/100), edgecolor='none', alpha=0.9))
    # Add a clean border
    ax.add_patch(patches.Rectangle((x - width/2, bottom), width, y, fill=False, edgecolor=base_color, linewidth=2))

def draw_premium_subplot(ax, metric_key, metric_data):
    ax.set_facecolor('#ffffff')
    ax.grid(axis='y', linestyle=':', alpha=0.3, color=SLATE_MED)
    
    # Titles and Formula
    ax.text(-0.4, metric_data['ylim'][1]*0.85, metric_data['formula'], fontsize=12, color=SLATE_MED, alpha=0.5, style='italic')
    ax.set_title(metric_data['title'].upper(), loc='left', fontsize=11, fontweight='black', color=ASU_MAROON, pad=15)
    
    # Bars
    x_pos = np.arange(len(models))
    width = 0.5
    
    colors = ["#e2e8f0", "#94a3b8", ASU_MAROON]
    
    for i, val in enumerate(metric_data['data']):
        if val > 0:
            draw_gradient_bar(ax, x_pos[i], val, width, base_color=colors[i])
            # Data Label Callout (Glassmorphism style)
            ax.text(x_pos[i], val + (metric_data['ylim'][1]*0.05), f"{val}{metric_data['unit']}", 
                    ha='center', va='bottom', fontsize=12, fontweight='bold', color=colors[i],
                    bbox=dict(facecolor='white', alpha=0.8, edgecolor=colors[i], boxstyle='round,pad=0.3', linewidth=1.5))
        else:
            # Empty state for 0% results
            ax.text(x_pos[i], metric_data['ylim'][1]*0.05, "N/A", ha='center', color="#94a3b8", alpha=0.5, fontsize=10)

    # Delta Arrow if C3 is high
    if metric_key in ['TOA', 'Safety'] and metric_data['data'][2] > 0:
        ax.annotate('', xy=(x_pos[2], metric_data['data'][2]), xytext=(x_pos[1], 2),
                    arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.3", color=ASU_MAROON, lw=2, linestyle='--'))
        ax.text((x_pos[1]+x_pos[2])/2, metric_data['data'][2]/2, "ENGINEERED SHIFT", 
                color=ASU_MAROON, fontweight='bold', fontsize=8, rotation=20, ha='center',
                bbox=dict(facecolor='white', alpha=1, edgecolor='none', pad=0))

    # Styling axes
    ax.set_xticks(x_pos)
    ax.set_xticklabels(models, fontsize=9, fontweight='medium', color=SLATE_MED)
    ax.set_ylim(metric_data['ylim'])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#e2e8f0')
    ax.spines['bottom'].set_color('#e2e8f0')
    ax.tick_params(axis='y', colors=SLATE_MED, labelsize=8)

# --- MAIN RENDER ---
fig = plt.figure(figsize=(6, 18), dpi=300)
fig.patch.set_facecolor('white')

# Add a subtle background texture (Tech Grid)
for i in range(10):
    fig.text(0.1, i/10, "////////////////////////////////////////////////////////////////////////////////", 
             alpha=0.03, color=ASU_MAROON, fontsize=20, rotation=45, ha='left')

gs = fig.add_gridspec(4, 1, hspace=0.35)

for i, key in enumerate(metrics.keys()):
    ax = fig.add_subplot(gs[i])
    draw_premium_subplot(ax, key, metrics[key])

# Overall Dashboard Header
fig.text(0.5, 0.98, "QUANTITATIVE PERFORMANCE MATRICES", ha='center', fontsize=16, fontweight='black', color=SLATE_DARK)
fig.text(0.5, 0.97, "MULTI-AGENT SYSTEM (C3) VS STATE-OF-THE-ART (C1)", ha='center', fontsize=9, color=ASU_MAROON, alpha=0.7)

plt.subplots_adjust(top=0.95, bottom=0.05, left=0.15, right=0.95)
plt.savefig('data/processed/quant_results_premium_vertical.png', facecolor='white', bbox_inches='tight')

print("✅ 'Wow' Factor Achieved: Generated Premium Quantitative Dashboard.")
