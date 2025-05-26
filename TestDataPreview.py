import duckdb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Connect to DuckDB database
con = duckdb.connect("data/sovereignty.duckdb")

# Query all data
df = con.execute("SELECT * FROM sovereignty ORDER BY timestamp DESC").df()

df_top100 = con.execute("SELECT * FROM sovereignty ORDER BY timestamp DESC LIMIT 1000").df()

# Summary
print("=== Sovereignty Score Test Data Overview ===")
print("Total Records:", len(df))
print("Unique Users:", df["username"].nunique())
print("Earliest Entry:", df["timestamp"].min())
print("Latest Entry:", df["timestamp"].max())
print("Average Score:", round(df["score"].mean(), 2))
print("Top Paths:\n", df["path"].value_counts().head(5))

print("\nTop 10 Users:")
print(df["username"].value_counts().head(10))

# Histogram
plt.figure(figsize=(10, 5))
sns.histplot(df["score"], bins=20, kde=True, color="gold")
plt.title("Distribution of Sovereignty Scores")
plt.savefig("score_distribution.png")

# Path bar chart
plt.figure(figsize=(10, 5))
sns.countplot(data=df, x="path", order=df["path"].value_counts().index, palette="viridis")
plt.title("Submissions per Sovereignty Path")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("path_counts.png")

print("\n✅ Charts saved: score_distribution.png, path_counts.png")

print(df_top100.to_string(index=False))