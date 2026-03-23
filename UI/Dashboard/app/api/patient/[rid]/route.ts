import { NextResponse } from 'next/server';
import neo4j from 'neo4j-driver';

// Global Driver Singleton for Next.js Fast Refresh
let driver: neo4j.Driver;

function getDriver() {
  if (!driver) {
    const uri = (process.env.NEO4J_URI || '').trim();
    const user = (process.env.NEO4J_USER || '').trim();
    const password = (process.env.NEO4J_PASSWORD || '').trim();
    driver = neo4j.driver(uri, neo4j.auth.basic(user, password), {
      maxConnectionPoolSize: 50,
      connectionAcquisitionTimeout: 20000
    });
  }
  return driver;
}

export async function GET(request: Request, context: any) {
  const resolvedParams = await context.params;
  const ridStr = resolvedParams.rid;
  
  const rid = parseInt(ridStr);
  if (isNaN(rid)) {
    return NextResponse.json({ error: 'Invalid RID' }, { status: 400 });
  }

  const dbDriver = getDriver();
  const session = dbDriver.session();

  try {
    // 1. Fetch Patient Timeline Summary from Macro/Micro Graph
    const patientResult = await session.run(
      'MATCH (p:Patient {rid: $rid}) RETURN p.summary AS summary, p.total_visits AS total_visits',
      { rid: neo4j.int(rid) }
    );

    if (patientResult.records.length === 0) {
      return NextResponse.json({ error: 'Patient not found' }, { status: 404 });
    }

    const summary = patientResult.records[0].get('summary');
    const totalVisits = patientResult.records[0].get('total_visits');

    // 2. Fetch Clinical Twins from the P2P Mesh Layer
    const twinResult = await session.run(
      'MATCH (p:Patient {rid: $rid})-[:SIMILAR_TO]-(twin:Patient) RETURN twin.rid AS twin_rid',
      { rid: neo4j.int(rid) }
    );
    // Extract twins into an array
    const twins = twinResult.records.map(r => {
      const twin_rid = r.get('twin_rid');
      return neo4j.integer.toNumber(twin_rid);
    });

    return NextResponse.json({
      rid,
      summary,
      totalVisits: totalVisits ? neo4j.integer.toNumber(totalVisits) : 1,
      twinsCount: twins.length,
      twins
    });
  } catch (error: any) {
    console.error("Neo4j Error:", error);
    return NextResponse.json({ 
      error: error.message
    }, { status: 500 });
  } finally {
    // DO NOT close the driver here, only the session.
    await session.close();
  }
}
