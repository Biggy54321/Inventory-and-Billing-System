# Import the required modules
from CmsLib.InventoryManager import *

# This variable stores the next OrderID integer
next_order_id = None
# This variable indicates whether the next_order_id has been initialized
next_order_id_read = 0

# @brief This class is used to handle the order management in CMS
# @note  There is not need to create an object of this class as all
#        methods in this class are static
class OrderManager:

    # @brief This method places an order of the requested products and
    #        adds the product details of the order
    # @param pysql PySql object
    # @param products_quantities (ProductID, Quantity) (list of tuples)
    # @retval order_id The OrderId (string)
    @staticmethod
    def __place_order(pysql, products_quantities):
        # Fetch the global variables
        global next_order_id
        global next_order_id_read

        # Initialize the next order id
        if not next_order_id_read:
            sql_stmt = "SELECT COUNT(*) \
                        FROM `Orders`"
            pysql.run(sql_stmt)
            next_order_id = pysql.scalar_result
            next_order_id_read = 1

        # Create the order id
        order_id = "ORD-" + format(next_order_id, "010d")

        # Create the new order
        sql_stmt = "INSERT INTO `Orders` (`OrderID`, `OrderDate`) \
                    VALUES (%s, (SELECT CURRENT_TIMESTAMP))"
        pysql.run(sql_stmt, (order_id, ))

        # Add the products for the order
        sql_stmt = "INSERT INTO `OrdersOfProducts` \
                    VALUES ('{}', %s, %s)".format(order_id)
        pysql.run_many(sql_stmt, products_quantities)

        # Increment the global order id count
        next_order_id += 1

        # Return the currently created order id
        return order_id

    # @brief This method gets the delivery status of the specified order
    # @param pysql PySql object
    # @param order_id The OrderID (string)
    # @retval (0, 0) Not delivered not cancelled
    # @retval (0, 1) Not delivered but cancelled
    # @retval (1, 0) Delivered and not cancelled
    # @retval (1, 1) OrderID not found
    @staticmethod
    def __get_order_status(pysql, order_id):
        # Get the delivered status of the order
        sql_stmt = "SELECT `Delivered?`, `Cancelled?` \
                    FROM `Orders` \
                    WHERE `OrderID` = %s"
        pysql.run(sql_stmt, (order_id, ))

        # Get order status
        order_status = pysql.result[0]

        # If order status not found
        if not order_status:
            return (1, 1)

        return order_status

    # @brief This method cancels an order only if it is not delivered
    #        and not already cancelled
    # @param pysql PySql object
    # @param order_id OrderID (string)
    @staticmethod
    def __cancel_order(pysql, order_id):
        # Get the order status
        is_delivered, is_cancelled = OrderManager.get_order_status(pysql, order_id)

        # If order is already delivered or cancelled
        if is_delivered or is_cancelled:
            return

        # Set the status of order as cancelled and delivered as NULL
        sql_stmt = "UPDATE `Orders` \
                    SET `Delivered?` = 0, \
                        `Cancelled?` = 1 \
                    WHERE `OrderID` = %s"
        pysql.run(sql_stmt, (order_id, ))

    # @brief This method receives the order i.e. updates the stored
    #        inventory quantities and marks the order as delivered
    # @param pysql PySql object
    # @param order_id OrderID of the order received (string)
    @staticmethod
    def __receive_order(pysql, order_id):
        # Get the order status
        is_delivered, is_cancelled = OrderManager.get_order_status(pysql, order_id)

        # If order is already delivered or cancelled
        if is_delivered or is_cancelled:
            return

        # Get all the products and quantities of the given order
        sql_stmt = "SELECT `Quantity`, `ProductID` \
                    FROM `OrdersOfProducts` \
                    WHERE `OrderID` = %s"
        pysql.run(sql_stmt, (order_id, ))
        quantities_products = pysql.result

        # Update the quantities of all the products that are already present
        sql_stmt = "UPDATE `Inventory` \
                    SET `StoredQuantity` = `StoredQuantity` + %s \
                    WHERE `ProductID` = %s"
        pysql.run_many(sql_stmt, quantities_products)

        # Insert the products in the inventory if not present by default
        # (set threshold to 10 percent of the order quantity)
        sql_stmt = "INSERT INTO `Inventory` \
                    (SELECT `ProductID`, `Quantity`, 0.0, Quantity * 0.1 \
                     FROM `OrdersOfProducts` \
                     WHERE `OrderID` = %s and `ProductID` NOT IN (SELECT `ProductID` \
                                                                  FROM `Inventory`))"
        pysql.run(sql_stmt, (order_id, ))

        # Mark the order delivered status as true
        sql_stmt = "UPDATE `Orders` \
                    SET `Delivered?` = true \
                    WHERE `OrderID` = %s"
        pysql.run(sql_stmt, (order_id, ))

        # Log the transactions
        for quantity, product_id in quantities_products:
            InventoryManager.log_transaction(pysql, "INVENTORY_ADD", product_id, quantity)

    # @brief This function returns all the order till date
    # @param pysql PySql object
    # @retval (OrderID, OrderDate, Delivered?, Cancelled?) (list of tuples)
    @staticmethod
    def __get_orders(pysql):
        # Get all the orders
        sql_stmt = "SELECT * \
                    FROM `Orders`"
        pysql.run(sql_stmt)

        # Get the result
        orders = pysql.result

        return orders

    # @brief This function returns the products in the orders
    # @param pysql PySql object
    # @param order_id OrderId
    # @retval (ProductID, Name, Quantity, UnitType) (list of tuples)
    @staticmethod
    def __get_order_details(pysql, order_id):
        # Get order status
        sql_stmt = "SELECT * \
                    FROM `Orders` \
                    WHERE `OrderID` = %s"
        pysql.run(sql_stmt, (order_id, ))
        order_status = pysql.result[0]

        # Get the products in the given order
        sql_stmt = "SELECT `ProductID`, `Name`, `Quantity`, `UnitType` \
                    FROM `OrdersOfProducts` JOIN `Products` USING (`ProductID`) \
                    WHERE `OrderID` = %s"
        pysql.run(sql_stmt, (order_id, ))
        order_details = pysql.result

        # Return the result
        return order_status, order_details

    # @brief This function returns all the order till between the two dates
    # @param pysql PySql object
    # @param start_date From Date (string of format "YYYY-MM-DD")
    # @param end_date To Date (string of format "YYYY-MM-DD")
    # @retval (OrderID, OrderDate, Delivered?, Cancelled?) (list of tuples)
    @staticmethod
    def __get_orders_between_date(pysql, start_date, end_date):
        # Get all the orders between the given date
        sql_stmt = "SELECT * \
                    FROM `Orders` \
                    WHERE DATE(`OrderDate`) BETWEEN %s AND %s"
        pysql.run(sql_stmt, (start_date, end_date))

        # Get the result
        orders = pysql.result

        return orders

    # @ref __place_order
    @staticmethod
    def place_order(pysql, products_quantities):
        return pysql.run_transaction(OrderManager.__place_order,
                                     products_quantities)
    # @ref __get_order_status
    @staticmethod
    def get_order_status(pysql, order_id):
        return pysql.run_transaction(OrderManager.__get_order_status,
                                     order_id,
                                     commit = False)
    # @ref __cancel_order
    @staticmethod
    def cancel_order(pysql, order_id):
        return pysql.run_transaction(OrderManager.__cancel_order,
                                     order_id)
    # @ref __receive_order
    @staticmethod
    def receive_order(pysql, order_id):
        return pysql.run_transaction(OrderManager.__receive_order,
                                     order_id)

    # @ref __get_orders
    @staticmethod
    def get_orders(pysql):
        return pysql.run_transaction(OrderManager.__get_orders,
                                     commit = False)

    # @ref __get_order_details
    @staticmethod
    def get_order_details(pysql, order_id):
        return pysql.run_transaction(OrderManager.__get_order_details,
                                     order_id,
                                     commit = False)

    # @ref __get_orders_between_date
    @staticmethod
    def get_orders_between_date(pysql, start_date, end_date):
        return pysql.run_transaction(OrderManager.__get_orders_between_date,
                                     start_date,
                                     end_date,
                                     commit = False)
