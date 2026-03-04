import os
from neo4j import GraphDatabase

URI = "neo4j+s://a1e8aa49.databases.neo4j.io" 
AUTH = ("neo4j", "O6Km241NG57sX1iUnIkduX1WwL9mu9wd7YUWQf9F3pU")
# But wait, lines 3 and 4 in the file say:
# NEO4J_USERNAME=a1e8aa49
# NEO4J_PASSWORD=...
# So let's try that.
AUTH_ALT = ("a1e8aa49", "O6Km241NG57sX1iUnIkduX1WwL9mu9wd7YUWQf9F3pU")

def test_conn():
    try:
        print(f"Connecting to {URI} with user a1e8aa49...")
        driver = GraphDatabase.driver(URI, auth=AUTH_ALT)
        driver.verify_connectivity()
        print("Connected with a1e8aa49!")
        driver.close()
        return
    except Exception as e:
        print(f"Connection failed with a1e8aa49: {e}")

    try:
        print(f"Connecting to {URI} with user neo4j...")
        driver = GraphDatabase.driver(URI, auth=AUTH)
        driver.verify_connectivity()
        print("Connected with neo4j!")
        driver.close()
    except Exception as e:
        print(f"Connection failed with neo4j: {e}")


if __name__ == "__main__":
    test_conn()
