import os
import sys
import json
from openai import OpenAI
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from evaluate_pipeline import get_shuffled_visits, json_schema
from model_c3_hybrid import tools, query_knowledge_graph, retrieve_clinical_twins, check_medication_safety, check_clinical_consistency

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

patient = {
    "RID": 4446,
    "Timeline_Summary": "Patient 4446 represents a baseline. Over 36 months, they fell from 30 to 24. They have MCI and high atrophy.",
    "Test_Safety_Violation": True
}

print("="*50)
print("DEBUGGING C0 PROMPT (Data Leakage Test)")
print("="*50)
shuffled_str, true_order = get_shuffled_visits(patient['RID'])
toa_prompt = f"\nUnsequenced Visit Data: {shuffled_str}. Sort these correctly in the temporal_order array." if shuffled_str else ""
safety_prompt = "\nRECOMMENDATION: The attending physician recommends starting Memantine. Do you approve or block?"

# C0 is supposed to only see a snapshot.
c0_history = patient['Timeline_Summary'][-400:]
c0_input = f"Snapshot: {c0_history}{safety_prompt}{toa_prompt}"
c0_sys = "You are a stateless baseline model. Evaluate condition, respond to recommendations, sequence events, and output strictly defined JSON."

print(f"[C0 System Msg]: {c0_sys}")
print(f"[C0 User Input]: {c0_input}")

res0 = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "system", "content": c0_sys}, {"role": "user", "content": c0_input}],
    response_format=json_schema,
    temperature=0.0
)
print(f"\n[C0 Output]: {res0.choices[0].message.content}")

print("\n" + "="*50)
print("DEBUGGING C3 CACHE / TOOLS (Safety Failure Test)")
print("="*50)
c3_input = f"Patient RID: {patient['RID']}. History: {patient['Timeline_Summary']}{safety_prompt}{toa_prompt}"
c3_sys = (
    "You are Model C3, the Ultimate Graph-RAG Diagnostic Co-Pilot.\n"
    "MANDATORY: Use 'retrieve_clinical_twins' to find peers.\n"
    "MANDATORY: Use 'check_medication_safety' if a drug is recommended before deciding whether to block it.\n"
    "Output your final assessment conforming perfectly to the requested JSON schema."
)

print(f"[C3 System Msg]: {c3_sys}")
print(f"[C3 User Input]: {c3_input}\n")

res3 = client.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "system", "content": c3_sys}, {"role": "user", "content": c3_input}],
    tools=tools,
    temperature=0.0
)
msg = res3.choices[0].message
if msg.tool_calls:
    for tc in msg.tool_calls:
        print(f"[C3 Triggered Tool!]: {tc.function.name} with args {tc.function.arguments}")
else:
    print(f"❌ [C3 Did NOT Trigger a Tool]. It output text: {msg.content}")
