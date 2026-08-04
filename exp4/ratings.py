from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "neo4j://127.0.0.1:7687",
    auth=("neo4j","2026165038")
)

ratings = [

    ("Ahmed","Veg Pizza",5),
    ("Ahmed","Chicken Tikka",4),

    ("John","Garlic Bread",5),
    ("John","Fish Curry",4),

    ("Sara","Spring Rolls",5),
    ("Sara","Veg Momos",4),

    ("Ali","Mac and Cheese",5),
    ("Ali","Egg Fried Rice",4),

    ("David","Mushroom Soup",5),
    ("David","Paneer Butter Masala",4)

]

with driver.session() as session:

    for user,recipe,score in ratings:

        session.run("""

        MATCH (u:User {name:$user})

        MATCH (r:Recipe {name:$recipe})

        MERGE (u)-[x:RATED]->(r)

        SET x.score=$score

        """,

        user=user,

        recipe=recipe,

        score=score)

driver.close()

print("Ratings Added Successfully!")