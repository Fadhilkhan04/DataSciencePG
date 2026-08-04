from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "neo4j://127.0.0.1:7687",
    auth=("neo4j","2026165038")
)

users = [
    "Ahmed",
    "John",
    "Sara",
    "Ali",
    "David"
]

with driver.session() as session:

    for user in users:

        session.run("""

        MERGE (:User {name:$name})

        """,
        name=user)

driver.close()

print("Users Created Successfully!")