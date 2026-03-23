import { NextResponse } from 'next/server';
import neo4j from 'neo4j-driver';
import { GoogleGenerativeAI } from '@google/generative-ai';

let driver: neo4j.Driver;
function getDriver() {
  if (!driver) {
    const uri = (process.env.NEO4J_URI || '').trim();
    const user = (process.env.NEO4J_USER || '').trim();
    const password = (process.env.NEO4J_PASSWORD || '').trim();
    driver = neo4j.driver(uri, neo4j.auth.basic(user, password));
  }
  return driver;
}

export async function POST(request: Request) {
  try {
    const { query } = await request.json();
    if (!query) return NextResponse.json({ error: 'Missing query' }, { status: 400 });

    const genai = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || '');
    const model = genai.getGenerativeModel({ model: 'gemini-2.5-flash' });

    const fetchWithRetry = async (targetPrompt: string, retries = 3): Promise<any> => {
      for (let i = 0; i < retries; i++) {
        try {
          return await model.generateContent(targetPrompt);
        } catch (e: any) {
          if (e.message?.includes('503') && i < retries - 1) {
             console.warn(`[Gemini 503] Retrying consultant inference... Attempt ${i+1}`);
             await new Promise(r => setTimeout(r, 2000 * (i + 1))); 
             continue;
          }
          throw e; 
        }
      }
    };

    // Step 1: MultiClinNER Entity Projection
    const promptNER = `You are a MultiClinAI Entity Extractor (ACL 2026).
INPUT: "${query}"

1. Detect Language.
2. Extract Clinical Entities (Diseases, Symptoms, Procedures).
3. Project them to the English medical equivalents used in our Knowledge Graph.

 Return ONLY a JSON list of objects: 
[ { "original": "...", "projected_node": "...", "type": "..." } ]`;

    const nerResponse = await fetchWithRetry(promptNER);
    let entitiesStr = nerResponse.response.text().replace(/```json/g, '').replace(/```/g, '').trim();
    let entities: any[] = [];
    try {
      entities = JSON.parse(entitiesStr);
    } catch(e) {
      console.error("NER JSON parse failed:", entitiesStr);
      return NextResponse.json({ error: "Failed to extract entities." }, { status: 500 });
    }

    if (!entities || entities.length === 0) {
      return NextResponse.json({
        entities: [],
        evidence: [],
        assessment: "No clinical entities detected in the query."
      });
    }

    // Step 2: Query Graph Evidence
    const db = getDriver();
    const session = db.session();
    const allEvidence: string[] = [];
    const projectedList: string[] = [];

    for (const ent of entities) {
      projectedList.push(ent.projected_node);
      const result = await session.run(`
        MATCH (n)-[r]->(target)
        WHERE toLower(n.name) CONTAINS toLower($name)
        RETURN n.name AS s_name, type(r) AS r_type, target.name AS t_name
        LIMIT 2
      `, { name: ent.projected_node });

      result.records.forEach(req => {
        allEvidence.push(`✅ ${req.get('s_name')} --[${req.get('r_type')}]--> ${req.get('t_name')}`);
      });
    }
    await session.close();

    // Step 3: Generative Clinical Assessment Grounding
    const promptAssessment = `Using these projected clinical nodes: ${JSON.stringify(projectedList)}, 
provide a risk assessment based on our 109-patient study results. 
Cite the 47.7% MCI-to-Dementia and 25% NL-to-MCI transition rates. Maintain a professional, clinical tone. Do not ask for user response.`;

    const assessResponse = await fetchWithRetry(promptAssessment);

    return NextResponse.json({
      entities,
      evidence: allEvidence,
      assessment: assessResponse.response.text()
    });

  } catch (error: any) {
    console.error("Consultant Error:", error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
