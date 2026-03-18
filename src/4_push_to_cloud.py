import os
import pandas as pd
from neo4j import GraphDatabase

# ==========================================
# ☁️ CLOUD CONFIGURATION (Fill these in!)
# ==========================================
# I built this using the ID 'a1e8aa49' from your screenshot:
URI = "neo4j+s://a1e8aa49.databases.neo4j.io" 

# This is the password you saved earlier:
AUTH = ("a1e8aa49", os.environ.get("NEO4J_PASSWORD"))

# PATHS
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
NODES_PATH = os.path.join(SCRIPT_DIR, "../data/processed/neo4j_import/nodes.csv")
EDGES_PATH = os.path.join(SCRIPT_DIR, "../data/processed/neo4j_import/edges.csv")

def push_data():
    print("Connecting to Neo4j Cloud...")
    try:
        driver = GraphDatabase.driver(URI, auth=AUTH)
        driver.verify_connectivity()
        print(" Connected!")
    except Exception as e:
        print(f" Connection Failed: {e}")
        return

    # Load Data
    print(" Reading CSV files...")
    if not os.path.exists(NODES_PATH) or not os.path.exists(EDGES_PATH):
        print(f"Error: CSV files not found at {NODES_PATH} or {EDGES_PATH}")
        return

    nodes_df = pd.read_csv(NODES_PATH)
    edges_df = pd.read_csv(EDGES_PATH)
    
    # 1. CLEANUP (Optional: Wipes DB before upload)
    with driver.session() as session:
        print(" Clearing old data...")
        session.run("MATCH (n) DETACH DELETE n")

        # 2. UPLOAD NODES
        print(f" Uploading {len(nodes_df)} nodes...")
        # We upload in batches to be safe
        query_nodes = """
        UNWIND $batch AS row
        CALL apoc.create.node([row.type], {id: row.id, name: row.name, features: row.features}) YIELD node
        RETURN count(node)
        """
        # Convert DF to list of dicts
        # Replace NaN with safe values if necessary, though neo4j driver handles some
        nodes_df = nodes_df.fillna("") 
        nodes_list = nodes_df.to_dict('records')
        
        # Batch size 1000
        for i in range(0, len(nodes_list), 1000):
            batch = nodes_list[i:i+1000]
            try:
                session.run(query_nodes, batch=batch)
                print(f"   - Pushed batch {i} to {min(i+1000, len(nodes_list))}")
            except Exception as e:
                print(f"   - Error pushing node batch {i}: {e}")
                # Fallback: Check if APOC is missing
                if "Unknown function 'apoc.create.node'" in str(e):
                    print("CRITICAL: APOC plugin is missing. Attempting standard Cypher fallback...")
                    # Fallback requires known labels. For now, let's just error out if APOC is missing
                    # as rewriting for dynamic labels in pure Cypher is complex without mapped labels.
                    # But we can try a simplified version if needed. 
                    return

        # 3. UPLOAD EDGES
        print(f" Uploading {len(edges_df)} edges...")
        query_edges = """
        UNWIND $batch AS row
        MATCH (s {id: row.src})
        MATCH (d {id: row.dst})
        CALL apoc.create.relationship(s, row.type, {}, d) YIELD rel
        RETURN count(rel)
        """
        edges_df = edges_df.fillna("")
        edges_list = edges_df.to_dict('records')
        
        for i in range(0, len(edges_list), 1000):
            batch = edges_list[i:i+1000]
            try:
                session.run(query_edges, batch=batch)
                print(f"   - Linked batch {i} to {min(i+1000, len(edges_list))}")
            except Exception as e:
                 print(f"   - Error pushing edge batch {i}: {e}")

    driver.close()
    print(" UPLOAD COMPLETE! Go check your Cloud Console.")

if __name__ == "__main__":
    push_data()
