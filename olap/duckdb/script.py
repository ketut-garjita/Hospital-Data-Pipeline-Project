import duckdb

con = duckdb.connect("my_duckdb.db")  # creates file-based DB
con.execute("CREATE TABLE IF NOT EXISTS items (id INTEGER, name VARCHAR)")
con.execute("INSERT INTO items VALUES (1, 'apple'), (2, 'banana')")
print(con.execute("SELECT * FROM items").fetchall())

