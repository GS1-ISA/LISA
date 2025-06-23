import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Neo4jIngestor:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def ingest_product(self, gtin, name, description):
        query = (
            "MERGE (p:Product {gtin: $gtin})"
            "ON CREATE SET p.name = $name, p.description = $description"
            "ON MATCH SET p.name = $name, p.description = $description"
            "RETURN p"
        )
        with self.driver.session() as session:
            result = session.write_transaction(self._create_product_node, query, gtin, name, description)
            return result

    @staticmethod
    def _create_product_node(tx, query, gtin, name, description):
        result = tx.run(query, gtin=gtin, name=name, description=description)
        return result.single()[0]

if __name__ == "__main__":
    # Ensure .venv is active and python-dotenv is installed
    if not os.getenv("VIRTUAL_ENV"):
        print("Error: .venv is not active. Please activate your virtual environment.")
        exit(1)

    try:
        import dotenv
    except ImportError:
        print("Error: python-dotenv is not installed. Please install it using 'pip install python-dotenv'.")
        exit(1)

    # Neo4j connection details from environment variables
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

    ingestor = None
    try:
        ingestor = Neo4jIngestor(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
        print("Successfully connected to Neo4j.")

        # Ingest a sample product
        print("Ingesting sample product...")
        product_node = ingestor.ingest_product("00012345678905", "Sample Product A", "A sample product for testing KG ingestion.")
        print(f"Ingested Product: {product_node['name']} (GTIN: {product_node['gtin']})")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if ingestor:
            ingestor.close()
            print("Neo4j connection closed.")

    print("\nTo verify ingestion:")
    print("1. Ensure your Neo4j database is running.")
    print("2. Open Neo4j Browser (usually at http://localhost:7474).")
    print("3. Run the following Cypher query:")
    print("   MATCH (p:Product {gtin: '00012345678905'}) RETURN p")
    print("You should see the 'Sample Product A' node.")