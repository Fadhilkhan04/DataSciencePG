from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "neo4j://127.0.0.1:7687",
    auth=("neo4j","")
)


with driver.session() as session:

    while True:

        print("\n========== MENU ==========")
        print("1. Show Recipes")
        print("2. Show Ingredients of a Recipe")
        print("3. Recipes Containing an Ingredient")
        print("4. Average Rating")
        print("5. Highest Rated Recipe")
        print("6. Exit")

        choice = input("Enter Choice : ")

        if choice=="1":

            result=session.run("""

            MATCH (r:Recipe)

            RETURN r.name

            """)

            for x in result:

                print(x["r.name"])

        elif choice=="2":

            recipe=input("Enter Recipe : ")

            result=session.run("""

            MATCH (r:Recipe {name:$recipe})-[:CONTAINS]->(i)

            RETURN i.name

            """,

            recipe=recipe)

            for x in result:

                print(x["i.name"])

        elif choice=="3":

            ingredient=input("Enter Ingredient : ")

            result=session.run("""

            MATCH (r:Recipe)-[:CONTAINS]->(i:Ingredient {name:$ingredient})

            RETURN r.name

            """,

            ingredient=ingredient)

            for x in result:

                print(x["r.name"])

        elif choice=="4":

            result=session.run("""

            MATCH (:User)-[x:RATED]->(r:Recipe)

            RETURN r.name,
            AVG(x.score) AS Rating

            """)

            for x in result:

                print(x["r.name"],round(x["Rating"],2))

        elif choice=="5":

            result=session.run("""

            MATCH (:User)-[x:RATED]->(r:Recipe)

            RETURN r.name,
            AVG(x.score) AS Rating

            ORDER BY Rating DESC

            LIMIT 1

            """)

            for x in result:

                print(x["r.name"],round(x["Rating"],2))

        elif choice=="6":

            break

driver.close()