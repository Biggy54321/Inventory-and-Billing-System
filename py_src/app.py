# Import the required libraries
from flask import Flask, render_template, request, redirect, session
from flask_session import Session
import sys
from decimal import Decimal
import pdfkit
import flask_weasyprint
sys.path.append('../')
from CmsLib import *

# Create the flask object for server side programming
app = Flask(__name__ ,
            template_folder = '../html_src/',
            static_folder = '../html_src/')

app.secret_key = "abc"

invoice_id_global = ""

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
                return redirect("/InventoryManager/" + option)

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
        gst = float(request.form['SGST'].strip())
        cgst = float(request.form['CGST'].strip())
        current_discount = float(request.form['Discount'].strip())

        # Add the product
        retval = ProductManager.add_product(pysql, product_id, name, description, unit_price, unit_type, gst, cgst, current_discount)

        # If no errors
        if retval == 0:
            return render_template('InventoryManager/inventory_manager_success.html', result='Product Added successfully')

        # If errors
        error_reasons = ["Product ID already used.",
                         "Unit price not valid.,",
                         "Unit type not valid.",
                         "SGST or CGST not valid",
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

            # If no error
            if retval not in [1, 2]:
                return render_template('/InventoryManager/inventory_manager_success.html', result="Order {} Placed Successfully".format(retval))
            # If error
            error_reasons = ["Details of one of the products ordered not found.",
                             "One of the quantities in the order is not valid"]
            return render_template('/InventoryManager/inventory_manager_failure.html', reason=error_reasons[retval - 1])
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
    # If no items
    if not inventory:
        return render_template('/InventoryManager/inventory_manager_alert.html', result="Inventory is empty")
    else:
        return render_template('/InventoryManager/inventory_manager_view_inventory.html', inventory = inventory)


# View products page
@app.route('/InventoryManager/ViewProducts', methods = ['GET', 'POST'])
def inventory_manager_view_products():
    # Get the product details
    products = ProductManager.get_all_products(pysql)
    # If no products
    if not products:
        return render_template('/InventoryManager/inventory_manager_alert.html', result="No Products found")
    return render_template('/InventoryManager/inventory_manager_view_products.html', products=products)


# Order details page
@app.route('/InventoryManager/OrderDetails', methods = ['GET', 'POST'])
def inventory_manager_order_details():
    if request.method == 'POST':
        # Get the order id
        order_id = request.form['OrderID'].strip()
        # Get the order details
        order_status, order_details = OrderManager.get_order_details(pysql, order_id)
        if order_status and order_details:
            return render_template('/InventoryManager/inventory_manager_order_details_result.html', order_status=order_status, order_details=order_details)
        else:
            return render_template('InventoryManager/inventory_manager_failure.html', reason="Order ID not found")
    else:
        return render_template('/InventoryManager/inventory_manager_order_details.html')


# Orders between dates page
@app.route('/InventoryManager/OrdersBetweenDates', methods = ['GET', 'POST'])
def inventory_manager_orders_between_dates():
    if request.method == 'POST':
        # Get the start and end date
        from_date, to_date = request.form['FromDate'], request.form['ToDate']
        # Get the order details of those orders
        orders = OrderManager.get_orders_between_date(pysql, from_date, to_date)
        # If no orders
        if not orders:
            return render_template('InventoryManager/inventory_manager_alert.html', result="No orders found")
        else:
            return render_template('/InventoryManager/inventory_manager_orders_between_dates_result.html', from_date=from_date, to_date=to_date, orders=orders)
    else:
        return render_template('/InventoryManager/inventory_manager_orders_between_dates.html')


# Transaction log page
@app.route('/InventoryManager/TransactionLog', methods = ['GET', 'POST'])
def inventory_manager_transaction_log():
    # Get the transactions
    transactions = InventoryManager.get_transactions(pysql)
    # If no transactions
    if not transactions:
        return render_template('InventoryManager/inventory_manager_alert.html', result="No transactions found")
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
        # If product not found
        if not product_id:
            return render_template('InventoryManager/inventory_manager_failure.html', reason="Product not found")

        transactions = InventoryManager.get_transactions_of_product_by_date(pysql, product_id, on_date)

        # If no transactions found
        if not transactions:
            return render_template('InventoryManager/inventory_manager_alert.html', result="No transactions found")

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
    # If no statuses found
    if not statuses:
        return render_template('/TokenManager/token_manager_alert.html', result="No tokens found")
    else:
        return render_template('/TokenManager/token_manager_token_statuses.html', statuses=statuses)

# Get token page
@app.route('/TokenManager/GetToken', methods = ['GET', 'POST'])
def token_manager_get_token():
    # Get the token from the available tokens
    token_id = TokenManager.get_token(pysql)
    # If no token found
    if token_id is None:
        return render_template('/TokenManager/token_manager_failure.html', reason="Token not available")
    else:
        return render_template('/TokenManager/token_manager_success.html', result="Token {} assigned".format(token_id))

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

        if not token_details:
            return render_template('TokenManager/token_manager_alert.html', result="No products are bagged by this token")
        else:
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
            return redirect('/CounterOperator/counter_operator_alert.html', result="Quantity cannot be empty")

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
            return redirect('/CounterOperator/counter_operator_alert.html', result="Quantity cannot be empty")

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

# Bill desk page
@app.route('/BillDesk', methods=['GET', 'POST'])
def bill_desk():
    if request.method == 'POST':
        # Get the options
        options = ["GenerateInvoice",
                   "AdditionalDiscount",
                   "ViewInvoice",
                   "DateWiseInvoice"]

        # Check if an option is asserted
        for option in options:
            if option in request.form:
                return redirect("/BillDesk/" + option)
    else:
        return render_template('/BillDesk/bill_desk.html')

# Generate invoice page
@app.route('/BillDesk/GenerateInvoice', methods=['GET', 'POST'])
def generate_invoice():
    # Get all token statuses
    tokens = TokenManager.get_all_tokens_status(pysql)
    # Get the token ids
    tokens = [each[0] for each in tokens]

    if request.method == 'POST':
        # Get the token ids
        token_ids = request.form.getlist("Select[]")

        # Check if tokens are selected
        if not token_ids:
            return render_template('/BillDesk/bill_desk_alert.html', result="No tokens selected")

        # Get the current discount and payment mode
        payment_mode = request.form['PaymentMode']

        # Generate the invoice
        retval = InvoiceManager.generate_invoice(pysql, token_ids, payment_mode)

        # If no errors
        if retval not in [1, 2, 3]:
            return render_template('/BillDesk/bill_desk_success.html', result="Invoice {} generated successfully".format(retval))

        # If errors
        error_reason = ['One of the tokens is not found or not assigned',
                        'No products to be billed',
                        'Payment mode incorrect']
        return render_template('/BillDesk/bill_desk_failure.html', reason=error_reason[retval - 1])

    else:
        return render_template('/BillDesk/bill_desk_generate_invoice.html', tokens=tokens)

# Print invoice page
@app.route('/BillDesk/PrintInvoiceCopy', methods=['GET', 'POST'])
def print_invoice_copy():
    # Get the invoice details
    invoice_id = invoice_id_global
    invoice_parameters, invoice_details = InvoiceManager.get_invoice_details(pysql, invoice_id)

    # Check if we have a result
    if invoice_parameters and invoice_details:
        # Extract the parameter information
        timestamp = invoice_parameters[1]
        invoice_total = invoice_parameters[2]
        discount_given = invoice_parameters[3]
        payment_mode = invoice_parameters[4]
        # Initialize the empty invoice
        invoice = []
        sgst_total = 0
        cgst_total = 0

        # Process the invoice information
        for product_id, name, quantity, unit_price, sgst, cgst, discount in invoice_details:
            # Get the product id and name
            product_id_name = "{} ({})".format(name, product_id)
            # Get the appropriate unitprice subtracting the discount
            unit_price_with_discount = unit_price * (1 - discount / 100)
            # As unit price is including gst get the product total including gst
            product_total_with_gst = round(quantity * unit_price_with_discount, 2)
            # Get the product total without gst
            product_total_without_gst = round(product_total_with_gst / (1 + (sgst + cgst) / 100), 2)
            # Get the sgst and cgst amounts
            product_sgst = round(product_total_without_gst * sgst / 100, 2)
            product_cgst = round(product_total_without_gst * cgst / 100, 2)
            # Update the total sgst, cgst and products
            sgst_total += product_sgst
            cgst_total += product_cgst
              # Convert sgst and cgst to strings
            product_sgst = "{} @ {}%".format(product_sgst, sgst)
            product_cgst = "{} @ {}%".format(product_cgst, cgst)

            invoice.append((product_id_name, quantity, unit_price_with_discount, product_sgst, product_cgst, product_total_with_gst))

        return render_template('/BillDesk/bill_desk_print_invoice.html', invoice_id=invoice_id, timestamp=timestamp, discount_given=discount_given, payment_mode=payment_mode, invoice=invoice, sgst_total=sgst_total, cgst_total=cgst_total, invoice_total=invoice_total)

# Print Invoice method
@app.route('/BillDesk/PrintInvoice')
def print_invoice():
    pdfkit.from_url('127.0.0.1:5000/BillDesk/PrintInvoiceCopy', '../Invoices/current_invoice.pdf')
    return "nothing"

# Give additional discount page
@app.route('/BillDesk/AdditionalDiscount', methods=['GET', 'POST'])
def additional_discount():
    if request.method == 'POST':
        # Get the invoice id and discount
        invoice_id = request.form['InvoiceID']
        discount = Decimal(request.form['DiscountGiven'])
        discount = round(discount, 3)

        # Give additional discount
        retval = InvoiceManager.give_additional_discount(pysql, invoice_id, discount)

        # If no errors
        if retval == 0:
            return render_template('/BillDesk/bill_desk_success.html', result="Discount given successfully")

        # If errors
        error_reasons = ['This Invoice ID does not exist',
                         'The discount given is negative']
        return render_template('/BillDesk/bill_desk_failure.html', reason=error_reasons[retval - 1])
    else:
        return render_template('/BillDesk/bill_desk_additional_discount.html')

# View invoice details page
@app.route('/BillDesk/ViewInvoice', methods=['GET', 'POST'])
def view_invoice_details():
    if request.method == 'POST':
        # Get the invoice id
        invoice_id = request.form['InvoiceID']
        global invoice_id_global
        invoice_id_global = invoice_id

        # Get the invoice details
        invoice_parameters, invoice_details = InvoiceManager.get_invoice_details(pysql, invoice_id)

        # Check if we have a result
        if invoice_parameters and invoice_details:
            # Extract the parameter information
            timestamp = invoice_parameters[1]
            invoice_total = invoice_parameters[2]
            discount_given = invoice_parameters[3]
            payment_mode = invoice_parameters[4]
            # Initialize the empty invoice
            invoice = []
            sgst_total = 0
            cgst_total = 0

            # Process the invoice information
            for product_id, name, quantity, unit_price, sgst, cgst, discount in invoice_details:
                # Get the product id and name
                product_id_name = "{} ({})".format(name, product_id)
                # Get the appropriate unitprice subtracting the discount
                unit_price_with_discount = unit_price * (1 - discount / 100)
                # As unit price is including gst get the product total including gst
                product_total_with_gst = round(quantity * unit_price_with_discount, 2)
                # Get the product total without gst
                product_total_without_gst = round(product_total_with_gst / (1 + (sgst + cgst) / 100), 2)
                # Get the sgst and cgst amounts
                product_sgst = round(product_total_without_gst * sgst / 100, 2)
                product_cgst = round(product_total_without_gst * cgst / 100, 2)
                # Update the total sgst, cgst and products
                sgst_total += product_sgst
                cgst_total += product_cgst
                # Convert sgst and cgst to strings
                product_sgst = "{} @ {}%".format(product_sgst, sgst)
                product_cgst = "{} @ {}%".format(product_cgst, cgst)

                invoice.append((product_id_name, quantity, unit_price_with_discount, product_sgst, product_cgst, product_total_with_gst))

            return render_template('/BillDesk/bill_desk_view_invoice_details_result.html', invoice_id=invoice_id, timestamp=timestamp, discount_given=discount_given, payment_mode=payment_mode, invoice=invoice, sgst_total=sgst_total, cgst_total=cgst_total, invoice_total=invoice_total)
        else:
            return render_template('/BillDesk/bill_desk_alert.html', result="Invoice details not found")
    else:
        return render_template('/BillDesk/bill_desk_view_invoice_details.html')

# Date wise invoices page
@app.route('/BillDesk/DateWiseInvoice', methods=['GET', 'POST'])
def date_wise_invoice():
    if request.method == 'POST':
        # Get the date
        on_date = request.form['OnDate']
        # Get the invoices on the given date
        invoices = InvoiceManager.get_invoices_by_date(pysql, on_date)

        if not invoices:
            return render_template('/BillDesk/bill_desk_alert.html', result="No invoices found on {}".format(on_date))
        else:
            return render_template('/BillDesk/bill_desk_date_wise_invoice_result.html', invoices=invoices)
    else:
        return render_template('/BillDesk/bill_desk_date_wise_invoice.html')

if __name__ == "__main__" :
    #serve(app, port = 5000, host = '0.0.0.0')
    app.run(debug=True)
