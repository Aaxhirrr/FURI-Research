import google.generativeai as genai
from neo4j import GraphDatabase
import json

# 1. Setup - Using your Gemini and Aura Credentials
genai.configure(api_key="AIzaSyBM8mdPI6gOpKO520zJjOKGJP5FZlN_lgY")
model = genai.GenerativeModel('gemini-2.5-flash')

NEO4J_URI = "neo4j+s://a1e8aa49.databases.neo4j.io"
NEO4J_USER = "a1e8aa49"
NEO4J_PASSWORD = "O6Km241NG57sX1iUnIkduX1WwL9mu9wd7YUWQf9F3pU"

def multiclin_ner_projection(user_input):
    """
    MultiClinNER: Extracts clinical entities and projects them to the 
    standardized English Knowledge Graph nodes.
    Supports: ES, EN, IT, NL, RO, SV, CS.
    """
    prompt = f"""You are a MultiClinAI Entity Extractor (ACL 2026).
    INPUT: "{user_input}"
    
    1. Detect Language.
    2. Extract Clinical Entities (Diseases, Symptoms, Procedures).
    3. Project them to the English medical equivalents used in our Knowledge Graph.
    
    Return ONLY a JSON list of objects: 
    [{{ "original": "...", "projected_node": "...", "type": "..." }}]"""

    response = model.generate_content(prompt)
    try:
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except:
        return []

def query_graph_evidence(node_name):
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with driver.session() as session:
        # Searching your relationships for predictive paths
        result = session.run("""
            MATCH (n:Node)-[r:RELATIONSHIP]->(target)
            WHERE toLower(n.name) CONTAINS toLower($name)
            RETURN n.name, type(r), target.name
            LIMIT 2
        """, name=node_name)
        return [f"✅ {record[0]} --[{record[1]}]--> {record[2]}" for record in result]

def main():
    print("—"*60)
    print("🌍 MULTICLINAI PREDICTIVE ENGINE (ACL 2026 CHALLENGE)")
    print("Supports: Spanish, English, Italian, Dutch, Romanian, Swedish, Czech")
    print("—"*60)
    
    while True:
        try:
            user_query = input("\n👤 Patient Input: ")
        except EOFError:
            break
            
        if user_query.lower() in ['exit', 'quit']: break

        # Step 1: Multi-language extraction and projection
        print("🧠 Extracting and Projecting entities to English Knowledge Graph...")
        entities = multiclin_ner_projection(user_query)
        
        if not entities:
            print("❌ No clinical entities detected.")
            continue

        # Step 2: Show the mapping live in the CLI
        projected_list = []
        for ent in entities:
            print(f"🔗 {ent['original']} ({ent['type']}) -> Projected to: '{ent['projected_node']}'")
            projected_list.append(ent['projected_node'])
            # Pull live evidence from Neo4j
            evidence = query_graph_evidence(ent['projected_node'])
            for line in evidence: print(f"   {line}")

        # Step 3: Assessment grounded in the 47.7% and 25% transition rates
        assessment_prompt = f"""Using these projected clinical nodes: {projected_list}, 
        provide a risk assessment based on our 109-patient study results. 
        Cite the 47.7% MCI-to-Dementia and 25% NL-to-MCI transition rates."""
        
        print("\n🏥 CLINICAL ASSESSMENT:")
        try:
            print(model.generate_content(assessment_prompt).text)
        except Exception as e:
            print(f"❌ Could not generate risk assessment: {e}")

if __name__ == "__main__":
    main()
