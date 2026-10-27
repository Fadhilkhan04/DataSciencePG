import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

# 1. Load datasets
map_data = gpd.read_file("india_states.geojson")
df = pd.read_csv("population.csv")

# 2. Clean state names
map_data["State"] = map_data["State"].str.strip().str.lower()
df["State"] = df["State"].str.strip().str.lower()

# 3. Remove missing values
map_data = map_data.dropna(subset=["State"])
df = df.dropna(subset=["State", "Population"])

# 4. Remove duplicate states in CSV
df = df.drop_duplicates(subset=["State"])

# 5. Merge datasets
merged = map_data.merge(df, on="State", how="inner")

# 6. Plot map
merged.plot(column="Population", legend=True)
plt.title("State-wise Population")
plt.show()