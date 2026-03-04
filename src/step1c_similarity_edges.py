import os
from neo4j import GraphDatabase

# 1. SETUP: NEO4J CONNECTION
NEO4J_URI = "neo4j+s://a1e8aa49.databases.neo4j.io"
NEO4J_USER = "a1e8aa49"
NEO4J_PASSWORD = "O6Km241NG57sX1iUnIkduX1WwL9mu9wd7YUWQf9F3pU"
AUTH = (NEO4J_USER, NEO4J_PASSWORD)

def create_p2p_edges(tx):
    """
    Creates SIMILAR_TO edges between patients who share clinical profiles.
    We limit the margin to keep the graph from becoming a 'hairball'.
    """
    # Query 1: Link patients who share the same extreme atrophy rates (>5%)
    atrophy_query = """
    MATCH (p1:Patient), (p2:Patient)
    WHERE p1.rid < p2.rid 
      AND p1.summary CONTAINS 'atrophy' AND p2.summary CONTAINS 'atrophy'
      // This is a placeholder for when we extract hard floats later
      // For now, we link by shared 'Extreme Progressor' status in text
    WITH p1, p2
    WHERE p1.summary CONTAINS 'MCI to Dementia' AND p2.summary CONTAINS 'MCI to Dementia'
    MERGE (p1)-[r:SIMILAR_TO {reason: 'MCI_CONVERTER_COHORT'}]->(p2)
    RETURN count(r) as EdgeCount
    """
    
    print("[INFO] Building bridges between MCI-to-AD Converters...")
    result = tx.run(atrophy_query)
    for record in result:
        print(f"[INFO] Created {record['EdgeCount']} SIMILAR_TO edges.")

def main():
    driver = GraphDatabase.driver(NEO4J_URI, auth=AUTH)
    with driver.session() as session:
        session.execute_write(create_p2p_edges)
    driver.close()
    print("[SUCCESS] Patient-to-Patient correspondence is now live.")

if __name__ == "__main__":
    main()
