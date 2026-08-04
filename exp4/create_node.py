from neo4j import GraphDatabase
import pandas as pd

URI = "neo4j://127.0.0.1:7687"
USERNAME = "neo4j"
PASSWORD = "2026165038"      

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


df = pd.read_csv("recipes.csv")

with driver.session() as session:

   
    for recipe in df["Recipe"].unique():

        session.run(
            """
            MERGE (:Recipe {name:$recipe})
            """,
            recipe=recipe
        )

    for ingredient in df["Ingredient"].unique():

        session.run(
            """
            MERGE (:Ingredient {name:$ingredient})
            """,
            ingredient=ingredient
        )

    for cuisine in df["Cuisine"].unique():

        session.run(
            """
            MERGE (:Cuisine {name:$cuisine})
            """,
            cuisine=cuisine
        )

    for diet in df["Diet"].unique():

        session.run(
            """
            MERGE (:Diet {name:$diet})
            """,
            diet=diet
        )

driver.close()

print("All nodes created successfully!")