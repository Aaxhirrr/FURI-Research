const neo4j = require('neo4j-driver');

const uri = 'neo4j+s://a1e8aa49.databases.neo4j.io';
const user = 'a1e8aa49';
const password = 'O6Km241NG57sX1iUnIkduX1WwL9mu9wd7YUWQf9F3pU';

console.log(`Connecting to ${uri} as ${user}...`);

const driver = neo4j.driver(uri, neo4j.auth.basic(user, password));

driver.verifyConnectivity()
  .then(() => {
    console.log('✅ SUCCESS: Connected to Neo4j AuraDB!');
    return driver.getServerInfo();
  })
  .then((info) => {
    console.log('Server Info:', info);
  })
  .catch(err => {
    console.error('❌ ERROR: Failed to connect.');
    console.error(err);
  })
  .finally(() => {
    driver.close();
  });
