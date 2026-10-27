from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt

client = MongoClient("mongodb://localhost:27017/")

db = client["CVE_Database"]
collection = db["vulnerabilities"]

data = list(collection.find({}, {"_id": 0}))

df = pd.DataFrame(data)

print(df.head())