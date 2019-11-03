# This variable stores the next TransactionID integer
next_transaction_id = None
# This variable indicates whether the next_transaction_id has been initialized
next_transaction_id_read = 0

# @brief This class is used to handle the inventory management in CMS
# @note  There is not need to create an object of this class as all
#        methods in this class are static
class InventoryManager:

    # @brief This method returns the displayed (counter) quantity of the
    #        specified product
    # @param pysql PySql object
    # @param product_id ProductID (string)
    # @retval integer When quantity of product is found
    # @retval None For product not found
    @staticmethod
    def get_displayed_quantity(pysql, product_id):
        # Initialize the pysql object
        pysql.init()

        # Get the displayed quantity of the product
        sql_stmt = "SELECT `DisplayedQuantity` \
                    FROM `Inventory` \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (product_id, ))

        # Return the quantity
        quantity = pysql.scalar_result

        # Deinitialize the pysql object
        pysql.deinit()

        return quantity

    # @brief This method returns the stored (local inventory) quantity of the
    #        specified product
    # @param pysql PySql object
    # @param product_id ProductID (string)
    # @retval integer When quantity of product is found
    # @retval None For product not found
    @staticmethod
    def get_stored_quantity(pysql, product_id):
        # Initialize the pysql object
        pysql.init()

        # Get the stored quantity of the product
        sql_stmt = "SELECT `StoredQuantity` \
                    FROM `Inventory` \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (product_id, ))

        # Return the quantity
        quantity = pysql.scalar_result

        # Deinitialize the pysql object
        pysql.deinit()

        return quantity

    # @brief This method checks if the specified product stored
    #        is below the set threshold
    # @param pysql PySql Object
    # @param product_id ProductID (string)
    # @retval 1 If the product is below threshold
    # @retval 0 If the product is not below threshold
    # @retval None For product not found
    @staticmethod
    def is_below_threshold(pysql, product_id):
        # Initialize the pysql object
        pysql.init()

        # Check if the stored quantity is less than equal the store threshold
        sql_stmt = "SELECT `StoredQuantity` <= `StoreThreshold` \
                    FROM `Inventory` \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (product_id, ))

        # Return boolean value
        is_below = pysql.scalar_result

        # Deinitialize the pysql object
        pysql.deinit()

        return is_below

    # @brief This method updates the threshold value of the specified product
    # @param pysql PySql object
    # @param product_id ProductID (string)
    # @param threshold Threshold (float)
    @staticmethod
    def update_threshold(pysql, product_id, threshold):
        # Initialize the pysql object
        pysql.init()

        # Set the value of threshold to the given argument
        sql_stmt = "UPDATE `Inventory` \
                    SET `StoreThreshold` = %s \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (threshold, product_id))

        # Commit the changes
        pysql.commit()

        # Deinitialize the pysql object
        pysql.deinit()

    # @brief This method removes the specified product quantity from the
    #        stored (local inventory) quantity and logs the transaction
    # @param pysql PySql object
    # @param product_id ProductID (string)
    # @param threshold Threshold (float)
    @staticmethod
    def sub_product_from_inventory(pysql, product_id, quantity):
        # Initialize the pysql object
        pysql.init()

        # Subtract the specified quantity of the product
        sql_stmt = "UPDATE `Inventory` \
                    SET `StoredQuantity` = `StoredQuantity` - %s \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (quantity, product_id))

        # Log the transaction
        InventoryManager.log_transaction(pysql, "INVENTORY_SUB", product_id, quantity)

        # Commit the changes
        pysql.commit()

        # Deinitialize the pysql object
        pysql.deinit()

    # @brief This method logs the transaction of a specified quantity
    #        of the product depending on the transaction type
    # @param pysql PySql object
    # @param transaction_type TransactionType (string enum)
    # @param product_id ProductID (string)
    # @param quantity Product quantity (float)
    @staticmethod
    def log_transaction(pysql, transaction_type, product_id, quantity):
        # Fetch the global variables
        global next_transaction_id
        global next_transaction_id_read

        # Initialize the pysql object
        pysql.init()

        # Read the next transaction id if already filled with data
        if not next_transaction_id_read:
            sql_stmt = "SELECT COUNT(*) \
                        FROM `InventoryTransactions`"
            pysql.run(sql_stmt)
            next_transaction_id = pysql.scalar_result
            next_transaction_id_read = 1

        # Get the string transaction id
        transaction_id = "TRC-" + format(next_transaction_id, "010d")

        # Enter the transaction in the inventory transactions
        sql_stmt = "INSERT INTO `InventoryTransactions` \
                    VALUES (%s, %s, %s, %s, (SELECT CURRENT_TIMESTAMP))"
        pysql.run(sql_stmt, (transaction_id, transaction_type, product_id, quantity))

        # Increment the global transaction id count
        next_transaction_id += 1

        # Deinitialize the pysql object
        pysql.deinit()

    # @brief This method returns the details of all the products
    #        in the inventory
    # @param pysql PySql object
    # @retval (ProductID, Name, StoredQuantity, DisplayedQuantity, StoreThreshold, UnitType) (list of tuples)
    @staticmethod
    def get_inventory_details(pysql):
        # Initialize the pysql object
        pysql.init()

        # Get the product details of othe entire inventory
        sql_stmt = "SELECT `ProductID`, `Name`, `StoredQuantity`, `DisplayedQuantity`, `StoreThreshold`, `UnitType` \
                    FROM `Products` JOIN `Inventory` USING (`ProductID`)"
        pysql.run(sql_stmt)

        # Get the results
        inventory_details = pysql.result

        # Deinitialize the pysql object
        pysql.deinit()

        return inventory_details

    # @brief This method returns the all transactions
    # @param pysql PySql object
    # @retval (TransactionID, ProductID, Name, TransactionType, Quantity, UnitType, Timestamp) (list of tuples)
    @staticmethod
    def get_transactions(pysql):
        # Initialize the pysql object
        pysql.init()

        sql_stmt = "SELECT `TransactionID`, `ProductID`, `Name`, `TransactionType`, `Quantity`, `UnitType`, `Timestamp` \
                    FROM `InventoryTransactions` JOIN `Products` USING (`ProductID`)"
        pysql.run(sql_stmt)

        # Get the results
        transactions = pysql.result

        # Deinitialize the pysql object
        pysql.deinit()

        return transactions

    # @brief This method returns the transactions made on a particular day
    # @param pysql PySql object
    # @param date On Date (string of format "YYYY-MM-DD")
    # @retval (TransactionID, ProductID, Name, TransactionType, Quantity, UnitType, Timestamp) (list of tuples)
    @staticmethod
    def get_transactions_by_date(pysql, date):
        # Initialize the pysql object
        pysql.init()

        # Get the transactions made on that date
        sql_stmt = "SELECT `TransactionID`, `ProductID`, `Name`, `TransactionType`, `Quantity`, `UnitType`, TIME(`Timestamp`) \
                    FROM `InventoryTransactions` JOIN `Products` USING (`ProductID`) \
                    WHERE DATE(`Timestamp`) = %s"
        pysql.run(sql_stmt, (date, ))

        # Get the results
        transactions = pysql.result

        # Deinitialize the pysql object
        pysql.deinit()

        return transactions

    # @brief This method returns all the transactions of the product
    #        on a given day
    # @param pysql PySql object
    # @param product_id ProductID
    # @param date On Date (string of format "YYYY-MM-DD")
    # @retval (TransactionID, TransactionType, Quantity, Timestamp) (list of tuples)
    @staticmethod
    def get_transactions_of_product_by_date(pysql, product_id, date):
        # Initialize the pysql object
        pysql.init()

        # Get the transaction details of the products on the given date
        sql_stmt = "SELECT `TransactionID`, `TransactionType`, `Quantity`, TIME(`Timestamp`) \
                    FROM `InventoryTransactions` \
                    WHERE `ProductID` = %s AND DATE(`Timestamp`) = %s"
        pysql.run(sql_stmt, (product_id, date))

        # Get the result
        transactions = pysql.result

        # Deinitialize the pysql object
        pysql.deinit()

        return transactions
