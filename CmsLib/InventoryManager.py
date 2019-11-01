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
    # @param product_id ProductID to be checked (string)
    # @retval unsigned integer When there is some quantity of the specified
    #                          product
    # @retval 0 When the quantity of the product is 0 / product does not exists
    @staticmethod
    def get_displayed_quantity(pysql, product_id):
        try:
            # Get the displayed quantity of the product
            sql_stmt = "SELECT `DisplayedQuantity` \
                        FROM `Inventory` \
                        WHERE `ProductID` = %s"
            pysql.run(sql_stmt, (product_id, ))

            # Return the quantity
            return pysql.get_results()[0][0]
        except IndexError:
            # If product not present
            return 0
        except:
            # Print error
            pysql.print_error()

    # @brief This method returns the stored (local inventory) quantity of the
    #        specified product
    # @param pysql PySql object
    # @param product_id ProductID to be checked (string)
    # @retval unsigned integer When there is some quantity of the specified
    #                          product
    # @retval 0 When the quantity of the product is 0 / product does not exists
    @staticmethod
    def get_stored_quantity(pysql, product_id):
        try:
            # Get the stored quantity of the product
            sql_stmt = "SELECT `StoredQuantity` \
                        FROM `Inventory` \
                        WHERE `ProductID` = %s"
            pysql.run(sql_stmt, (product_id, ))

            # Return the quantity
            return pysql.get_results()[0][0]
        except IndexError:
            return 0
        except:
            # Print error
            pysql.print_error()

    # @brief This method checks if the specified product stored
    #        is below the set threshold
    # @param pysql PySql Object
    # @param product_id ProductID to be checked for (string)
    # @retval 1 If the product is below threshold
    # @retval 0 If the product is not below threshold
    @staticmethod
    def is_below_threshold(pysql, product_id):
        try:
            # Check if the stored quantity is less than equal the store threshold
            sql_stmt = "SELECT `StoredQuantity` <= `StoreThreshold` \
                        FROM `Inventory` \
                        WHERE `ProductID` = %s"
            pysql.run(sql_stmt, (product_id, ))

            # Return boolean value
            return pysql.get_results()[0][0]
        except IndexError:
            return 0
        except:
            # Print error
            pysql.print_error()

    # @brief This method updates the threshold value of the specified product
    # @param pysql PySql object
    # @param product_id ProductID to be updated (string)
    # @param threshold Threshold to be set for the product (float)
    @staticmethod
    def update_threshold(pysql, product_id, threshold):
        try:
            # Set the value of threshold to the given argument
            sql_stmt = "UPDATE `Inventory` \
                        SET `StoreThreshold` = %s \
                        WHERE `ProductID` = %s"
            pysql.run(sql_stmt, (threshold, product_id))
            # Commit the changes
            pysql.commit()
        except:
            # Print error
            pysql.print_error()
            # Revert the changes
            pysql.rollback()

    # @brief This method removes the specified product quantity from the
    #        stored (local inventory) quantity and logs the transaction
    # @param pysql PySql object
    # @param product_id ProductID to be updated (string)
    # @param threshold Threshold to be set for the product (float)
    @staticmethod
    def sub_product_from_inventory(pysql, product_id, quantity):
        try:
            # Subtract the specified quantity of the product
            sql_stmt = "UPDATE `Inventory` \
                        SET `StoredQuantity` = `StoredQuantity` - %s \
                        WHERE `ProductID` = %s"
            pysql.run(sql_stmt, (quantity, product_id))

            # Log the transaction
            InventoryManager.log_transaction(pysql, "INV_SUB", product_id, quantity)

            # Commit the changes
            pysql.commit()
        except:
            # Print error
            pysql.print_error()
            # Revert the changes
            pysql.rollback()

    # @brief This method logs the transaction of a specified quantity
    #        of the product depending on the transaction type
    # @param pysql PySql object
    # @param transaction_type Enum TransactionType (string)
    # @param product_id ProductID (strin)
    # @param quantity Product quantity (float)
    @staticmethod
    def log_transaction(pysql, transaction_type, product_id, quantity):
        # Fetch the global variables
        global next_transaction_id
        global next_transaction_id_read

        # Read the next transaction id if already filled with data
        if not next_transaction_id_read:
            sql_stmt = "SELECT COUNT(*) \
                        FROM `InventoryTransactions`"
            pysql.run(sql_stmt)
            next_transaction_id = pysql.get_results()[0][0]
            next_transaction_id_read = 1

        # Get the string transaction id
        transaction_id = "TRC-" + format(next_transaction_id, "010d")
        next_transaction_id += 1

        # Enter the transaction in the inventory transactions
        try:
            sql_stmt = "INSERT INTO `InventoryTransactions` \
                        VALUES (%s, %s, %s, %s, (SELECT CURRENT_TIMESTAMP))"
            pysql.run(sql_stmt, (transaction_id, transaction_type, product_id, quantity))
        except:
            # Restore the transaction id
            next_transaction_id -= 1
            # Print error
            pysql.print_error()
