import { NextResponse } from 'next/server';
import neo4j from 'neo4j-driver';

// Global Neo4j Driver
let driver: neo4j.Driver;
function getDriver() {
  if (!driver) {
    const uri = (process.env.NEO4J_URI || '').trim();
    const user = (process.env.NEO4J_USER || '').trim();
    const password = (process.env.NEO4J_PASSWORD || '').trim();
    driver = neo4j.driver(uri, neo4j.auth.basic(user, password), {
      maxConnectionPoolSize: 50,
    });
  }
  return driver;
}

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const limitStr = searchParams.get("limit");
  const limit = parseInt(limitStr || "200");
  
  const dbDriver = getDriver();
  const session = dbDriver.session();

  try {
    const result = await session.run(`
      MATCH (n)-[r]->(m)
      RETURN id(n) AS source_id, labels(n)[0] AS source_label, n.name AS source_name, n.rid AS source_rid,
             type(r) AS edge_type, id(r) AS edge_id,
             id(m) AS target_id, labels(m)[0] AS target_label, m.name AS target_name, m.rid AS target_rid
      LIMIT $limit
    `, { limit: neo4j.int(limit) });

    const nodesMap = new Map();
    const edges: any[] = [];

    result.records.forEach((req: any) => {
      const sourceId = req.get('source_id').toString();
      const targetId = req.get('target_id').toString();
      
      const sourceLabel = req.get('source_label');
      const targetLabel = req.get('target_label');

      if (!nodesMap.has(sourceId)) {
        nodesMap.set(sourceId, {
          id: sourceId,
          label: sourceLabel === 'Patient' ? `RID ${req.get('source_rid')}` : (req.get('source_name') || sourceLabel),
          group: sourceLabel
        });
      }
      if (!nodesMap.has(targetId)) {
        nodesMap.set(targetId, {
          id: targetId,
          label: targetLabel === 'Patient' ? `RID ${req.get('target_rid')}` : (req.get('target_name') || targetLabel),
          group: targetLabel
        });
      }
      edges.push({
        id: req.get('edge_id').toString(),
        from: sourceId,
        to: targetId,
        label: req.get('edge_type'),
        arrows: 'to'
      });
    });

    const nodes = Array.from(nodesMap.values());
    return NextResponse.json({ nodes, edges });
  } catch (error: any) {
    console.error("Graph Error:", error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  } finally {
    await session.close();
  }
}
