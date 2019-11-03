from flask import Flask, render_template, request, redirect
import sys
sys.path += ['../']
from CmsLib import *

app = Flask(__name__ , template_folder = '../html_src/', static_folder = '../html_src/')
pysql = PySql(app, 'db.yaml')

@app.route('/', methods = ['GET', 'POST'])
def index():
    pysql.connect_py_sql()
    return render_template('index.html')

@app.route('/InventoryManager', methods = ['GET', 'POST'])
def load_inventory_modules():
    if request.method == 'POST' :
        if 'place_order' in request.form:
            return redirect('InventoryManager/PlaceOrder')
        elif 'receive_order' in request.form:
            return redirect('InventoryManager/ReceiveOrder')
        elif 'cancel_order' in request.form:
            return redirect('InventoryManager/CancelOrder')
        elif 'view_inventory' in request.form:
            return redirect('InventoryManager/ViewInventory')
        elif 'view_products' in request.form:
            return redirect('InventoryManager/ViewProducts')
        elif 'order_details' in request.form:
            return redirect('InventoryManager/OrderDetails')
        elif 'daily_orders' in request.form:
            return redirect('InventoryManager/DailyOrders')
        elif 'transaction_log' in request.form:
            return redirect('InventoryManager/TransactionLog')
        elif 'products_in_orders' in request.form:
            return redirect('InventoryManager/ProductsInOrders')
        elif 'products_in_inv_transactions' in request.form:
            return redirect('InventoryManager/ProductsInInvTransactions')

    return render_template('InventoryManager/inventory_manager_home.html')
    
@app.route('/InventoryManager/PlaceOrder', methods = ['GET', 'POST'])
def place_order():
    order_details = list()
    product_ = pysql.run('SELECT * FROM products')
    #product_ = ProductManager.get_all_products(pysql)
    '''print (product_)
    product_data = [(each[0], each[1], each[4]) for each in product_]
    if request.method == 'POST':
        if 'add_product' in request.form:
            order_details.append((request.form['product_id'], request.form['quantity']))
        elif 'place_order' in request.form:
            order_id = OrderManager.place_order(pysql, order_details)
            return render_template('/InventoryManager/success_placed.html', order_id = order_id)'''
    return render_template('/InventoryManager/place_order.html', product_data = product_data)

@app.route('/InventoryManager/ReceiveOrder', methods = ['GET', 'POST'])
def receive_order():
    if request.method == 'POST':
        order_id = request.form['order_id']
        OrderManager.receive_order(pysql, order_id)
        return redirect('/InventoryManager')

@app.route('/InventoryManager/CancelOrder', methods = ['GET', 'POST'])
def cancel_order():
    if request.method == 'POST':
        order_id = request.form['order_id']
        OrderManager.cancel_order(pysql, order_id)
        return redirect('/InventoryManager')

'''@app.route('/InventoryManager/ViewInventory', methods = ['GET', 'POST'])
def place_order():
    pass

@app.route('/InventoryManager/ViewProducts', methods = ['GET', 'POST'])
def place_order():
    pass

@app.route('/InventoryManager/OrderDetails', methods = ['GET', 'POST'])
def place_order():
    pass

@app.route('/InventoryManager/DailyOrders', methods = ['GET', 'POST'])
def place_order():
    pass

@app.route('/InventoryManager/TransactionLog', methods = ['GET', 'POST'])
def place_order():
    pass
'''
@app.route('/InventoryManager/ProductsInInvTransactions', methods = ['GET', 'POST'])
def fn():
    pass



if __name__ == "__main__" :
    app.run(debug = True)