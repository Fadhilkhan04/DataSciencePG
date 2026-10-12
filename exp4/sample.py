# 1. Import library
from neo4j import GraphDatabase

# 2. Connect to Neo4j
uri = "bolt://localhost:7687"
username = "neo4j"
password = "your_password"

driver = GraphDatabase.driver(
    uri, auth=(username, password)
)

# 3. Create recipes and ingredients
def create_recipes(tx):
    tx.run("""
        CREATE (r1:Recipe {name: 'Pasta'})
        CREATE (r2:Recipe {name: 'Sandwich'})
        CREATE (r3:Recipe {name: 'Salad'})

        CREATE (i1:Ingredient {name: 'Tomato'})
        CREATE (i2:Ingredient {name: 'Cheese'})
        CREATE (i3:Ingredient {name: 'Bread'})
        CREATE (i4:Ingredient {name: 'Lettuce'})

        CREATE (r1)-[:CONTAINS]->(i1)
        CREATE (r1)-[:CONTAINS]->(i2)
        CREATE (r2)-[:CONTAINS]->(i2)
        CREATE (r2)-[:CONTAINS]->(i3)
        CREATE (r3)-[:CONTAINS]->(i1)
        CREATE (r3)-[:CONTAINS]->(i4)
    """)

# 4. Recommend recipes
def recommend_recipes(tx, ingredient):
    result = tx.run("""
        MATCH (r:Recipe)-[:CONTAINS]->(i:Ingredient)
        WHERE toLower(i.name) = toLower($ingredient)
        RETURN DISTINCT r.name AS recipe
    """, ingredient=ingredient)

    return [record["recipe"] for record in result]

# 5. Execute program
try:
    with driver.session() as session:
        session.execute_write(create_recipes)

        ingredient = input("Enter an ingredient: ")

        recipes = session.execute_read(
            recommend_recipes, ingredient
        )

        if recipes:
            print("Recommended Recipes:")
            for recipe in recipes:
                print(recipe)
        else:
            print("No recipes found.")

finally:
    driver.close()