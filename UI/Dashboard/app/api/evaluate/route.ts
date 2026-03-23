import { NextResponse } from 'next/server';
import neo4j from 'neo4j-driver';
import { GoogleGenerativeAI } from '@google/generative-ai';
let driver: neo4j.Driver;
function getDriver() {
  if (!driver) {
    driver = neo4j.driver(
      (process.env.NEO4J_URI || '').trim(),
      neo4j.auth.basic((process.env.NEO4J_USER || '').trim(), (process.env.NEO4J_PASSWORD || '').trim())
    );
  }
  return driver;
}

export async function POST(request: Request) {
  try {
    const { rid } = await request.json();
    if (!rid) return NextResponse.json({ error: 'Missing RID' }, { status: 400 });

    // 1. Fetch Summary from Neo4j
    const db = getDriver();
    const session = db.session();
    const result = await session.run(
      'MATCH (p:Patient {rid: $rid}) RETURN p.summary AS summary',
      { rid: neo4j.int(rid) }
    );
    await session.close();

    if (result.records.length === 0) {
      return NextResponse.json({ error: 'Patient not found' }, { status: 404 });
    }

    const summary = result.records[0].get('summary');

    // 2. Data Splitting Logic (Ported from evaluate_baselines.py)
    // Smart split that ignores decimals like "28.0" natively (Requires Node V8 Lookbehind Support)
    const sentences = summary.split(/(?<=[a-zA-Z])\.\s+/).map((s: string) => s.trim() + '.').filter((s: string) => s.length > 2);
    if (sentences.length < 3) {
      return NextResponse.json({ error: 'Not enough longitudinal data to split.' }, { status: 400 });
    }

    // Isolate the past context vs the current context
    const past_history = sentences.slice(0, -1).join(" ");
    const latest_visit = sentences.slice(-1).join(" ");

    // 3. Setup Gemini API
    const genai = new GoogleGenerativeAI(process.env.GEMINI_API_KEY || '');
    const model = genai.getGenerativeModel({ model: 'gemini-2.5-flash' });

    // Robust Retry logic for Google API 503 limits
    const fetchWithRetry = async (targetPrompt: string, retries = 3): Promise<any> => {
      for (let i = 0; i < retries; i++) {
        try {
          return await model.generateContent(targetPrompt);
        } catch (e: any) {
          if (e.message?.includes('503') && i < retries - 1) {
             console.warn(`[Gemini 503] Retrying inference... Attempt ${i+1}`);
             await new Promise(r => setTimeout(r, 2000 * (i + 1))); // Exponential backoff
             continue;
          }
          throw e; // Throw if other error or out of retries
        }
      }
    };

    // 4. Run C0 (Stateless)
    const promptC0 = `You are evaluating Patient RID ${rid}. 
You only have access to their MOST RECENT clinical status:
"${latest_visit}"

Task: What exactly changed in the patient's cognitive scores (like MMSE) or diagnosis since their LAST visit? 
Provide a comprehensive, well-structured summary. Use 3-4 descriptive bullet points that clearly explain the clinical shift and any missing data without being overly verbose.
Start your response strictly with: "**Patient RID ${rid}**: "`;

    // 5. Run C1 (Memory Augmented)
    const promptC1 = `You are evaluating Patient RID ${rid}. 
You have retrieved their PAST HISTORY from the vector database:
"${past_history}"

And you have their MOST RECENT clinical status:
"${latest_visit}"

Task: What exactly changed in the patient's cognitive scores (like MMSE) or diagnosis since their LAST visit? 
Calculate the exact longitudinal numerical delta (e.g. initial -> final score). Provide a comprehensive, well-structured summary. Use 3-5 descriptive bullet points that clearly explain the exact trajectory shifts and clinical significance without being overly verbose.
Start your response strictly with: "**Patient RID ${rid}**: "`;

    const [resC0, resC1] = await Promise.all([
      fetchWithRetry(promptC0),
      fetchWithRetry(promptC1)
    ]);

    return NextResponse.json({
      c0_output: resC0.response.text(),
      c1_output: resC1.response.text(),
      latest_visit,   // Send back to UI for diagnostic display
      past_history    // Send back to UI for diagnostic display
    });

  } catch (error: any) {
    console.error("Evaluation Error:", error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
