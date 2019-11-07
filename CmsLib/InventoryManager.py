# Import the required libraries
from CmsLib.ProductManager import *

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
    def __get_displayed_quantity(pysql, product_id):
        # Get the displayed quantity of the product
        sql_stmt = "SELECT `DisplayedQuantity` \
                    FROM `Inventory` \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (product_id, ))

        # Return the quantity
        quantity = pysql.scalar_result

        return quantity

    # @brief This method returns the stored (local inventory) quantity of the
    #        specified product
    # @param pysql PySql object
    # @param product_id ProductID (string)
    # @retval integer When quantity of product is found
    # @retval None For product not found
    @staticmethod
    def __get_stored_quantity(pysql, product_id):
        # Get the stored quantity of the product
        sql_stmt = "SELECT `StoredQuantity` \
                    FROM `Inventory` \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (product_id, ))

        # Return the quantity
        quantity = pysql.scalar_result

        return quantity

    # @brief This method checks if the specified product stored
    #        is below the set threshold
    # @param pysql PySql Object
    # @param product_id ProductID (string)
    # @retval 1 If the product is below threshold
    # @retval 0 If the product is not below threshold
    # @retval None For product not found
    @staticmethod
    def __is_below_threshold(pysql, product_id):
        # Check if the stored quantity is less than equal the store threshold
        sql_stmt = "SELECT `StoredQuantity` <= `StoreThreshold` \
                    FROM `Inventory` \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (product_id, ))

        # Return boolean value
        is_below = pysql.scalar_result

        return is_below

    # @brief This method updates the threshold value of the specified product
    # @param pysql PySql object
    # @param product_id ProductID (string)
    # @param threshold Threshold (float)
    # @retval 0 Updated successfully
    # @retval 1 Threshold negative
    # @retval 2 Product not found
    @staticmethod
    def __update_threshold(pysql, product_id, threshold):
        # Check if threshold is negative
        if threshold < 0:
            return 1

        # Check if product exists
        sql_stmt = "SELECT 1 \
                    FROM `Inventory` \
                    WHERE `ProductID` = %s"
        product_present = pysql.scalar_result
        if not product_present:
            return 2

        # Set the value of threshold to the given argument
        sql_stmt = "UPDATE `Inventory` \
                    SET `StoreThreshold` = %s \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (threshold, product_id))

        return 0

    # @brief This method removes the specified product quantity from the
    #        stored (local inventory) quantity and logs the transaction
    # @param pysql PySql object
    # @param product_id ProductID (string)
    # @param threshold Threshold (float)
    # @retval 0 Transaction successfull
    # @retval 1 Quantity not positive
    # @retval 2 Product not found
    @staticmethod
    def __sub_product_from_inventory(pysql, product_id, quantity):
        # Check if quantity is negative
        if quantity < 0:
            return 1

        # Check if product exists
        sql_stmt = "SELECT 1 \
                    FROM `Inventory` \
                    WHERE `ProductID` = %s"
        product_present = pysql.scalar_result
        if not product_present:
            return 2

        # Subtract the specified quantity of the product
        sql_stmt = "UPDATE `Inventory` \
                    SET `StoredQuantity` = `StoredQuantity` - %s \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (quantity, product_id))

        # Log the transaction
        InventoryManager.__log_transaction(pysql, "INVENTORY_SUB", product_id, quantity)

        return 0

    # @brief This method logs the transaction of a specified quantity
    #        of the product depending on the transaction type
    # @param pysql PySql object
    # @param transaction_type TransactionType (string enum)
    # @param product_id ProductID (string)
    # @param quantity Product quantity (float)
    # @retval 0 Transaction successfull
    # @retval 1 Transaction type invalid
    # @retval 2 Product not found
    # @retval 3 Quantity negative
    @staticmethod
    def __log_transaction(pysql, transaction_type, product_id, quantity):
        # Fetch the global variables
        global next_transaction_id
        global next_transaction_id_read

        # Read the next transaction id if already filled with data
        if not next_transaction_id_read:
            sql_stmt = "SELECT COUNT(*) \
                        FROM `InventoryTransactions`"
            pysql.run(sql_stmt)
            next_transaction_id = pysql.scalar_result
            next_transaction_id_read = 1

        # Check if transaction type is valid
        if transaction_type not in ["COUNTER_ADD", "COUNTER_SUB", "INVENTORY_TO_COUNTER", "INVENTORY_ADD", "INVENTORY_SUB"]:
            return 1

        # Check if product exists
        if not ProductManager._Product_Manager__is_product_id_used(pysql, product_id):
            return 2

        # Check if quantity is positive
        if quantity <= 0:
            return 3

        # Get the string transaction id
        transaction_id = "TRC-" + format(next_transaction_id, "010d")

        # Enter the transaction in the inventory transactions
        sql_stmt = "INSERT INTO `InventoryTransactions` \
                    VALUES (%s, %s, %s, %s, (SELECT CURRENT_TIMESTAMP))"
        pysql.run(sql_stmt, (transaction_id, transaction_type, product_id, quantity))

        # Increment the global transaction id count
        next_transaction_id += 1

        return 0

    # @brief This method returns the details of all the products
    #        in the inventory
    # @param pysql PySql object
    # @retval (ProductID, Name, StoredQuantity, DisplayedQuantity, StoreThreshold, UnitType) (list of tuples)
    @staticmethod
    def __get_inventory_details(pysql):
        # Get the product details of othe entire inventory
        sql_stmt = "SELECT `ProductID`, `Name`, `StoredQuantity`, `DisplayedQuantity`, `StoreThreshold`, `UnitType` \
                    FROM `Products` JOIN `Inventory` USING (`ProductID`)"
        pysql.run(sql_stmt)

        # Get the results
        inventory_details = pysql.result

        return inventory_details

    # @brief This method returns the all transactions
    # @param pysql PySql object
    # @retval (TransactionID, ProductID, Name, TransactionType, Quantity, UnitType, Timestamp) (list of tuples)
    @staticmethod
    def __get_transactions(pysql):
        sql_stmt = "SELECT `TransactionID`, `ProductID`, `Name`, `TransactionType`, `Quantity`, `UnitType`, `Timestamp` \
                    FROM `InventoryTransactions` JOIN `Products` USING (`ProductID`)"
        pysql.run(sql_stmt)

        # Get the results
        transactions = pysql.result

        return transactions

    # @brief This method returns the transactions made on a particular day
    # @param pysql PySql object
    # @param date On Date (string of format "YYYY-MM-DD")
    # @retval (TransactionID, ProductID, Name, TransactionType, Quantity, UnitType, Timestamp) (list of tuples)
    @staticmethod
    def __get_transactions_by_date(pysql, date):
        # Get the transactions made on that date
        sql_stmt = "SELECT `TransactionID`, `ProductID`, `Name`, `TransactionType`, `Quantity`, `UnitType`, TIME(`Timestamp`) \
                    FROM `InventoryTransactions` JOIN `Products` USING (`ProductID`) \
                    WHERE DATE(`Timestamp`) = %s"
        pysql.run(sql_stmt, (date, ))

        # Get the results
        transactions = pysql.result

        return transactions

    # @brief This method returns all the transactions of the product
    #        on a given day
    # @param pysql PySql object
    # @param product_id ProductID
    # @param date On Date (string of format "YYYY-MM-DD")
    # @retval (TransactionID, TransactionType, Quantity, Timestamp) (list of tuples)
    @staticmethod
    def __get_transactions_of_product_by_date(pysql, product_id, date):
        # Get the transaction details of the products on the given date
        sql_stmt = "SELECT `TransactionID`, `TransactionType`, `Quantity`, TIME(`Timestamp`) \
                    FROM `InventoryTransactions` \
                    WHERE `ProductID` = %s AND DATE(`Timestamp`) = %s"
        pysql.run(sql_stmt, (product_id, date))

        # Get the result
        transactions = pysql.result

        return transactions

    # @ref __get_displayed_quantity
    @staticmethod
    def get_displayed_quantity(pysql, product_id):
        return pysql.run_transaction(InventoryManager.__get_displayed_quantity,
                                     product_id,
                                     commit = False)

    # @ref __get_stored_quantity
    @staticmethod
    def get_stored_quantity(pysql, product_id):
        return pysql.run_transaction(InventoryManager.__get_stored_quantity,
                                     product_id,
                                     commit = False)

    # @ref __is_below_threshold
    @staticmethod
    def is_below_threshold(pysql, product_id):
        return pysql.run_transaction(InventoryManager.__is_below_threshold,
                                     product_id,
                                     commit = False)

    # @ref __update_threshold
    @staticmethod
    def update_threshold(pysql, product_id, threshold):
        return pysql.run_transaction(InventoryManager.__update_threshold,
                                     product_id,
                                     threshold)

    # @ref __sub_product_from_inventory
    @staticmethod
    def sub_product_from_inventory(pysql, product_id, quantity):
        return pysql.run_transaction(InventoryManager.__sub_product_from_inventory,
                                     product_id,
                                     quantity)

    # @ref __log_transaction
    @staticmethod
    def log_transaction(pysql, transaction_type, product_id, quantity):
        return pysql.run_transaction(InventoryManager.__log_transaction,
                                     transaction_type,
                                     product_id,
                                     quantity,
                                     commit = False)

    # @ref __get_inventory_details
    @staticmethod
    def get_inventory_details(pysql):
        return pysql.run_transaction(InventoryManager.__get_inventory_details,
                                     commit = False)

    # @ref __get_transactions
    @staticmethod
    def get_transactions(pysql):
        return pysql.run_transaction(InventoryManager.__get_transactions,
                                     commit = False)

    # @ref __get_transactions_by_date
    @staticmethod
    def get_transactions_by_date(pysql, date):
        return pysql.run_transaction(InventoryManager.__get_transactions_by_date,
                                     date,
                                     commit = False)

    # @ref __get_transactions_of_product_by_date
    @staticmethod
    def get_transactions_of_product_by_date(pysql, product_id, date):
        return pysql.run_transaction(InventoryManager.__get_transactions_of_product_by_date,
                                     product_id,
                                     date,
                                     commit = False)
