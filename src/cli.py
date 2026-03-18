import os
import argparse
import sys
from neo4j import GraphDatabase

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# 1. SETUP: NEO4J CONNECTION
URI = "neo4j+s://a1e8aa49.databases.neo4j.io"
AUTH = ("a1e8aa49", os.environ.get("NEO4J_PASSWORD"))

class FuriMasterKGGraph:
    def __init__(self, uri, auth):
        self.driver = GraphDatabase.driver(uri, auth=auth)

    def close(self):
        self.driver.close()

    def print_status(self):
        """Fetches the total patient count linked to the Master Node."""
        query = """
        MATCH (c:Cohort {name: 'ADNI_1730_Master'})
        MATCH (p:Patient)-[:MEMBER_OF]->(c)
        RETURN count(p) as total_patients, c.total_n as expected_n
        """
        with self.driver.session() as session:
            result = session.run(query).single()
            print("\n" + "="*50)
            print("🚀 FuriMasterKG Status")
            print("="*50)
            print(f"✅ Connection: ONLINE")
            print(f"🧬 Active Patient Nodes: {result['total_patients']} / {result['expected_n']}")
            print("="*50 + "\n")

    def print_master_stats(self):
        """Fetches the Global Ground Truth from the Macro-KG."""
        query = """
        MATCH (mci:ClinicalState {name: 'MCI'})-[r:CONVERTS_TO]->(ad:ClinicalState {name: 'AD'})
        MATCH (atrophy:Biomarker {name: 'Hippocampal Atrophy'})-[c:CORRELATES_WITH]->(mmse:CognitiveTest)
        RETURN r.rate as conversion_rate, r.avg_years as avg_years, 
               atrophy.annual_rate_percent as atrophy_rate, c.r_value as pearson_r
        """
        with self.driver.session() as session:
            result = session.run(query).single()
            print("\n" + "="*50)
            print("📊 GLOBAL COHORT STATS (MACRO-KG)")
            print("="*50)
            print(f"📉 MCI-to-Dementia Conversion: {result['conversion_rate'] * 100}% (over {result['avg_years']} yrs)")
            print(f"🧠 Avg Annual Hippocampal Atrophy: {result['atrophy_rate']}%")
            print(f"🔗 Biomarker-to-Cognition Correlation: r = {result['pearson_r']}")
            print("="*50 + "\n")

    def query_patient(self, rid):
        """Fetches a specific patient and their 'Clinical Twins' via the P2P Mesh."""
        query = """
        MATCH (p:Patient {rid: $rid})
        OPTIONAL MATCH (p)-[:SIMILAR_TO]-(twin:Patient)
        RETURN p.summary as summary, p.total_visits as visits, collect(twin.rid) as twins
        """
        with self.driver.session() as session:
            result = session.run(query, rid=int(rid)).single()
            
            if not result or not result['summary']:
                print(f"\n❌ Patient RID {rid} not found in the Knowledge Graph.\n")
                return

            print("\n" + "="*50)
            print(f"👤 PATIENT PROFILE: RID {rid}")
            print("="*50)
            print(f"📅 Total Visits: {result['visits']}")
            print(f"👯 Clinical Twins Found: {len(result['twins'])} matching patients")
            if len(result['twins']) > 0:
                print(f"   Sample Twins: {result['twins'][:5]}...")
            print("\n📄 TIMELINE SUMMARY:")
            print(result['summary'])
            print("="*50 + "\n")

def main():
    parser = argparse.ArgumentParser(description="FuriMasterKG Terminal Interface")
    parser.add_argument("--status", action="store_true", help="Check Neo4j DB connection and patient count")
    parser.add_argument("--stats", action="store_true", help="Display global cohort benchmarks (Macro-KG)")
    parser.add_argument("--query", type=int, metavar="RID", help="Fetch a patient's timeline and clinical twins")

    args = parser.parse_args()
    
    # If no arguments provided, show help
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    # Initialize Neo4j Connection
    kg = FuriMasterKGGraph(URI, AUTH)

    try:
        if args.status:
            kg.print_status()
        if args.stats:
            kg.print_master_stats()
        if args.query:
            kg.query_patient(args.query)
    finally:
        kg.close()

if __name__ == "__main__":
    main()
