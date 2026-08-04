from neo4j import GraphDatabase
import pandas as pd

URI = "neo4j://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = ""     

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

df = pd.read_csv("recipes.csv")

with driver.session() as session:

    for index, row in df.iterrows():

        # Recipe -> Ingredient
        session.run("""
            MATCH (r:Recipe {name:$recipe})
            MATCH (i:Ingredient {name:$ingredient})
            MERGE (r)-[:CONTAINS]->(i)
        """,
        recipe=row["Recipe"],
        ingredient=row["Ingredient"])

        # Recipe -> Cuisine
        session.run("""
            MATCH (r:Recipe {name:$recipe})
            MATCH (c:Cuisine {name:$cuisine})
            MERGE (r)-[:BELONGS_TO]->(c)
        """,
        recipe=row["Recipe"],
        cuisine=row["Cuisine"])

        # Recipe -> Diet
        session.run("""
            MATCH (r:Recipe {name:$recipe})
            MATCH (d:Diet {name:$diet})
            MERGE (r)-[:SUITABLE_FOR]->(d)
        """,
        recipe=row["Recipe"],
        diet=row["Diet"])

driver.close()

print("Relationships Created Successfully!")