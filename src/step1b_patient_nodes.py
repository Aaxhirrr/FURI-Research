import json
import os
from neo4j import GraphDatabase
from tqdm import tqdm

# 1. SETUP: NEO4J CONNECTION
NEO4J_URI = "neo4j+s://a1e8aa49.databases.neo4j.io"
NEO4J_USER = "a1e8aa49"
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")
AUTH = (NEO4J_USER, NEO4J_PASSWORD)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Reading the timelines we generated earlier
input_file = os.path.join(SCRIPT_DIR, '../data/processed/CLEAN_1730_TIMELINES.json')

def import_patients(tx, patient_data):
    """Creates the Patient Node and links it to the Master Cohort."""
    query = """
    MATCH (c:Cohort {name: 'ADNI_1730_Master'})
    MERGE (p:Patient {rid: $rid})
    SET p.total_visits = $visits,
        p.summary = $summary
    MERGE (p)-[:MEMBER_OF]->(c)
    """
    tx.run(query, rid=patient_data['RID'], visits=patient_data['Total_Visits'], summary=patient_data['Timeline_Summary'])

def main():
    print(f"[INFO] Loading 1,730 clean timelines from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Filter out any null entries we found earlier (just in case)
    clean_data = [p for p in data if p is not None and 'RID' in p]

    driver = GraphDatabase.driver(NEO4J_URI, auth=AUTH)
    with driver.session() as session:
        print("[INFO] Injecting patients into the Knowledge Graph...")
        for patient in tqdm(clean_data):
            session.execute_write(import_patients, patient)
            
    driver.close()
    print(f"[SUCCESS] {len(clean_data)} patients are now linked to the Master Foundation.")

if __name__ == "__main__":
    main()
