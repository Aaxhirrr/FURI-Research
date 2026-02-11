import pandas as pd
import os

# Dynamic path to find your data
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, "../data/processed/tadpole_clean.csv")

def profile_gnn_features():
    print("Generating GNN Data Profile...")
    if not os.path.exists(DATA_PATH):
        print("Error: Data not found. Run 1_preprocess_data.py first.")
        return

    df = pd.read_csv(DATA_PATH)
    
    # The specific "Region Data" nodes your professor asked for
    # (Plus cognitive scores to check distribution)
    target_cols = [
        "Hippocampus", "Ventricles", "WholeBrain", "Entorhinal", "Fusiform", 
        "ICV", "MMSE", "ADAS13"
    ]
    
    print("-" * 65)
    print(f"{'FEATURE':<15} | {'MIN':<10} | {'MAX':<10} | {'MEAN':<10} | {'STD DEV':<10}")
    print("-" * 65)
    
    for col in target_cols:
        if col in df.columns:
            # simple stats
            c_min = df[col].min()
            c_max = df[col].max()
            c_mean = df[col].mean()
            c_std = df[col].std()
            
            print(f"{col:<15} | {c_min:<10.2f} | {c_max:<10.2f} | {c_mean:<10.2f} | {c_std:<10.2f}")
    print("-" * 65)
    print("DONE. Use 'Mean +/- StdDev' to define your Knowledge Graph edges.")

if __name__ == "__main__":
    profile_gnn_features()
