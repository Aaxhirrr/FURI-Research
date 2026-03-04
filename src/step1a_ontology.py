from neo4j import GraphDatabase

# Using the AuraDB credentials from previous scripts
NEO4J_URI = "neo4j+s://a1e8aa49.databases.neo4j.io"
NEO4J_USER = "a1e8aa49"
NEO4J_PASSWORD = "O6Km241NG57sX1iUnIkduX1WwL9mu9wd7YUWQf9F3pU"

ontology_query = """
// 1. CREATE THE COHORT NODE
MERGE (c:Cohort {name: "ADNI_1730_Master"})
SET c.total_n = 1730,
    c.avg_follow_up = 4.1,
    c.source = "ADNI Longitudinal Data",
    c.integrity = "100%"

// 2. CREATE CLINICAL STATES
MERGE (mci:ClinicalState {name: "MCI"}) SET mci.description = "Mild Cognitive Impairment"
MERGE (ad:ClinicalState {name: "AD"}) SET ad.description = "Alzheimer's Dementia"

// 3. MAP THE GLOBAL PROGRESSION RATE
MERGE (mci)-[r1:CONVERTS_TO]->(ad)
SET r1.rate = 0.46, 
    r1.confidence = "High", 
    r1.avg_years = 2.9,
    r1.metric = "Conversion to AD"

// 4. MAP THE BIOMARKER CORRELATION (THE PEARSON R)
MERGE (atrophy:Biomarker {name: "Hippocampal Atrophy"})
SET atrophy.annual_rate_percent = 3.9

MERGE (mmse:CognitiveTest {name: "MMSE"})
SET mmse.annual_decline_points = 2.5

MERGE (atrophy)-[r2:CORRELATES_WITH]->(mmse)
SET r2.r_value = 0.73,
    r2.significance = "p < 0.001",
    r2.type = "Positive Linear"

// 5. CONNECT TO COHORT
MERGE (c)-[:MONITORS]->(mci)
MERGE (c)-[:MONITORS]->(ad)
MERGE (c)-[:VALIDATES]->(atrophy)
MERGE (c)-[:VALIDATES]->(mmse)
"""

def establish_ontology():
    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        driver.verify_connectivity()
        print("✅ Connected to AuraDB")
        
        with driver.session() as session:
            session.run(ontology_query)
            print("🧠 Step 1a Successfully executed: Master Ontology Foundation built!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    establish_ontology()
