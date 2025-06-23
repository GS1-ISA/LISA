import neo4j, { Driver, Session, Record } from 'neo4j-driver';
import { z } from 'zod'; // Assuming zod is used for schema definition in Genkit
import { ai } from '../genkit'; // Import the ai object

let driver: Driver | null = null;

// Initialize Neo4j Driver
function initializeNeo4jDriver() {
  if (!driver) {
    const uri = process.env.NEO4J_URI || 'bolt://localhost:7687';
    const user = process.env.NEO4J_USER || 'neo4j';
    const password = process.env.NEO4J_PASSWORD || 'password'; // Consider more secure handling

    driver = neo4j.driver(uri, neo4j.auth.basic(user, password));

    // Verify connection on initialization
    driver.verifyConnectivity()
      .then(() => {
        console.log('Neo4j Driver initialized and connected successfully.');
      })
      .catch((error: Error) => { // Explicitly type error
        console.error('Neo4j Driver initialization failed:', error);
        driver = null; // Reset driver if connection fails
        throw error;
      });
  }
  return driver;
}

// Close Neo4j Driver (optional, for graceful shutdown)
export async function closeNeo4jDriver() {
  if (driver) {
    console.log('Closing Neo4j Driver...');
    await driver.close();
    driver = null;
    console.log('Neo4j Driver closed.');
  }
}

export const queryKnowledgeGraphTool = ai.defineTool(
  {
    name: 'queryKnowledgeGraph',
    description: 'Executes a Cypher query against the Neo4j Knowledge Graph and returns the results. This tool is designed to retrieve structured information from the graph database based on a provided Cypher query.',
    inputSchema: z.object({ // Use zod for input schema
      cypherQuery: z.string().describe('The Cypher query to execute against the Neo4j Knowledge Graph. Ensure the query is valid Cypher syntax.'),
    }),
    outputSchema: z.array(z.record(z.any())).describe('An array of records from the Cypher query result, where each record is an object.'), // Use zod for output schema
  },
  async (input: { cypherQuery: string }) => { // Explicitly type input
    let session: Session | null = null;
    try {
      const neo4jDriver = initializeNeo4jDriver();
      session = neo4jDriver.session();
      const result = await session.run(input.cypherQuery);

      // Convert Neo4j records to plain JavaScript objects
      const records = result.records.map((record: Record) => { // Explicitly type record
        const obj: { [key: string]: any } = {};
        record.keys.forEach((key: PropertyKey, index: number) => { // Corrected type for key
          obj[key.toString()] = record.get(index); // Convert PropertyKey to string for object key
        });
        return obj;
      });

      return records;
    } catch (error: unknown) { // Changed to unknown as per TypeScript best practices
      console.error('Error executing Cypher query:', error);
      // Ensure error is an instance of Error before accessing message
      throw new Error(`Failed to query knowledge graph: ${(error as Error).message}`);
    } finally {
      if (session) {
        await session.close();
      }
    }
  }
);