from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "neo4j://127.0.0.1:7687",
    auth=("neo4j","2026165038")
)


recipe=input("Enter Recipe : ")

with driver.session() as session:

    result=session.run("""

    MATCH (r1:Recipe {name:$recipe})-[:CONTAINS]->(i)<-[:CONTAINS]-(r2:Recipe)

    WHERE r1<>r2

    RETURN

    r2.name,

    COUNT(i) AS Similarity

    ORDER BY Similarity DESC

    LIMIT 5

    """,

    recipe=recipe)

    print("\nRecommended Recipes\n")

    for x in result:

        print(x["r2.name"],
              "Similarity =",x["Similarity"])

driver.close()