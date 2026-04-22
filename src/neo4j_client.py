import os
import logging
import warnings
from dotenv import load_dotenv
from neo4j import GraphDatabase

# Suppress noisy DBMS Neo4j warnings from polluting the stdout
logging.getLogger("neo4j").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

load_dotenv()

class Neo4jClient:
    def __init__(self):
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")
        if not uri or not user or not password:
            raise ValueError("Neo4j credentials are not correctly set in the .env file.")
        
        # Connect to AuraDB
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        if self.driver:
            self.driver.close()

    def execute_query(self, cypher_query: str, parameters: dict = None):
        """
        Executes a Cypher query against the FuriMasterKG and returns results as JSON-serializable dicts.
        """
        if parameters is None:
            parameters = {}
            
        try:
            with self.driver.session() as session:
                result = session.run(cypher_query, parameters)
                # .data() converts the Neo4j Record object into a standard Python dictionary
                return [record.data() for record in result]
        except Exception as e:
            return {"error": str(e), "query": cypher_query}

# Initialize a singleton client for the agent to import and use
kg_client = Neo4jClient()

if __name__ == "__main__":
    print("Testing connection to FuriMasterKG AuraDB...")
    try:
        # Simple test query to count nodes
        res = kg_client.execute_query("MATCH (n) RETURN count(n) AS total_nodes")
        if isinstance(res, dict) and "error" in res:
            print(f"FAILED to query Neo4j: {res['error']}")
        else:
            print(f"SUCCESS! Connected to Neo4j. Total nodes in graph: {res[0]['total_nodes']}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        kg_client.close()

