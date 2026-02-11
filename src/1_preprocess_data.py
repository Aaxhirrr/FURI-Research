import pandas as pd
import numpy as np
import os

# Config - paths relative to script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

RAW_DATA_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "TADPOLE_D1_D2.csv")
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "data", "processed", "tadpole_clean.csv")

KEEP_COLUMNS = [
    # Identity & Time
    "RID", "PTID", "VISCODE", "EXAMDATE", "Month", "D1", "D2",
    # Labels
    "DX", "DXCHANGE", "DX_bl",
    # Demographics & Genetics
    "AGE", "PTGENDER", "PTEDUCAT", "APOE4", 
    # Cognitive Function
    "MMSE", "ADAS11", "ADAS13", "CDRSB", "FAQ", 
    "RAVLT_immediate", "RAVLT_learning", "RAVLT_forgetting",
    # MRI Volumes
    "Hippocampus", "Ventricles", "WholeBrain", "Entorhinal", 
    "Fusiform", "MidTemp", "ICV",
    # Biomarkers
    "FDG", "AV45"
]

def preprocess_tadpole_v1():
    print(f"Loading TADPOLE D1/D2...")
    
    # Load required columns only
    try:
        df = pd.read_csv(RAW_DATA_PATH, usecols=lambda c: c in KEEP_COLUMNS, low_memory=False)
    except Exception as e:
        print(f"Error loading columns: {e}")
        return

    print(f"   Raw Shape: {df.shape}")

    # Standardize months from VISCODE if needed
    if 'Month' not in df.columns:
        df['Month'] = df['VISCODE'].apply(lambda x: 0 if x=='bl' else int(x[1:]) if str(x).startswith('m') else -1)

    # Map diagnosis to labels: 0=CN, 1=MCI, 2=AD
    dx_map = {
        'CN': 0, 'NL': 0, 
        'MCI': 1, 'EMCI': 1, 'LMCI': 1, 
        'Dementia': 2, 'AD': 2
    }
    df['Label'] = df['DX'].map(dx_map)
    
    # Drop rows without diagnosis
    df = df.dropna(subset=['Label'])

    # Mean imputation for missing values
    numeric_cols = [c for c in df.columns if c not in ["RID", "PTID", "VISCODE", "EXAMDATE", "DX", "DX_bl", "Label"]]
    
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = df[col].fillna(df[col].mean())

    # Sort by patient and time
    df = df.sort_values(by=["RID", "Month"])

    # Save processed data
    os.makedirs("../data/processed", exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    
    print("-" * 30)
    print(f"✅ SUCCESS: V1 Dataset saved to {OUTPUT_PATH}")
    print(f"   - Patients: {df['RID'].nunique()}")
    print(f"   - Visits: {len(df)}")
    print(f"   - Features: {len(df.columns)}")
    print("-" * 30)

if __name__ == "__main__":
    preprocess_tadpole_v1()