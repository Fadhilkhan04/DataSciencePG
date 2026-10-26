from neo4j import GraphDatabase

# Connect to Neo4j
URI = "bolt://localhost:7687"
USERNAME = "neo4j"
PASSWORD = "your_password"

driver = GraphDatabase.driver(
    URI, auth=(USERNAME, PASSWORD)
)

# Create users, recipes and relationships
def create_data(tx):
    tx.run("""
        MERGE (a:User {name: 'Alice'})
        MERGE (b:User {name: 'Bob'})

        MERGE (p:Recipe {name: 'Pizza'})
        MERGE (pa:Recipe {name: 'Pasta'})
        MERGE (s:Recipe {name: 'Salad'})

        MERGE (a)-[:LIKES]->(p)
        MERGE (a)-[:LIKES]->(pa)
        MERGE (b)-[:LIKES]->(p)
        MERGE (b)-[:LIKES]->(s)
    """)

# Recommend recipes
def recommend(tx, username):
    result = tx.run("""
        MATCH (u:User {name: $username})-[:LIKES]->(common:Recipe)
              <-[:LIKES]-(other:User)
        MATCH (other)-[:LIKES]->(rec:Recipe)

        WHERE NOT (u)-[:LIKES]->(rec)

        RETURN rec.name AS recipe,
               count(DISTINCT other) AS score

        ORDER BY score DESC, recipe
    """, username=username)

    return [
        record.data() for record in result
    ]

# Execute
with driver.session() as session:
    session.execute_write(create_data)

    recommendations = session.execute_read(
        recommend, "Alice"
    )

    print("Recommended recipes for Alice:")

    for item in recommendations:
        print(item["recipe"], "- Score:", item["score"])

driver.close()