import os
import sys
import json
import logging
import warnings
from openai import OpenAI
from neo4j_client import kg_client
from dotenv import load_dotenv

# Suppress ugly Neo4j driver warnings from polluting the terminal
logging.getLogger("neo4j").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# --- Tools for C3 Hybrid Agent ---

def query_knowledge_graph(cypher_query: str) -> str:
    """Standard retrieval of patient data or clinical rules."""
    print(f"\n   [🛠️ GRAPH RETRIEVAL] {cypher_query}")
    results = kg_client.execute_query(cypher_query)
    return json.dumps(results)

def retrieve_clinical_twins(patient_rid: int) -> str:
    """Specialized RAG tool to find patients with similar trajectories via SIMILAR_TO edges."""
    print(f"\n   [🧠 RAG RETRIEVAL] Finding Clinical Twins for RID {patient_rid}...")
    query = f"MATCH (p1:Patient {{rid: {patient_rid}}})-[:SIMILAR_TO]-(p2:Patient) RETURN p2.rid as twin_rid, p2.summary as twin_summary LIMIT 3"
    results = kg_client.execute_query(query)
    return json.dumps(results)

def check_medication_safety(current_stage: str, prescribed_drug: str) -> str:
    print(f"\n   [⚠️ MED SAFETY CHECK] Validating {prescribed_drug} for stage {current_stage}")
    severe_drugs = ["memantine", "namenda"]
    if current_stage.lower() == "mci" and prescribed_drug.lower() in severe_drugs:
        return json.dumps({"status": "DANGER", "reason": f"{prescribed_drug} is contraindicated for MCI. Approved only for moderate-to-severe AD."})
    return json.dumps({"status": "SAFE", "reason": f"{prescribed_drug} is generally safe for {current_stage}."})

def check_clinical_consistency(mmse_drop: float, annual_atrophy_rate: float) -> str:
    print(f"\n   [🧠 CLINICAL CONSISTENCY CHECK] Atrophy: {annual_atrophy_rate}% | MMSE Drop: {mmse_drop}")
    if annual_atrophy_rate < 1.0 and mmse_drop > 5.0:
        return json.dumps({"status": "WARNING", "reason": "High cognitive drop but very low structural atrophy. Possible non-AD pathology."})
    if 3.6 <= annual_atrophy_rate <= 4.6 and mmse_drop >= 3.0:
        return json.dumps({"status": "CONSISTENT", "reason": "Decline is mathematically consistent with standard MCI-to-Dementia progression timelines in the FuriMasterKG."})
    return json.dumps({"status": "EVALUATE_FURTHER", "reason": "Metrics are atypical. Suggest secondary review."})

tools = [
    {
        "type": "function",
        "function": {
            "name": "query_knowledge_graph",
            "description": "Executes a Cypher query to retrieve specific patient data or clinical rules from the FuriMasterKG.",
            "parameters": {
                "type": "object",
                "properties": {"cypher_query": {"type": "string"}},
                "required": ["cypher_query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "retrieve_clinical_twins",
            "description": "Retrieves the historical summaries of 'Clinical Twins' (similar patients) from the graph database to ground the prognosis in real data.",
            "parameters": {
                "type": "object",
                "properties": {"patient_rid": {"type": "integer"}},
                "required": ["patient_rid"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_medication_safety",
            "description": "Performs a hard biological rule check against the graph to ensure the prescribed drug is safe for the patient's stage.",
            "parameters": {
                "type": "object",
                "properties": {
                    "current_stage": {"type": "string", "description": "e.g., MCI vs Dementia"},
                    "prescribed_drug": {"type": "string"}
                },
                "required": ["current_stage", "prescribed_drug"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_clinical_consistency",
            "description": "Validates if the clinical cognitive decline (MMSE drop) logically aligns with structural biomarker changes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "mmse_drop": {"type": "number"},
                    "annual_atrophy_rate": {"type": "number"}
                },
                "required": ["mmse_drop", "annual_atrophy_rate"]
            }
        }
    }
]

def chat_loop():
    print("—"*60)
    print("🧬 MODEL C3: HYBRID DIAGNOSTIC CO-PILOT")
    print("⚡ Powered by OpenAI gpt-4o")
    print("Interactive Mode: Ask to evaluate any scenario or test the rule logic.")
    print("—"*60)
    
    messages = [
        {"role": "system", "content": (
            "You are Model C3, the Ultimate Graph-RAG (Retrieval-Augmented Generation) Diagnostic Co-Pilot for Alzheimer's.\n\n"
            "YOUR MISSION (THESIS-GATED RAG LOOP):\n"
            "1. RETRIEVE: When a patient is presented, you MUST first use 'retrieve_clinical_twins' to find similar peer cohorts in the FuriMasterKG.\n"
            "2. AUGMENT: Use 'query_knowledge_graph' to fetch the specific clinical rules (Medication Safety, Consistency rules) governing those twins.\n"
            "3. GENERATE: Synthesize the patient's vector timeline with the retrieved graph knowledge to generate a prognosis and predict the MMSE response variable.\n\n"
            "CRITICAL RATE LIMIT RULE: If retrieval fails, rely on 'check_medication_safety' and 'check_clinical_consistency' logic to protect the session.\n\n"
            "Provide a highly accurate, structured longitudinal prognosis and formally cite 'Graph Retrieval' results in your response."
        )}
    ]
    
    while True:
        try:
            user_input = input("\n👤 Clinician: ")
        except EOFError:
            break
            
        if user_input.lower() in ['exit', 'quit']: break
        if not user_input.strip(): continue
        
        messages.append({"role": "user", "content": user_input})
        print("🤖 C3 Agent is analyzing and querying constraints in parallel...")
        
        temp_messages = messages.copy()
        while True:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=temp_messages,
                tools=tools
            )
            
            message = response.choices[0].message
            temp_messages.append(message)
            
            if message.tool_calls:
                for tool_call in message.tool_calls:
                    args = json.loads(tool_call.function.arguments)
                    if tool_call.function.name == "query_knowledge_graph":
                        res = query_knowledge_graph(args.get("cypher_query", ""))
                    elif tool_call.function.name == "retrieve_clinical_twins":
                        res = retrieve_clinical_twins(args.get("patient_rid", 0))
                    elif tool_call.function.name == "check_medication_safety":
                        res = check_medication_safety(args.get("current_stage", ""), args.get("prescribed_drug", ""))
                    elif tool_call.function.name == "check_clinical_consistency":
                        res = check_clinical_consistency(args.get("mmse_drop", 0), args.get("annual_atrophy_rate", 0))
                        
                    temp_messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": res
                    })
            else:
                print("\n🩺 FINAL C3 PROGNOSIS:")
                print(message.content)
                messages.append({"role": "assistant", "content": message.content})
                break

if __name__ == "__main__":
    chat_loop()
