import sys
sys.path += ["../"]
from CmsLib import *

# Assuming that cms_ddl.sql file is sourced in the mysql prompt
# If not resource the ddl script and make the entire database empty
# > sudo mysql
# > sourece ./cms_ddl.sql

# Create the sql handle
pysql = PySql("bhaskar", "biggy", "CMS")
pysql.connect_py_sql()

# Add few products
ProductManager.add_product(pysql, "BKR-20", "Bhakarwadi", "Damn Good", 35.1, "kg", 2.51)
ProductManager.add_product(pysql, "PED-45", "Pedha", "Too sweet", 70.8, "kg", 6.37)
ProductManager.add_product(pysql, "CHK-87", "Chakli", "Too hard", 10.0, "pcs", 0.9)

# Initialize the inventory
pysql.run("INSERT INTO Inventory VALUES ('BKR-20', 2000, 800, 600)")
pysql.run("INSERT INTO Inventory VALUES ('PED-45', 1000, 300, 100)")

# Add the tokens (100 tokens)
token_ids = []
for i in range(0, 100):
    token_ids.append(("TOK-" + format(i, "02d"), ))
pysql.run_many("INSERT INTO Tokens (TokenID) VALUES (%s)", token_ids)

# Get tokens for two customers
tok1 = TokenManager.get_token(pysql)
tok2 = TokenManager.get_token(pysql)

print(tok1, tok2)

# Add products to these tokens
CounterManager.add_counter_to_token(pysql, tok1, "BKR-20", 50.0)
CounterManager.add_counter_to_token(pysql, tok1, "PED-45", 85.0)
CounterManager.add_counter_to_token(pysql, tok2, "BKR-20", 180.0)
CounterManager.add_counter_to_token(pysql, tok2, "PED-45", 15.0)

# Bring some products from inventory to counter
CounterManager.add_inventory_to_counter(pysql, "PED-45", 200)

# Place orders for chaklis and pedha
ord_id = OrderManager.place_order(pysql, [("CHK-87", 1000), ("PED-45", 3000)])

# Asshuming tokens 1 and 2 generate a same invoice
inv_id = InvoiceManager.generate_invoice(pysql, [tok1, tok2], "card")
InvoiceManager.give_additional_discount(pysql, inv_id, 200)
# Replace the tokens 1 and 2
TokenManager.put_token(pysql, tok1)
TokenManager.put_token(pysql, tok2)

# Asshuming the orders arrived
OrderManager.receive_order(pysql, ord_id)
