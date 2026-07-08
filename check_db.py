import sqlite3

conn = sqlite3.connect("data/products.db")
conn.row_factory = sqlite3.Row

cursor = conn.cursor()

cursor.execute("SELECT * FROM products")

rows = cursor.fetchall()

print(f"\nTotal Products: {len(rows)}\n")

for row in rows:
    print(dict(row))

conn.close()
