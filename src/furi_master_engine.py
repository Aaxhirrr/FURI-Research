import os
import google.generativeai as genai
from neo4j import GraphDatabase
import json
import sys

# 1. AUTHENTICATION & SETUP
# Replace with your actual credentials from credentials-a1e8aa49.txt
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
# Use gemini-2.5-flash due to free tier quotas on pro
model = genai.GenerativeModel('gemini-2.5-flash')

NEO4J_URI = "neo4j+s://a1e8aa49.databases.neo4j.io"
NEO4J_USER = "a1e8aa49"
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")

# Connect to the cloud instance once
try:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    driver.verify_connectivity()
except Exception as e:
    print(f"❌ Connection Error: {e}")
    sys.exit()

def multiclin_processor(user_input):
    """
    Handles MultiClinNER and Annotation Projection for the ACL 2026 Challenge.
    Extracts clinical entities and maps them to English KG nodes.
    """
    prompt = f"""You are a MultiClinAI Entity Architect (ACL 2026).
    Analyze this input: "{user_input}"
    1. Detect Language (ES, EN, IT, NL, RO, SV, CS).
    2. Extract Clinical Entities (Diseases, Symptoms, Procedures).
    3. Project to the standardized English medical term for our Neo4j Graph.
    Return ONLY JSON exactly like this:
    {{
      "lang": "Language Detected",
      "entities": [
        {{"original": "...", "projected": "...", "type": "..."}}
      ]
    }}"""
    
    response = model.generate_content(prompt)
    try:
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except Exception as e:
        print(f"JSON Parsing Error: {e}")
        return {"lang": "unknown", "entities": []}

def push_and_query_graph(lang, entities):
    """
    Injects new multilingual nodes into the cloud and queries existing cohort risks.
    """
    # Note: In our active predictive graph, nodes are labeled `Node` and relationships `RELATIONSHIP`
    with driver.session() as session:
        for ent in entities:
            # THE PUSH: Visualizes the multilingual link in real-time
            session.run("""
                MERGE (l:Language {name: $lang})
                MERGE (e:Node {name: $projected})
                MERGE (l)-[r:MAPPED_TO {original_term: $original}]->(e)
            """, lang=lang, projected=ent['projected'], original=ent['original'])
            
            print(f"🔗 [MAPPING]: '{ent['original']}' ({lang}) -> '{ent['projected']}' (English Node)")
            
            # THE QUERY: Pulls the 47.7% / 25% risk paths from your logic
            result = session.run("""
                MATCH (n:Node)-[r:RELATIONSHIP]->(target)
                WHERE toLower(n.name) CONTAINS toLower($name)
                RETURN n.name, type(r), target.name LIMIT 2
            """, name=ent['projected'])
            
            for record in result:
                print(f"   🧬 [GRAPH EVIDENCE]: {record[0]} --[{record[1]}]--> {record[2]}")

def main():
    print("—"*60)
    print("🧠 FURI: MULTILINGUAL PREDICTIVE ENGINE (ACL 2026 CHALLENGE)")
    print("Supports: English, Spanish, Italian, Dutch, Romanian, Swedish, Czech")
    print("—"*60)

    while True:
        try:
            user_input = input("\n👤 Patient/Clinician: ")
        except EOFError:
            break
            
        if user_input.lower() in ['exit', 'quit']: break

        try:
            # 1. Analyze (NER & Projection)
            print("\n🌐 Analyzing input...")
            data = multiclin_processor(user_input)
            
            # 2. Visualize (Push to Cloud & Query Logic)
            if data['entities']:
                push_and_query_graph(data['lang'], data['entities'])
            else:
                print("❌ No clinical entities extracted.")
                continue
            
            # 3. Assess (Clinical Reasoning grounded in your FURI Study)
            projected_names = [e['projected'] for e in data['entities']]
            assessment_prompt = f"""Using clinical nodes {projected_names}, provide a concise risk 
            assessment citing our 109-patient study results. Cite the 47.7% MCI-to-Dementia 
            and 25% NL-to-MCI transition rates discovered in our cohort. Reply in {data['lang']}."""
            
            print(f"\n🩺 [DR. AI ASSESSMENT ({data['lang'].upper()})]:")
            print(model.generate_content(assessment_prompt).text)
            print("\n🚀 Cloud Updated. Refresh Neo4j Browser to see the new nodes.")

        except Exception as e:
            print(f"❌ Process Error: {e}")

if __name__ == "__main__":
    main()
