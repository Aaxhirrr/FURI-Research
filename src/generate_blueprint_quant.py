import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import os

os.makedirs('data/processed', exist_ok=True)

# THEME: Architectural Blueprint (Maroon & Slate)
plt.style.use('default')
ASU_MAROON = "#8C1D40"
SLATE_DARK = "#0f172a"
SLATE_MED = "#475569"
BG_WHITE = "#ffffff"

def draw_gauge(ax, center, radius, value, label, unit="%", color=ASU_MAROON):
    # Draw background arc
    bg_arc = patches.Wedge(center, radius, 0, 180, width=radius*0.2, facecolor='#f1f5f9', edgecolor=SLATE_MED, alpha=0.3)
    ax.add_patch(bg_arc)
    
    # Draw value arc (0 to 180 degree map to 0 to 100 value)
    mapped_value = (value / 100.0) * 180
    val_arc = patches.Wedge(center, radius, 180 - mapped_value, 180, width=radius*0.2, facecolor=color, edgecolor=SLATE_DARK, alpha=0.8)
    ax.add_patch(val_arc)
    
    # Text
    ax.text(center[0], center[1], f"{value}{unit}", ha='center', va='center', fontsize=16, fontweight='black', color=SLATE_DARK)
    ax.text(center[0], center[1] - radius*0.3, label.upper(), ha='center', fontsize=9, fontweight='bold', color=SLATE_MED)

def draw_trace_line(ax, start, end, label):
    ax.annotate('', xy=end, xytext=start,
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=.2", color=SLATE_MED, lw=1.5, alpha=0.5))
    mid = ((start[0]+end[0])/2, (start[1]+end[1])/2 + 0.5)
    ax.text(mid[0], mid[1], label, fontsize=8, color=SLATE_MED, style='italic', ha='center', rotation=15)

def draw_calibration_cloud(ax, center, error, label):
    # Error cloud: tighter scatter = better calibration
    # error of 5.2 (High) vs 0.7 (Low)
    num_points = 200
    spread = error * 0.1
    x = np.random.normal(center[0], spread, num_points)
    y = np.random.normal(center[1], spread, num_points)
    
    ax.scatter(x, y, s=5, alpha=0.3, color=ASU_MAROON, edgecolor='none')
    
    # Circular boundary
    circle = patches.Circle(center, 0.8, fill=False, edgecolor=SLATE_MED, linestyle='--', alpha=0.5)
    ax.add_patch(circle)
    
    ax.text(center[0], center[1] - 1.2, label.upper(), ha='center', fontsize=10, fontweight='black', color=SLATE_DARK)
    ax.text(center[0], center[1] + 1.0, f"Error Index: {error}", ha='center', fontsize=8, color=SLATE_MED, style='italic')

# --- MAIN RENDERING ---
fig, ax = plt.subplots(figsize=(10, 14), dpi=300)
ax.set_facecolor(BG_WHITE)
fig.patch.set_facecolor(BG_WHITE)

# Background Watermark / Grid
grid_size = 20
for x in range(0, grid_size):
    ax.axvline(x, color=SLATE_MED, alpha=0.03, lw=0.5)
for y in range(0, grid_size*2):
    ax.axhline(y, color=SLATE_MED, alpha=0.03, lw=0.5)

# HEADER BLOCK
ax.add_patch(patches.Rectangle((1, 26), 18, 2, facecolor='#f8fafc', edgecolor=SLATE_DARK, linewidth=2))
ax.text(10, 27, "C3 SYSTEM: MULTI-AGENT QUANTITATIVE BLUEPRINT", ha='center', va='center', fontsize=18, fontweight='black', color=ASU_MAROON)
ax.text(1.5, 26.5, "REV: 3.14-b", fontsize=8, color=SLATE_MED)
ax.text(18.5, 26.5, "SYSTEM: FuriMasterKG", fontsize=8, color=SLATE_MED, ha='right')

# SECTION 1: GAUGES (Diagnostic Accuracy)
# Row of three gauges for C0, C1, C3
draw_gauge(ax, (4, 22), 2, 85.6, "C0 Baseline")
draw_gauge(ax, (10, 22), 2, 86.2, "C1 Vector")
draw_gauge(ax, (16, 22), 2, 82.3, "C3 System", color=ASU_MAROON)

# SECTION 2: FLOW TRACES (Safety & TOA)
# We show a "System Path" 
ax.text(10, 18, "ALGORITHMIC MOMENTUM & SAFETY INTERCEPT", ha='center', fontsize=12, fontweight='black', color=SLATE_DARK)
ax.add_patch(patches.FancyBboxPatch((2, 13), 16, 4, boxstyle="round,pad=0.3", facecolor='none', edgecolor=SLATE_MED, alpha=0.2))

# Nodes
ax.scatter([4, 10, 16], [15, 15, 15], s=100, color=SLATE_DARK, zorder=5)
ax.text(4, 14, "Input Stream", ha='center', fontsize=8)
ax.text(10, 14, "Swarm Logic", ha='center', fontsize=8)
ax.text(16, 14, "Output Forecast", ha='center', fontsize=8)

draw_trace_line(ax, (4, 15), (10, 15), "Safety Intercept: 94.6%")
draw_trace_line(ax, (10, 15), (16, 15), "Temporal Accuracy (TOA): 15.5%")

# SECTION 3: CALIBRATION CLOUDS (ECE)
ax.text(10, 10, "PROBABILISTIC DENSITY CALIBRATION (ECE)", ha='center', fontsize=12, fontweight='black', color=SLATE_DARK)
draw_calibration_cloud(ax, (5, 6), 3.7, "C0 Baseline")
draw_calibration_cloud(ax, (10, 6), 0.7, "C1 Vector")
draw_calibration_cloud(ax, (15, 6), 5.2, "C3 Swarm")

# FOOTER MATH BLOCK
math_box = patches.Rectangle((2, 1), 16, 1.5, facecolor='none', edgecolor=SLATE_DARK, linewidth=1, linestyle='--')
ax.add_patch(math_box)
ax.text(10, 1.75, r"$Model Convergence = \int (\text{Acc} \cdot \text{Safety} \cdot \alpha) dt$", ha='center', fontsize=10, color=SLATE_MED)

# Setting limits and hiding actual plot axes
ax.set_xlim(0, 20)
ax.set_ylim(0, 30)
ax.axis('off')

plt.tight_layout()
plt.savefig('data/processed/algorithmic_blueprint_quant.png', facecolor=BG_WHITE, bbox_inches='tight')

print("✅ 'Blueprint' Visual Generated: High-density schematic output.")
