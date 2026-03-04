import json
import os

def get_sort_key(patient_record):
    rid = patient_record.get("RID", 0)
    viscode = patient_record.get("VISCODE", "")
    
    # Convert 'bl' to month 0, and 'm06', 'm120', etc. into actual integers
    if viscode == "bl":
        month = 0
    elif viscode.startswith("m") and viscode[1:].isdigit():
        month = int(viscode[1:])
    else:
        month = 9999 # Fallback just in case there's a weird value
        
    return (rid, month)

def main():
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(SCRIPT_DIR, "../data/processed/patient_narratives_fast_4omini.json")
    output_file = os.path.join(SCRIPT_DIR, "../data/processed/patient_narratives_sorted.json")
    
    print(f"Loading data from {input_file}...")
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Could not find {input_file}. Make sure you are running this from the right directory.")
        return

    print(f"Sorting {len(data)} narratives by RID and timeline...")
    # Sort the data using our custom chronological key
    sorted_data = sorted(data, key=get_sort_key)
    
    # Save the beautifully sorted data
    with open(output_file, 'w') as f:
        json.dump(sorted_data, f, indent=4)
        
    print(f"✅ Success! Your perfectly ordered timeline is saved in {output_file}")

if __name__ == "__main__":
    main()
