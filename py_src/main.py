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
ProductManager.add_product(pysql, "JBL-83", "Jalebi", "Damn Good", 35.1, "kg", 2.51)
ProductManager.add_product(pysql, "GOL-12", "Dunno", "Too sweet", 70.8, "kg", 6.37)
ProductManager.add_product(pysql, "PIP-88", "PeePee", "Too hard", 10.0, "pcs", 0.9)

# Initialize the inventory
pysql.run("INSERT INTO Inventory VALUES ('JBL-83', 2000, 800, 600)")
pysql.run("INSERT INTO Inventory VALUES ('GOL-12', 1000, 300, 100)")

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
CounterManager.add_counter_to_token(pysql, tok1, "PIP-88", 50.0)
CounterManager.add_counter_to_token(pysql, tok1, "GOL-12", 85.0)
CounterManager.add_counter_to_token(pysql, tok2, "PIP-88", 180.0)
CounterManager.add_counter_to_token(pysql, tok2, "JBL-83", 15.0)

# Bring some products from inventory to counter
CounterManager.add_inventory_to_counter(pysql, "PIP-88", 200)

# Place orders for chaklis and pedha
ord_id = OrderManager.place_order(pysql, [("JBL-83", 1000), ("GOL-12", 3000)])

# Asshuming tokens 1 and 2 generate a same invoice
inv_id = InvoiceManager.generate_invoice(pysql, [tok1, tok2], "wallet")
InvoiceManager.give_additional_discount(pysql, inv_id, 200)
# Replace the tokens 1 and 2
TokenManager.put_token(pysql, tok1)
TokenManager.put_token(pysql, tok2)

# Asshuming the orders arrived
OrderManager.receive_order(pysql, ord_id)
