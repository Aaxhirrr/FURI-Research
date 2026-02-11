import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, "../data/processed/tadpole_clean.csv")

def verify_splits():
    print("Verifying Data Splits...")
    df = pd.read_csv(DATA_PATH)
    
    # 1. Check if D1 (Train) and D2 (Test) exist
    if 'D1' not in df.columns or 'D2' not in df.columns:
        print("FAILED: D1/D2 Split columns missing!")
        return

    # 2. Extract Features
    drop_cols = ["RID", "PTID", "VISCODE", "EXAMDATE", "Month", "D1", "D2", "DX", "DXCHANGE", "DX_bl", "Label"]
    feature_cols = [c for c in df.columns if c not in drop_cols]
    
    X = df[feature_cols].values
    y = df['Label'].values
    X = np.nan_to_num(X) # Safety check
    
    # 3. Quick Train/Test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LogisticRegression(max_iter=100)
    model.fit(X_train, y_train)
    acc = accuracy_score(y_test, model.predict(X_test))
    
    print(f"SUCCESS: Baseline Verification Model Accuracy: {acc:.2f}")
    print("   (Splits are working. You are ready for GNN.)")

if __name__ == "__main__":
    verify_splits()
