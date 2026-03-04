import json
import os
import google.generativeai as genai
from neo4j import GraphDatabase

# 1. Setup Gemini (We use 2.5 flash because of token limits on 1.5-pro free tier)
genai.configure(api_key="AIzaSyBM8mdPI6gOpKO520zJjOKGJP5FZlN_lgY")
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. Neo4j Connection
# (These are the actual credentials we discovered for your aura instance)
NEO4J_URI = "neo4j+s://a1e8aa49.databases.neo4j.io"
NEO4J_USER = "a1e8aa49"
NEO4J_PASSWORD = "O6Km241NG57sX1iUnIkduX1WwL9mu9wd7YUWQf9F3pU"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def extract_predictive_logic(summary_text):
    prompt = f"""You are an AI Diagnostic Engineer specializing in Alzheimer's prediction. 
Analyze this clinical summary and extract a Knowledge Graph optimized for PREDICTIVE MODELING:

{summary_text}

Extract the following structure in JSON:
{{
  "nodes": [
    {{"Name": "Hippocampus_Atrophy", "Label": "Biomarker"}},
    {{"Name": "APOE4_Positive", "Label": "RiskFactor"}},
    {{"Name": "Conversion_to_Dementia", "Label": "Outcome"}}
  ],
  "relationships": [
    {{"Source": "APOE4_Positive", "Target": "Conversion_to_Dementia", "Type": "PREDICTS"}}
  ]
}}

1. Nodes: 
   - 'Label' should be 'Biomarker' (e.g., Hippocampus, ADAS13), 'RiskFactor' (e.g., APOE4_Positive), or 'Outcome' (e.g., Rapid_Decline, Conversion_to_Dementia)
   - 'Name' should be a concise, snake_case or CamelCase string name for the node. 
2. Relationships: 
   - 'Type' can be 'PREDICTS', 'CORRELATES_WITH', 'INDICATES_STAGE'.
   - 'Source' and 'Target' should match the 'Name' provided for the nodes.

Focus on the IF/THEN logic. (e.g., IF Hippocampus < X AND APOE4 is 1, THEN high probability of Outcome Y).
Return ONLY JSON with 'nodes' and 'relationships' keys. Make sure it is valid JSON."""

    print("🧠 Extracting Predictive Logic for the Graph...")
    response = model.generate_content(prompt)
    clean_json = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(clean_json)

def build_predictive_graph(graph_data):
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        print("Clearing the old graph...")
        session.run("MATCH (n) DETACH DELETE n") # Fresh start

        print(f"Creating {len(graph_data['nodes'])} Nodes...")
        # Create Nodes with Properties
        for node in graph_data['nodes']:
            session.run(
                "CREATE (n:Node {name: $name, label: $label})",
                name=node['Name'], label=node['Label']
            )

        print(f"Creating {len(graph_data['relationships'])} Relationships...")
        # Create Predictive Relationships
        for rel in graph_data['relationships']:
            # We match on the newly created nodes based on the name property
            session.run("""
                MATCH (a:Node {name: $source}), (b:Node {name: $target})
                CREATE (a)-[r:RELATIONSHIP {type: $type}]->(b)
                """, source=rel['Source'], target=rel['Target'], type=rel['Type'])
    driver.close()

if __name__ == "__main__":
    input_path = os.path.join(SCRIPT_DIR, '../data/processed/PROFESSOR_MASTER_SUMMARY.txt')
    with open(input_path, 'r', encoding='utf-8') as f:
        summary = f.read()
    
    predictive_data = extract_predictive_logic(summary)
    
    # Save the JSON representation just in case
    output_json = os.path.join(SCRIPT_DIR, '../data/processed/predictive_graph.json')
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(predictive_data, f, indent=4)
        
    print(f"Saved extracted graph data to {output_json}")
    
    # Build it in Neo4j
    build_predictive_graph(predictive_data)
    print("\n✅ Predictive Knowledge Graph is LIVE.")
