# Import the required libraries
from flask import Flask, render_template, request, redirect
import sys
from decimal import Decimal
#from waitress import serve
sys.path.append('../')
from CmsLib import *

# Create the flask object for server side programming
app = Flask(__name__ ,
            template_folder = '../html_src/',
            static_folder = '../html_src/')

# Create the pysql object for database programming
pysql = PySql(app, 'db.yaml')

# Index page
@app.route('/', methods = ['GET', 'POST'])
def index():
    return render_template('index.html')

# Inventory manager page
@app.route('/InventoryManager', methods = ['GET', 'POST'])
def inventory_manager():
    if request.method == 'POST' :
        # List of options
        options = ["AddProduct",
                   "PlaceOrder",
                   "ReceiveOrder",
                   "CancelOrder",
                   "ViewInventory",
                   "ViewProducts",
                   "OrderDetails",
                   "OrdersBetweenDates",
                   "TransactionLog",
                   "ProductDateTransactionLog"]

        # Check if any option is asserted
        for option in options:
            if option in request.form:
                return redirect("InventoryManager/" + option)

    return render_template('/InventoryManager/inventory_manager.html')


# Add product page
@app.route('/InventoryManager/AddProduct', methods = ['GET', 'POST'])
def inventory_manager_add_product():
    if request.method == 'POST':
        # Get the product details
        product_id = request.form['ProductID'].strip()
        name = request.form['Name'].strip()
        description = request.form['Description'].strip()
        unit_price = float((request.form['UnitPrice'].strip()))
        unit_type = request.form['UnitType'].strip()
        gst = float(request.form['GST'].strip())
        cgst = float(request.form['CGST'].strip())
        current_discount = float(request.form['CurrentDiscount'].strip())

        # Add the product
        retval = ProductManager.add_product(pysql, product_id, name, description, unit_price, unit_type, gst, cgst, current_discount)

        # If no errors
        if retval == 0:
            return render_template('InventoryManager/inventory_manager_success.html', result='Product Added successfully')

        # If errors
        error_reasons = ["Product ID already used.",
                         "Unit price not valid.,",
                         "Unit type not valid.",
                         "GST or CGST not valid",
                         "Discount not valid."]
        return render_template('InventoryManager/inventory_manager_failure.html', reason=error_reasons[retval - 1])
    else:
        return render_template('InventoryManager/inventory_manager_add_product.html')

# Place order page
@app.route('/InventoryManager/PlaceOrder', methods = ['GET', 'POST'])
def inventory_manager_place_order():
    # Get all products
    products = ProductManager.get_all_products(pysql)
    # Get the product ids, names and the unit types
    products = [(each[0], each[1], each[4]) for each in products]

    if request.method == 'POST':
        # Order list
        product_quantities = []
        # Quantities entered by user
        quantities = request.form.getlist("Quantity[]")
        # Get the product ids
        product_ids = [each[0] for each in products]
        # Check for each quantity
        for product_id, quantity in zip(product_ids, quantities):
            # Check if quantity is not null
            if quantity:
                # Convert string to float
                quantity = float(quantity)
                # Check if quantity is non zero
                if quantity:
                    product_quantities.append((product_id, quantity))

        # If product quantities are not null
        if product_quantities:
            # Place order
            retval = OrderManager.place_order(pysql, product_quantities)

            # If error
            error_reasons = ["Details of one of the products ordered not found.",
                             "One of the quantities in the order is not valid"]
            if retval == 1 or retval == 2:
                return render_template('/InventoryManager/inventory_manager_failure.html', reason=error_reasons[retval - 1])

            # If no error
            return render_template('/InventoryManager/inventory_manager_success.html', result="Order {} Placed Successfully".format(retval))
        else:
            return redirect('/InventoryManager')
    else:
        return render_template('/InventoryManager/inventory_manager_place_order.html', products=products)


# Receive order page
@app.route('/InventoryManager/ReceiveOrder', methods = ['GET', 'POST'])
def inventory_manager_receive_order():
    if request.method == 'POST':
        # Get the order id
        order_id = request.form['OrderID'].strip()
        # Receive the order
        retval = OrderManager.receive_order(pysql, order_id)

        # If no errors
        if retval == 0:
            return render_template('/InventoryManager/inventory_manager_success.html', result="Order received successfully")

        # If errors
        error_reasons = ["Order ID not found.",
                         "Order already delivered.",
                         "Order was previously cancelled."]
        return render_template('/InventoryManager/inventory_manager_failure.html', reason=error_reasons[retval - 1])
    else:
        return render_template('/InventoryManager/inventory_manager_receive_order.html')


# # Cancel order page
@app.route('/InventoryManager/CancelOrder', methods = ['GET', 'POST'])
def inventory_manager_cancel_order():
    if request.method == 'POST':
        # Get the order id
        order_id = request.form['OrderID'].strip()
        # Cancel the order
        retval = OrderManager.cancel_order(pysql, order_id)

        # If no errors
        if retval == 0:
            return render_template('/InventoryManager/inventory_manager_success.html', result="Order cancelled successfully")

        # If errors
        error_reasons = ["Order ID not found.",
                         "Order already delivered.",
                         "Order was previously cancelled."]
        return render_template('/InventoryManager/inventory_manager_failure.html', reason=error_reasons[retval - 1])
    else:
        return render_template('/InventoryManager/inventory_manager_cancel_order.html')


# View inventory page
@app.route('/InventoryManager/ViewInventory', methods = ['GET', 'POST'])
def inventory_manager_view_inventory():
    # Get the inventory details
    inventory = InventoryManager.get_inventory_details(pysql)
    return render_template('/InventoryManager/inventory_manager_view_inventory.html', inventory = inventory)


# View products page
@app.route('/InventoryManager/ViewProducts', methods = ['GET', 'POST'])
def inventory_manager_view_products():
    # Get the product details
    products = ProductManager.get_all_products(pysql)
    return render_template('/InventoryManager/inventory_manager_view_products.html', products=products)


# Order details page
@app.route('/InventoryManager/OrderDetails', methods = ['GET', 'POST'])
def inventory_manager_order_details():
    if request.method == 'POST':
        # Get the order id
        order_id = request.form['OrderID'].strip()
        # Get the order details
        order_status, order_details = OrderManager.get_order_details(pysql, order_id)
        return render_template('/InventoryManager/inventory_manager_order_details_result.html', order_status=order_status, order_details=order_details)
    else:
        return render_template('/InventoryManager/inventory_manager_order_details.html')


# Orders between dates page
@app.route('/InventoryManager/OrdersBetweenDates', methods = ['GET', 'POST'])
def inventory_manager_daily_orders():
    if request.method == 'POST':
        # Get the start and end date
        from_date, to_date = request.form['FromDate'], request.form['ToDate']
        # Get the order details of those orders
        orders = OrderManager.get_orders_between_date(pysql, from_date, to_date)
        return render_template('/InventoryManager/inventory_manager_orders_between_dates_result.html', from_date=from_date, to_date=to_date, orders=orders)
    else:
        return render_template('/InventoryManager/inventory_manager_orders_between_dates.html')


# Transaction log page
@app.route('/InventoryManager/TransactionLog', methods = ['GET', 'POST'])
def inventory_manager_transaction_log():
    # Get the transactions
    transactions = InventoryManager.get_transactions(pysql)
    return render_template('/InventoryManager/inventory_manager_transaction_log.html', transactions=transactions)


# Product date transaction page
@app.route('/InventoryManager/ProductDateTransactionLog', methods = ['GET', 'POST'])
def inventory_manager_transactions_of_product_on_date():
    # Get all products
    products = ProductManager.get_all_products(pysql)
    # Get the names of the products only
    products = [each[1] for each in products]

    if request.method == 'POST':
        # Get the on date and product name
        on_date, product_name = request.form['OnDate'], request.form['Name']
        # Get the product id from name
        product_id = ProductManager.get_product_id_from_name(pysql, product_name)
        transactions = InventoryManager.get_transactions_of_product_by_date(pysql, product_id, on_date)
        return render_template('/InventoryManager/inventory_manager_product_date_transaction_log_result.html', transactions=transactions)
    else:
        return render_template('/InventoryManager/inventory_manager_product_date_transaction_log.html', products=products)


# Token manager page
@app.route('/TokenManager', methods = ['GET', 'POST'])
def token_manager():
    if request.method == 'POST':
        # Set the options provided
        options = ["GetTokenStatuses",
                   "GetToken",
                   "ReturnToken",
                   "GetTokenDetails",
                   "AddToken",
                   "RemoveToken"]

        # Check if option is asserted
        for option in options:
            if option in request.form:
                return redirect("/TokenManager/" + option)
    else:
        return render_template('/TokenManager/token_manager.html')


# Token statuses page
@app.route('/TokenManager/GetTokenStatuses', methods = ['GET', 'POST'])
def token_manager_token_statuses():
    # Get the token statuses
    statuses = TokenManager.get_all_tokens_status(pysql)
    return render_template('/TokenManager/token_manager_token_statuses.html', statuses=statuses)


# Get token page
@app.route('/TokenManager/GetToken', methods = ['GET', 'POST'])
def token_manager_get_token():
    # Get the token from the available tokens
    token_id = TokenManager.get_token(pysql)
    if token_id is None:
        return render_template('/TokenManager/token_manager_failure.html', reason="Token not available")
    else:
        return render_template('/TokenManager/token_manager_get_token.html', token_id=token_id)


# Return token page
@app.route('/TokenManager/ReturnToken', methods = ['GET', 'POST'])
def token_manager_return_token():
    if request.method == 'POST':
        # Get the token id
        token_id = request.form['TokenID']
        # Return the token
        retval = TokenManager.put_token(pysql, token_id)

        # If no errors
        if retval == 0:
            return render_template('/TokenManager/token_manager_success.html', result="Token returned successfully")

        # If errors
        error_reasons = ["Token has products. Remove them first to continue.",
                         "Token is not assigned. Please check again and continue",
                         "Token not found. Please confirm token ID and continue"]
        return render_template('/TokenManager/token_manager_failure.html', reason=error_reasons[retval - 1])
    else:
        return render_template('/TokenManager/token_manager_token_id_input.html')


# Get token details page
@app.route('/TokenManager/GetTokenDetails', methods=['GET', 'POST'])
def token_manager_get_token_details():
    if request.method == 'POST':
        # Get the token id
        token_id = request.form['TokenID']
        # Get the token details
        token_details = TokenManager.get_token_details(pysql, token_id)
        return render_template('/TokenManager/token_manager_get_token_details.html', token_details=token_details)
    else:
        return render_template('/TokenManager/token_manager_token_id_input.html')


# Add token page
@app.route('/TokenManager/AddToken', methods = ['GET', 'POST'])
def token_manager_add_token():
    # Add new token to the existing list
    new_token_id = TokenManager.add_token(pysql)

    # If error
    if new_token_id == 1:
        return render_template('/TokenManager/token_manager_failure.html', reason="New token cannot be added")
    # If no error
    else:
        return render_template('/TokenManager/token_manager_success.html', result="Token {} added successfully".format(new_token_id))


# Remove token page
@app.route('/TokenManager/RemoveToken', methods = ['GET', 'POST'])
def token_manager_remove_token():
    if request.method == 'POST':
        # Get the token id
        token_id = request.form['TokenID']
        # Remove the token
        retval = TokenManager.remove_token(pysql, token_id)
        # If no error
        if retval == 0:
            return render_template('/TokenManager/token_manager_success.html', result="Removed token successfully")

        # If error
        error_reasons = ["Token already has products. Please remove them before proceeding.",
                         "Token is already assigned. Please desassign it to continue.",
                         "Token not found. Please check Token ID and continue"]
        return render_template('/TokenManager/token_manager_failure.html', reason=error_reasons[retval - 1])
    else:
        return render_template('/TokenManager/token_manager_token_id_input.html')


# Counter operator page
@app.route('/CounterOperator', methods = ['GET', 'POST'])
def counter_operator():
    if request.method == 'POST':
        # Get the list of options
        options = ["AddProductsToToken",
                   "AddInventoryToCounter",
                   "AddTokenToCounter"]

        # Check if a option is asserted
        for option in options:
            if option in request.form:
                return redirect("/CounterOperator/" + option)
    else:
        return render_template('/CounterOperator/counter_operator.html')


# Add products from counter to token page
@app.route('/CounterOperator/AddProductsToToken', methods=['GET', 'POST'])
def counter_operator_add_products_to_token():
    if request.method == 'POST':
        # Get the token details and product details
        token_id = request.form['TokenID'].strip()
        product_id = request.form['ProductID'].strip()
        quantity = request.form['Quantity'].strip()

        # Check if quantity is specified
        if not quantity:
            return redirect('/CounterOperator/AddProductsToToken')

        # Convert string to float
        quantity = float(quantity)

        # Add product quantity from counter to token
        retval = CounterManager.add_counter_to_token(pysql, token_id, product_id, quantity)

        # If no error
        if retval == 0:
            return render_template('/CounterOperator/counter_operator_success.html', result="Products added successfully to token")

        # If error
        error_reasons = ["Token not found or is not assigned.",
                         "Quantity not valid",
                         "Product not found in inventory",
                         "Quantity not sufficient in inventory"]
        return render_template('/CounterOperator/counter_operator_failure.html', reason=error_reasons[retval - 1])
    else:
        return render_template('/CounterOperator/counter_operator_add_products_to_token.html')


# Add products from inventory to counter
@app.route('/CounterOperator/AddInventoryToCounter', methods=['GET', 'POST'])
def counter_operator_add_inventory_to_counter():
    if request.method == 'POST':
        # Get the product and quantity to be transferred
        product_id = request.form['ProductID'].strip()
        quantity = request.form['Quantity'].strip()

        # Check if quantity is specified
        if not quantity:
            return redirect('/CounterOperator/Add_Inventory_To_Counter')

        # Convert string to float
        quantity = float(quantity)

        # Add the product quantity from inventory to counter
        retval = CounterManager.add_inventory_to_counter(pysql, product_id, quantity)

        # If no error
        if retval == 0:

            return render_template('/CounterOperator/counter_operator_success.html', result="Products transferred successfully from inventory to counter")

        # If error
        error_reasons = ["Quantity not valid.",
                         "Product not found in inventory",
                         "Quantity in warehouse not sufficient"]
        return render_template('/CounterOperator/counter_operator_failure.html', reason=error_reasons[retval - 1])
    else:
        return render_template('/CounterOperator/counter_operator_add_inventory_to_counter.html')

# Add products from token to counter
@app.route('/CounterOperator/AddTokenToCounter', methods=['GET', 'POST'])
def counter_operator_add_token_to_counter():
    if request.method == 'POST':
        # Get the token and product details
        token_id = request.form['TokenID'].strip()
        product_id = request.form['ProductID'].strip()

        # Remove product from token and add to the counter
        retval = CounterManager.add_token_to_counter(pysql, token_id, product_id)

        # If no error
        if retval == 0:
            return render_template('/CounterOperator/counter_operator_success.html', result="Product returned successfully from token to counter")

        # If no error
        error_reasons = ["Product not present in selected Token"]
        return render_template('/CounterOperator/counter_operator_failure.html', reason=error_reasons[retval - 1])
    else:
        return render_template('/CounterOperator/counter_operator_add_token_to_counter.html')


@app.route('/BillDesk', methods=['GET', 'POST'])
def bill_desk_home():
    if request.method == 'POST':
        if 'generate_invoice' in request.form:
            return redirect('BillDesk/GenerateInvoice')
        elif 'update_gst_cgst' in request.form:
            return redirect('BillDesk/UpdateCgstGst')
        elif 'additional_discount' in request.form:
            return redirect('BillDesk/AdditionalDiscount')
        elif 'view_invoice_details' in request.form:
            return redirect('BillDesk/ViewInvoice')
        elif 'date_wise_invoice' in request.form:
            return redirect('BillDesk/DateWiseInvoice')
    else:
        return render_template('/BillDesk/bill_desk_home.html')


@app.route('/BillDesk/GenerateInvoice', methods=['GET', 'POST'])
def generate_invoice():
    if request.method == 'POST':
        print("Yes")
    else:
        return render_template('/BillDesk/generate_invoice_home.html')

@app.route('/BillDesk/AdditionalDiscount', methods=['GET', 'POST'])
def additional_discount():
    if request.method == 'POST':
        invoice_id = request.form['invoice_id']
        add_discount = Decimal(request.form['add_discount'])
        add_discount = round(add_discount, 3)
        retval = InvoiceManager.give_additional_discount(pysql, invoice_id, add_discount)
        
        if retval == 0:
            return render_template('/BillDesk/success_add_discount.html')

        error_reasons = ['This Invoice-ID does not exist', 'The discount given is negative']

        return render_template('/BillDesk/bill_desk_failure_add_discount.html', reason = error_reasons[retval])

    else:
        return render_template('/BillDesk/bill_desk_additional_discount.html')


@app.route('/BillDesk/ViewInvoice', methods=['GET', 'POST'])
def view_invoice_details():
    if request.method == 'POST':
        invoice_id = request.form['invoice_id']
    else:
        return render_template('/BillDesk/view_invoice_details_home.html')


@app.route('/BillDesk/DateWiseInvoice', methods=['GET', 'POST'])
def date_wise_invoice():
    if request.method == 'POST':
        print("Yes")
    else:
        return render_template('/BillDesk/date_wise_invoice_home.html')

if __name__ == "__main__" :
    #serve(app, port = 5000, host = '0.0.0.0')
    app.run(debug=True)
