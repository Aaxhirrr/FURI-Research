import pandas as pd
import os

# 1. Load the clean dataset
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, "../data/processed/clean_patient_data.csv")

df = pd.read_csv(DATA_PATH)

# 2. Get the very first patient (Row 0)
first_patient = df.iloc[0]

# 3. Convert it to a dictionary (JSON format) and print it
patient_dict = first_patient.to_dict()

print("--- PATIENT 0 DATA ---")
for key, value in patient_dict.items():
    print(f"{key}: {value}")

print(f"\nTotal columns: {len(patient_dict)}")
