import os
import json
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

# 1. SETUP: NEO4J CONNECTION (AuraDB Cloud)
NEO4J_URI = "neo4j+s://a1e8aa49.databases.neo4j.io"
NEO4J_USER = "a1e8aa49"
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")
AUTH = (NEO4J_USER, NEO4J_PASSWORD)

def find_twins(patient_rid_to_search):
    driver = GraphDatabase.driver(NEO4J_URI, auth=AUTH)
    
    # This query actually uses the SIMILAR_TO reasoning we built
    query = """
    MATCH (p1:Patient {rid: $rid})-[r:SIMILAR_TO]-(p2:Patient)
    RETURN p1.rid AS primary_rid, 
           p1.summary AS primary_summary, 
           p2.rid AS twin_rid, 
           p2.summary AS twin_summary,
           r.reason AS match_logic
    LIMIT 5
    """
    
    print(f"\n🔍 Searching FuriMasterKG for Clinical Twins of Patient {patient_rid_to_search}...")
    print("—"*80)
    
    with driver.session() as session:
        result = session.run(query, rid=patient_rid_to_search)
        found = False
        for record in result:
            found = True
            print(f"✅ MATCH FOUND: RID {record['primary_rid']} <---[SIMILAR_TO]---> RID {record['twin_rid']}")
            print(f"🔗 Match Logic: {record['match_logic']}")
            print(f"\n📄 TWIN SUMMARY (RID {record['twin_rid']}):")
            print(f"{record['twin_summary'][:300]}...") # Truncate for clean output
            print("—"*80)
            
        if not found:
            print(f"❌ No twins found for RID {patient_rid_to_search}. Ensure you ran step1c_similarity_edges.py first.")
            
    driver.close()

if __name__ == "__main__":
    # We use RID 6 as our "gold standard" for converter twins
    find_twins(6)
