# Quick database update script
import duckdb

con = duckdb.connect("data/sovereignty.duckdb")

# Update all test user emails to your personal email
con.execute("""
    UPDATE users 
    SET email = 'dmh4681@gmail.com' 
    WHERE username IN ('test', 'test2', 'test_physical', 'test_financial', 'test_mental', 'test_spiritual')
""")

# Verify the changes
updated_users = con.execute("""
    SELECT username, email, path 
    FROM users 
    WHERE email = 'dmh4681@gmail.com'
""").fetchall()

print("Updated users:")
for user in updated_users:
    print(f"  {user[0]} | {user[1]} | {user[2]}")

con.close()