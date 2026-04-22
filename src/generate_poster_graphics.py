import matplotlib.pyplot as plt
import os
import seaborn as sns

os.makedirs('data/processed', exist_ok=True)

# --- SIMPLE ARCHITECTURAL THEME ---
plt.style.use('default')
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial']

# Colors matching the user's shared image
ASU_MAROON = "#8C1D40"
SLATE_GREY = "#4D5656" 
LIGHT_BLUE = "#EBF5FB"
models = ['C0\n(Stateless)', 'C1\n(Vector)', 'C3\n(Graph Swarm)']
colors = [LIGHT_BLUE, SLATE_GREY, ASU_MAROON]

def setup_simple_ax(title, ylabel):
    fig, ax = plt.subplots(figsize=(4, 5), dpi=300)
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')
    
    ax.set_title(title, fontsize=14, fontweight='bold', pad=15, color='black')
    ax.set_ylabel(ylabel, fontsize=11, fontweight='bold', color='black')
    
    # Simple grid and spines matching the image
    ax.grid(axis='y', linestyle='--', alpha=0.5, color='#BDC3C7')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('black')
    ax.spines['bottom'].set_color('black')
    ax.tick_params(colors='black', labelsize=10)
    
    return fig, ax

def finalize_simple_chart(ax, bars, data, ylim, is_percentage=True):
    for i, bar in enumerate(bars):
        height = bar.get_height()
        label = f"{height}%" if is_percentage else f"{height}"
        if height == 0: label = "0%"
        ax.text(bar.get_x() + bar.get_width()/2, height + (ylim[1]*0.02), label, 
                ha='center', va='bottom', fontsize=11, fontweight='bold', color='black')
    
    ax.set_ylim(ylim)
    plt.tight_layout()

# 1. TOA
def gen_toa():
    fig, ax = setup_simple_ax("2. Blind Temporal Sequencing (TOA)", "Accuracy (%)")
    bars = ax.bar(models, [0.0, 0.0, 15.5], color=colors, edgecolor='black', linewidth=1.5, width=0.6)
    finalize_simple_chart(ax, bars, [0.0, 0.0, 15.5], [0, 25])
    plt.savefig('data/processed/poster_chart_toa.png', facecolor='white', bbox_inches='tight')
    plt.close()

# 2. ECE
def gen_ece():
    fig, ax = setup_simple_ax("4. Expected Calibration Error (ECE)", "Error Score (Lower = Better)")
    bars = ax.bar(models, [3.7, 0.7, 5.2], color=colors, edgecolor='black', linewidth=1.5, width=0.6)
    finalize_simple_chart(ax, bars, [3.7, 0.7, 5.2], [0, 8], is_percentage=False)
    plt.savefig('data/processed/poster_chart_ece.png', facecolor='white', bbox_inches='tight')
    plt.close()

# 3. Accuracy (Using user's requested text from previous turn)
def gen_accuracy():
    title = "3. Clinical Forecasting Accuracy Models"
    fig, ax = setup_simple_ax(title, "Accuracy (%)")
    bars = ax.bar(['C0', 'C1', 'C3'], [26.4, 61.2, 94.2], color=colors, edgecolor='black', linewidth=1.5, width=0.6)
    
    # Subtitle for specific text
    ax.text(0.5, -0.28, "Restricted to Month 12 data to forecast Month 36 conversion.\nC0: 26.4% | C1: 61.2% | C3: 94.2% (Superior Swarm Precision)", 
            transform=ax.transAxes, ha='center', fontsize=8, color='black', fontweight='medium')
    
    finalize_simple_chart(ax, bars, [26.4, 61.2, 94.2], [0, 100])
    plt.savefig('data/processed/poster_chart_accuracy.png', facecolor='white', bbox_inches='tight')
    plt.close()

# 4. Safety (Using user's requested text from previous turn)
def gen_safety():
    title = "4. Medication Safety Guardrails"
    fig, ax = setup_simple_ax(title, "Interception Rate (%)")
    bars = ax.bar(models, [0.0, 0.0, 94.6], color=colors, edgecolor='black', linewidth=1.5, width=0.6)
    
    # Subtitle for specific text
    ax.text(0.5, -0.28, "Active Interception: The C3 Swarm actively queried Neo4j\nto block contraindicated drugs (e.g., Memantine for MCI) with a 94.6% success rate.", 
            transform=ax.transAxes, ha='center', fontsize=8, color='black', fontweight='medium')
    
    finalize_simple_chart(ax, bars, [0.0, 0.0, 94.6], [0, 110])
    plt.savefig('data/processed/poster_chart_safety.png', facecolor='white', bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    gen_toa()
    gen_ece()
    gen_accuracy()
    gen_safety()
    print("✅ Created FLAT, SIMPLE charts matching user reference.")
