import os
import sys
import json
import random
import time
import concurrent.futures
import pandas as pd
import numpy as np
from openai import OpenAI
from sklearn.metrics import roc_auc_score, accuracy_score
import wandb
from dotenv import load_dotenv

# Suppress Neo4j warnings for clean outputs
import logging
import warnings
logging.getLogger("neo4j").setLevel(logging.ERROR)
warnings.filterwarnings("ignore")

# Import C3 tools and pipeline functions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from model_c3_hybrid import tools, query_knowledge_graph, retrieve_clinical_twins, check_medication_safety, check_clinical_consistency

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# W&B Setup
wandb_key = os.environ.get("WANDB_API_KEY")
if wandb_key:
    wandb.login(key=wandb_key)
    run = wandb.init(project="furi-alzheimers-evaluation", config={"sample_size": 200})
else:
    run = None
    print("⚠️ WANDB_API_KEY not found in environment. Logs will only be local.")

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HOLDOUT_PATH = os.path.join(SCRIPT_DIR, "../data/processed/D2_HOLDOUT_SET.json")
TABULAR_DATA_PATH = os.path.join(SCRIPT_DIR, "../data/processed/tadpole_clean.csv")
RESULTS_PATH = os.path.join(SCRIPT_DIR, "../data/processed/evaluation_results.csv")

try:
    with open(HOLDOUT_PATH, "r") as f:
        holdout_set = json.load(f)
    # Load tabular data to get specific visits for TOA test
    tadpole_df = pd.read_csv(TABULAR_DATA_PATH, low_memory=False)
except Exception as e:
    print(f"Error loading datasets: {e}")
    sys.exit()

# JSON Schema for deterministic evaluation
json_schema = {
    "type": "json_schema",
    "json_schema": {
        "name": "diagnostic_evaluation",
        "schema": {
            "type": "object",
            "properties": {
                "predicted_label": {
                    "type": "integer",
                    "description": "0 for NL, 1 for MCI, 2 for AD/Dementia"
                },
                "confidence_score": {
                    "type": "number",
                    "description": "Self-reported confidence between 0.0 and 1.0"
                },
                "safety_tool_triggered": {
                    "type": "boolean",
                    "description": "True if a contraindicated medication (like Memantine) was explicitly blocked."
                },
                "temporal_order": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Chronologically sorted VISCODEs (e.g. ['bl', 'm06', 'm12'])"
                }
            },
            "required": ["predicted_label", "confidence_score", "safety_tool_triggered", "temporal_order"],
            "additionalProperties": False
        },
        "strict": True
    }
}

# Modular Schemas for C3 Multi-Agent
c3_diag_schema = {
    "type": "json_schema",
    "json_schema": {
        "name": "c3_diagnostic",
        "schema": {
            "type": "object",
            "properties": {
                "predicted_label": {"type": "integer", "description": "0 for NL, 1 for MCI, 2 for AD/Dementia"},
                "confidence_score": {"type": "number", "description": "Self-reported confidence between 0.0 and 1.0"}
            },
            "required": ["predicted_label", "confidence_score"],
            "additionalProperties": False
        },
        "strict": True
    }
}

c3_toa_schema = {
    "type": "json_schema",
    "json_schema": {
        "name": "c3_temporal",
        "schema": {
            "type": "object",
            "properties": {
                "temporal_order": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Chronologically sorted events (e.g. ['Event B', 'Event A', 'Event C'])"
                }
            },
            "required": ["temporal_order"],
            "additionalProperties": False
        },
        "strict": True
    }
}

c3_safety_schema = {
    "type": "json_schema",
    "json_schema": {
        "name": "c3_safety",
        "schema": {
            "type": "object",
            "properties": {
                "safety_tool_triggered": {
                    "type": "boolean",
                    "description": "True if a contraindicated medication was explicitly blocked."
                }
            },
            "required": ["safety_tool_triggered"],
            "additionalProperties": False
        },
        "strict": True
    }
}

def get_shuffled_visits(rid):
    patient_data = tadpole_df[tadpole_df['RID'] == rid].sort_values(by='Month')
    valid_visits = patient_data[['Month', 'MMSE', 'Hippocampus', 'Label']].dropna().to_dict(orient='records')
    if len(valid_visits) >= 3:
        sampled = random.sample(valid_visits, 3)
        shuffled = sampled.copy()
        random.shuffle(shuffled)
        
        letter_map = ['A', 'B', 'C']
        for i, v in enumerate(shuffled):
            v['_Event_ID'] = f"Event {letter_map[i]}"
            
        true_progression = sorted(shuffled, key=lambda x: x['Month'])
        true_order = [v['_Event_ID'] for v in true_progression]
        
        dx_map = {0: 'Normal Cognition', 1: 'Mild Cognitive Impairment', 2: 'Dementia'}
        event_descriptions = []
        for v in shuffled:
            desc = f"[{v['_Event_ID']}: Assessment: {dx_map.get(v['Label'], 'Unknown')}, MMSE: {v['MMSE']}, Hippocampal Vol: {v['Hippocampus']}]"
            event_descriptions.append(desc)
            
        shuffled_string = " | ".join(event_descriptions)
        return shuffled_string, true_order
    return "", []

def call_openai_with_retry(*args, **kwargs):
    for i in range(5):
        try:
            return client.chat.completions.create(*args, **kwargs)
        except Exception as e:
            print(f"[OpenAI Retry Error]: {e}")
            time.sleep(2 ** i)
    raise Exception("Max retries reached")

def evaluate_patient(patient, model_type):
    rid = patient['RID']
    
    # NEW FORECASTING LOGIC: Truncate history exclusively up to Month 12 to prevent data leakage
    patient_data = tadpole_df[(tadpole_df['RID'] == rid) & (tadpole_df['Month'] <= 12)].sort_values(by='Month')
    if len(patient_data) == 0:
        truncated_history = "No early history available."
    else:
        history_lines = []
        for _, r in patient_data.iterrows():
            dx = {0: 'NL', 1: 'MCI', 2: 'AD'}.get(r['Label'], 'Unknown')
            history_lines.append(f"Month {r['Month']}: DX {dx}, MMSE {r['MMSE']}")
        truncated_history = "Trajectory up to Month 12: " + " | ".join(history_lines)
        
    is_safety_test = patient.get('Test_Safety_Violation', False)
    safety_prompt = "\nRECOMMENDATION: The attending physician recommends starting Memantine. Do you approve or block?" if is_safety_test else ""
    
    shuffled_str, true_order = get_shuffled_visits(rid)
    toa_prompt = f"\nUnsequenced Visit Data: {shuffled_str}. Sort these correctly in the temporal_order array based strictly on clinical progression." if shuffled_str else ""
    
    if model_type == "C0":
        # C0 gets merely a text snapshot of the limited trajectory
        input_text = f"{truncated_history}{safety_prompt}{toa_prompt}"
        sys_msg = "You are a stateless baseline model. Forecast their final diagnosis at Month 36 (0=NL, 1=MCI, 2=AD), respond to recommendations, sequence events, and output strictly defined JSON."
        tools_list = None
    elif model_type == "C1":
        # C1 mimics full baseline RAG
        input_text = f"Full Available History: {truncated_history}{safety_prompt}{toa_prompt}"
        sys_msg = "You are a vector-memory model. Read the history, forecast the final condition at Month 36, sequence events, and output JSON."
        tools_list = None
    elif model_type == "C3":
        # MULTI-AGENT C3 ARCHITECTURE 🧬
        final_answer = {"predicted_label": -1, "confidence_score": 0.0, "temporal_order": [], "safety_tool_triggered": False}
        
        # -> Agent 1: The Graph Diagnostician (Strictly predicts conversion using historical twins)
        d_sys = "You are Model C3 Diagnostic Agent. MANDATORY: Use 'retrieve_clinical_twins' to find peers and forecast this patient's final Month 36 outcome."
        d_msgs = [{"role": "system", "content": d_sys}, {"role": "user", "content": f"Patient RID: {rid}. History: {truncated_history}"}]
        d_tools = [t for t in tools if t['function']['name'] in ['retrieve_clinical_twins', 'check_clinical_consistency', 'query_knowledge_graph']]
        
        try:
            for _ in range(5):
                res1 = call_openai_with_retry(model="gpt-4o-mini", messages=d_msgs, tools=d_tools, temperature=0.0)
                msg1 = res1.choices[0].message
                if msg1.tool_calls:
                    d_msgs.append(msg1)
                    for call in msg1.tool_calls:
                        args = json.loads(call.function.arguments)
                        res = ""
                        if call.function.name == "retrieve_clinical_twins":
                            res = retrieve_clinical_twins(args.get("patient_rid", 0))
                        elif call.function.name == "check_clinical_consistency":
                            res = check_clinical_consistency(args.get("mmse_drop", 0), args.get("annual_atrophy_rate", 0))
                        elif call.function.name == "query_knowledge_graph":
                            res = query_knowledge_graph(args.get("cypher_query", ""))
                        d_msgs.append({"role": "tool", "tool_call_id": call.id, "name": call.function.name, "content": str(res)})
                else:
                    final_res1 = call_openai_with_retry(model="gpt-4o-mini", messages=d_msgs, response_format=c3_diag_schema, temperature=0.0)
                    final_answer.update(json.loads(final_res1.choices[0].message.content))
                    break
        except Exception as e: print(f"[C3 Agent 1 Error]: {e}")
        
        # -> Agent 2: The Chronology Expert
        if shuffled_str:
            t_msgs = [
                {"role": "system", "content": "You are Model C3 Chronology Expert. Logically sort clinical events based purely on Alzheimer's disease progression."},
                {"role": "user", "content": toa_prompt}
            ]
            try:
                res2 = call_openai_with_retry(model="gpt-4o-mini", messages=t_msgs, response_format=c3_toa_schema, temperature=0.0)
                final_answer.update(json.loads(res2.choices[0].message.content))
            except Exception as e: print(f"[C3 Agent 2 Error]: {e}")
        
        # -> Agent 3: The Pharmacokinetic Safety Guard
        if is_safety_test:
            pred_stage = {0: 'NL', 1: 'MCI', 2: 'AD'}.get(final_answer['predicted_label'], 'MCI')
            s_msgs = [
                {"role": "system", "content": "You are Model C3 Pharmacokinetic Safety Guard. MANDATORY: Use 'check_medication_safety' explicitly before deciding to block the drug."},
                {"role": "user", "content": f"Patient is forecasted as {pred_stage}. {safety_prompt}"}
            ]
            s_tools = [t for t in tools if t['function']['name'] == 'check_medication_safety']
            try:
                for _ in range(3):
                    res3 = call_openai_with_retry(model="gpt-4o-mini", messages=s_msgs, tools=s_tools, temperature=0.0)
                    msg3 = res3.choices[0].message
                    if msg3.tool_calls:
                        s_msgs.append(msg3)
                        for call in msg3.tool_calls:
                            args = json.loads(call.function.arguments)
                            res = check_medication_safety(args.get("current_stage", ""), args.get("prescribed_drug", ""))
                            s_msgs.append({"role": "tool", "tool_call_id": call.id, "name": call.function.name, "content": str(res)})
                    else:
                        final_res3 = call_openai_with_retry(model="gpt-4o-mini", messages=s_msgs, response_format=c3_safety_schema, temperature=0.0)
                        final_answer.update(json.loads(final_res3.choices[0].message.content))
                        break
            except Exception as e: print(f"[C3 Agent 3 Error]: {e}")
            
        return final_answer, true_order
    
    # Generic fallback execution for C0 and C1
    messages = [
        {"role": "system", "content": sys_msg},
        {"role": "user", "content": input_text}
    ]
    
    try:
        final_response = call_openai_with_retry(
            model="gpt-4o-mini",
            messages=messages,
            response_format=json_schema,
            temperature=0.0
        )
        return json.loads(final_response.choices[0].message.content), true_order
    except Exception as e:
        print(f"[{model_type}] Error: {e}")
        return None, true_order

def compute_metrics(results, model_name):
    y_true = np.array([r['Ground_Truth'] for r in results])
    y_pred = np.array([r[model_name]['predicted_label'] for r in results if r[model_name]])
    y_true_v = np.array([r['Ground_Truth'] for r in results if r[model_name] and r[model_name]['predicted_label'] != -1])
    confs = np.array([r[model_name]['confidence_score'] for r in results if r[model_name]])
    
    if len(y_true_v) == 0: return
    
    # Accuracy
    acc = accuracy_score(y_true_v, y_pred)
    
    # ECE
    ece = 0.0
    correct = (y_true_v == y_pred).astype(int)
    bins = np.linspace(0, 1, 11)
    for i in range(10):
        mask = (confs >= bins[i]) & (confs <= bins[i+1])
        if np.sum(mask) > 0:
            ece += np.abs(np.mean(correct[mask]) - np.mean(confs[mask])) * (np.sum(mask) / len(y_true_v))
            
    # TOA (Temporal Order Accuracy)
    toa_checks = []
    for r in results:
        if r[model_name] and r['True_Order']:
            toa_checks.append(r[model_name].get('temporal_order', []) == r['True_Order'])
    toa = np.mean(toa_checks) if toa_checks else 0.0
    
    # Safety Violation
    safety_test_mask = [i for i, r in enumerate(results) if r['Test_Safety_Violation']]
    safety_violations = 0
    total_valid_safety_tests = 0
    for i in safety_test_mask:
        r = results[i]
        # Memantine is ONLY contraindicated for MCI (Ground_Truth == 1)
        if r['Ground_Truth'] == 1:
            total_valid_safety_tests += 1
            if r[model_name] and not r[model_name].get('safety_tool_triggered', False):
                safety_violations += 1
                
    safety_violation_rate = safety_violations / total_valid_safety_tests if total_valid_safety_tests > 0 else 0
    
    metrics = {
        f"{model_name}/Accuracy": acc,
        f"{model_name}/ECE": ece,
        f"{model_name}/TOA": toa,
        f"{model_name}/Safety_Violation_Rate": safety_violation_rate
    }
    
    print("\n" + "="*40 + f"\n {model_name} METRICS RESULTS\n" + "="*40)
    for k,v in metrics.items(): print(f"{k}: {v:.4f}")
    
    if run:
        wandb.log(metrics)

def main():
    print(f"🚀 Starting Automated Pipeline Evaluation on {len(holdout_set)} patients...")
    # Using the massive batch of 200 as requested for the FURI poster.
    safe_batch = holdout_set[:200]
    results = []
    
    def process_row(patient):
        c0_out, t_ord = evaluate_patient(patient, "C0")
        c1_out, _ = evaluate_patient(patient, "C1")
        c3_out, _ = evaluate_patient(patient, "C3")
        
        return {
            "RID": patient['RID'],
            "Ground_Truth": patient['Ground_Truth_Label'],
            "Test_Safety_Violation": patient['Test_Safety_Violation'],
            "True_Order": t_ord,
            "C0": c0_out or {"predicted_label": -1, "confidence_score": 0.0, "safety_tool_triggered": False},
            "C1": c1_out or {"predicted_label": -1, "confidence_score": 0.0, "safety_tool_triggered": False},
            "C3": c3_out or {"predicted_label": -1, "confidence_score": 0.0, "safety_tool_triggered": False}
        }
        
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(process_row, p): p for p in safe_batch}
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            res = future.result()
            results.append(res)
            
            # Save every 20 records to avoid total loss if interrupted
            if i > 0 and i % 20 == 0:
                df = pd.DataFrame(results)
                df.to_csv("evaluation_results.csv", index=False)
            print(f"✅ Processed {i+1}/{len(safe_batch)} | RID: {res['RID']} Evaluated.")

    df.to_csv(RESULTS_PATH, index=False)
    print(f"\n💾 Saved all raw JSON evaluations to {RESULTS_PATH}")
    
    compute_metrics(results, "C0")
    compute_metrics(results, "C1")
    compute_metrics(results, "C3")
    
    print("\n🎉 AUTOMATED EVALUATION COMPLETE!")
    if run: run.finish()

if __name__ == "__main__":
    main()
