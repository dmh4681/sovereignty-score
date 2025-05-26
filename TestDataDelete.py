import duckdb

# Connect to your DuckDB database
con = duckdb.connect("data/sovereignty.duckdb")

# Delete all rows
con.execute("DELETE FROM sovereignty;")

# Confirm
remaining = con.execute("SELECT COUNT(*) FROM sovereignty;").fetchone()[0]
print(f"✅ Deleted all test data. Rows remaining: {remaining}")
