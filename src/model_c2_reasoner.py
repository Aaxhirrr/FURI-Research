import os
import json
from openai import OpenAI
from neo4j_client import kg_client
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

tools = [{
    "type": "function",
    "function": {
        "name": "query_knowledge_graph",
        "description": "Executes a Cypher query against the FuriMasterKG Neo4j database to retrieve clinical data.",
        "parameters": {
            "type": "object",
            "properties": {
                "cypher_query": {
                    "type": "string",
                    "description": "A valid Neo4j Cypher query string."
                }
            },
            "required": ["cypher_query"]
        }
    }
}]

def query_knowledge_graph(cypher_query: str) -> str:
    print(f"\n   [🛠️ C2 TOOL TRIGGERED] Executing Cypher:\n   {cypher_query}\n")
    results = kg_client.execute_query(cypher_query)
    return json.dumps(results)

def chat_loop():
    print("—"*60)
    print("🧠 MODEL C2: GRAPH-ONLY REASONER (FURI)")
    print("⚡ Powered by OpenAI gpt-4o")
    print("—"*60)
    
    messages = [
        {"role": "system", "content": (
            "You are Model C2, the Autonomous Graph-Only Reasoner.\n\n"
            "STRICT SCHEMA RULES (DO NOT DEVIATE):\n"
            "1. ONLY use the label (:Patient).\n"
            "2. ONLY use the relationship [:SIMILAR_TO].\n"
            "3. ALL clinical data (APOE4, MCI, MMSE, Atrophy) is stored in the 'p.summary' property.\n"
            "4. NEVER use other labels like :Genotype, :Condition, :Diagnosis, :APOE.\n"
            "5. ERROR HANDLING: If you write a query that returns no results, do not keep guessing. Stop.\n\n"
            "HOW TO QUERY:\n"
            "- Step 1: Find a patient using a summary search (e.g., MATCH (p:Patient) WHERE toLower(p.summary) CONTAINS 'apoe4' AND toLower(p.summary) CONTAINS 'mci' RETURN p LIMIT 1)\n"
            "- Step 2: Once you have a patient, find their twins (e.g., MATCH (p1:Patient {rid: <RID_FROM_STEP1>})-[:SIMILAR_TO]-(p2:Patient) RETURN p2.summary LIMIT 3)\n\n"
            "Perform exactly these steps to answer the user's clinical question."
        )}
    ]
    
    while True:
        try:
            user_input = input("\n👤 Query: ")
        except EOFError:
            break
            
        if user_input.lower() in ['exit', 'quit']: break
        
        messages.append({"role": "user", "content": user_input})
        print("🤖 C2 Model is thinking and querying the FuriMasterKG...")
        
        # Open tool calling loop
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
                    if tool_call.function.name == "query_knowledge_graph":
                        args = json.loads(tool_call.function.arguments)
                        func_result = query_knowledge_graph(args["cypher_query"])
                        temp_messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_call.function.name,
                            "content": func_result
                        })
            else:
                print("\n🩺 C2 RESPONSE:")
                print(message.content)
                messages.append({"role": "assistant", "content": message.content})
                break

if __name__ == "__main__":
    chat_loop()
