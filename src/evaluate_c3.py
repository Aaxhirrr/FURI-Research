import json
import os
import sys
from openai import OpenAI
from dotenv import load_dotenv

# Import the C3 Hybrid tools
from model_c3_hybrid import tools, query_knowledge_graph, retrieve_clinical_twins, check_medication_safety, check_clinical_consistency

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Setup paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(SCRIPT_DIR, '../data/processed/CLEAN_1730_TIMELINES.json')

def get_patient_history(rid, data):
    for patient in data:
        if patient and patient.get('RID') == rid:
            return patient.get('Timeline_Summary', '')
    return None

def run_c3_validation(rid, past_history):
    print("\n" + "🔵"*20)
    print(" C3 MODEL: GRAPH-RAG VALIDATION")
    print("🔵"*20)
    
    prompt = f"Patient RID {rid}. History: {past_history}. Evaluate trajectory, check clinical twins, and verify med safety (Memantine)."
    
    messages = [
        {"role": "system", "content": (
            "You are Model C3, the Ultimate Graph-RAG Diagnostic Co-Pilot.\n"
            "MANDATORY RAG STEP: Use 'retrieve_clinical_twins' first to find historical peers."
        )},
        {"role": "user", "content": prompt}
    ]
    
    print(f"🤖 Evaluating Patient {rid} using Graph-RAG pipeline...")
    
    try:
        while True:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                tools=tools
            )
            
            message = response.choices[0].message
            messages.append(message)
            
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
                        
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": res
                    })
            else:
                print(f"\n>> C3 FINAL ASSESSMENT:\n{message.content}\n")
                break
    except Exception as e:
        print(f"❌ Error during AI execution: {e}")

if __name__ == "__main__":
    TARGET_RID = 6
    
    print(f"🧬 Loading FURI dataset to validate Graph-RAG Architecture...")
    try:
        if not os.path.exists(input_file):
             # Fallback if the specific clean file isn't there
             input_file = os.path.join(SCRIPT_DIR, '../data/processed/patient_timelines.json')

        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        history = get_patient_history(TARGET_RID, data)
        if history:
            print(f"✅ Loaded timeline for Patient {TARGET_RID}!")
            run_c3_validation(TARGET_RID, history)
        else:
            print(f"❌ Failed to find RID {TARGET_RID} in the dataset.")
    except Exception as e:
        print(f"❌ Execution error: {e}")
