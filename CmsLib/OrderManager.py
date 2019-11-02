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
    # @param products_quantities List of ProductIDs and Quantities (list of tuples)
    # @retval order_id The OrderId for the current order (string)
    @staticmethod
    def place_order(pysql, products_quantities):
        # Fetch the global variables
        global next_order_id
        global next_order_id_read

        # Initialize the next order id
        if not next_order_id_read:
            sql_stmt = "SELECT COUNT(*) \
                        FROM `Orders`"
            pysql.run(sql_stmt)
            next_order_id = pysql.get_results()[0][0]
            next_order_id_read = 1

        # Create the order id
        order_id = "ORD-" + format(next_order_id, "010d")
        next_order_id += 1

        try:
            # Create the new order
            sql_stmt = "INSERT INTO `Orders` (`OrderID`, `OrderDate`) \
                        VALUES (%s, (SELECT CURRENT_TIMESTAMP))"
            pysql.run(sql_stmt, (order_id, ))

            # Add the products for the order
            sql_stmt = "INSERT INTO `OrdersOfProducts` \
                        VALUES ('{}', %s, %s)".format(order_id)
            pysql.run_many(sql_stmt, products_quantities)

            # Commit the changes
            pysql.commit()

            # Return the currently created order id
            return order_id
        except:
            # Restore the order number
            next_order_id -= 1
            # Print error
            pysql.print_error()
            # Revert the changes
            pysql.rollback()

    # @brief This method gets the delivery status of the specified order
    # @param pysql PySql object
    # @param order_id The OrderID to check for (string)
    # @retval (0, 0) The order is not delivered and is not cancelled
    # @retval (0, 1) The order is not delivered and is cancelled
    # @retval (1, 0) The order is delivered and is not cancelled
    # @retval (1, 1) OrderID not found
    @staticmethod
    def get_order_status(pysql, order_id):
        try:
            # Get the delivered status of the order
            sql_stmt = "SELECT `Delivered?`, `Cancelled?` \
                        FROM `Orders` \
                        WHERE `OrderID` = %s"
            pysql.run(sql_stmt, (order_id, ))

            # Return the boolean tuple
            return pysql.get_results()[0]
        except IndexError:
            return (1, 1)
        except:
            # Print error
            pysql.print_error()

    # @brief This method cancels an order only if it is not delivered
    #        and not already cancelled
    # @param pysql PySql object
    # @param order_id The OrderID to check for (string)
    @staticmethod
    def cancel_order(pysql, order_id):
        # Get the order status
        is_delivered, is_cancelled = OrderManager.get_order_status(pysql, order_id)

        # If order is already delivered
        if is_delivered:
            return

        # If it is already cancelled
        if is_cancelled:
            return

        try:
            # Set the status of order as cancelled and delivered as NULL
            sql_stmt = "UPDATE `Orders` \
                        SET `Delivered?` = 0, \
                            `Cancelled?` = 1 \
                        WHERE `OrderID` = %s"
            pysql.run(sql_stmt, (order_id, ))

            # Commit the changes
            pysql.commit()
        except:
            # Print error
            pysql.print_error()
            # Revert the changes
            pysql.rollback()

    # @brief This method receives the order i.e. updates the stored
    #        inventory quantities and marks the order as delivered
    # @param pysql PySql object
    # @param order_id OrderID of the order received (string)
    @staticmethod
    def receive_order(pysql, order_id):
        # Get the order status
        is_delivered, is_cancelled = OrderManager.get_order_status(pysql, order_id)

        # If order is already delivered
        if is_delivered:
            return

        # If it is already cancelled
        if is_cancelled:
            return

        try:
            # Get all the products and quantities of the given order
            sql_stmt = "SELECT `Quantity`, `ProductID` \
                        FROM `OrdersOfProducts` \
                        WHERE `OrderID` = %s"
            pysql.run(sql_stmt, (order_id, ))
            quantities_products = pysql.get_results()

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
            for pair in quantities_products:
                InventoryManager.log_transaction(pysql, "INVENTORY_ADD", pair[1], pair[0])

            # Commit the changes
            pysql.commit()
        except:
            # Print error
            pysql.print_error()
            # Revert the changes
            pysql.rollback()

    # @brief This function returns all the order till date
    # @param pysql PySql object
    # @retval List of tuples of format (OrderID, OrderDate, Delivered?, Cancelled?)
    @staticmethod
    def get_orders(pysql):
        try:
            # Get all the orders
            sql_stmt = "SELECT * \
                        FROM `Orders`"
            pysql.run(sql_stmt)

            # Return the result
            return pysql.get_results()
        except:
            # Print error
            pysql.print_error()

    # @brief This function returns the products in the orders
    # @param pysql PySql object
    # @param order_id OrderId to get the details of
    # @retval List of tuples of format (ProductID, Name, Quantity, UnitType)
    @staticmethod
    def get_order_details(pysql, order_id):
        try:
            # Get the products in the given order
            sql_stmt = "SELECT `ProductID`, `Name`, `Quantity`, `UnitType` \
                        FROM `OrdersOfProducts` JOIN `Products` USING (`ProductID`) \
                        WHERE `OrderID` = %s"
            pysql.run(sql_stmt, (order_id, ))

            # Return the result
            return pysql.get_results()
        except:
            # Print error
            pysql.print_error()

    # @brief This function returns all the order till between the two dates
    # @param pysql PySql object
    # @retval List of tuples of format (OrderID, OrderDate, Delivered?, Cancelled?)
    @staticmethod
    def get_orders_between_date(pysql, start_date, end_date):
        try:
            # Get all the orders between the given date
            sql_stmt = "SELECT * \
                        FROM `Orders` \
                        WHERE DATE(`OrderDate`) BETWEEN %s AND %s"
            pysql.run(sql_stmt, (start_date, end_date))

            # Return the result
            return pysql.get_results()
        except:
            # Print error
            pysql.print_error()
