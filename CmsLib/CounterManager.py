# Import the required modules
from CmsLib.InventoryManager import *
from CmsLib.TokenManager import *

# @brief This class is used to handle the counter management in CMS
# @note  There is not need to create an object of this class as all
#        methods in this class are static
class CounterManager:

    # @brief This method is used to add the requested quantity of requested
    #        product from counter to the requesting token and also logs the
    #        transaction
    # @param pysql Pysql Object
    # @param token_id TokenID (string)
    # @param product_id ProductID (string)
    # @param quantity Product Quantity (float)
    @staticmethod
    def __add_counter_to_token(pysql, token_id, product_id, quantity):
        # Check if token is assigned
        if not TokenManager.is_token_assigned(pysql, token_id):
            return

        # Remove from displayed quantity
        sql_stmt = "UPDATE `Inventory` \
                    SET `DisplayedQuantity` = `DisplayedQuantity` - %s \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (quantity, product_id))

        # Add the product quantity to the select relation
        sql_stmt = "INSERT INTO `TokensSelectProducts` \
                    VALUES (%s, %s, %s)"
        pysql.run(sql_stmt, (token_id, product_id, quantity))

        # Log the transaction
        InventoryManager.log_transaction(pysql, "COUNTER_SUB", product_id, quantity)

    # @brief This method adds the specified quantity of the product from
    #        the stored inventory to the counter inventory and also logs
    #        the transaction
    # @param pysql PySql object
    # @param product_id ProductID  (string)
    # @param quantity Product Quantity (float)
    @staticmethod
    def __add_inventory_to_counter(pysql, product_id, quantity):
        # Remove from inventory
        sql_stmt = "UPDATE `Inventory` \
                    SET `DisplayedQuantity` = `DisplayedQuantity` + %s, \
                        `StoredQuantity` = `StoredQuantity` - %s \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (quantity, quantity, product_id))

        # Log the transaction
        InventoryManager.log_transaction(pysql, "INVENTORY_TO_COUNTER", product_id, quantity)

    # @brief This method adds the specified quantity of the product to
    #        the counter and logs the transaction
    # @param pysql PySql object
    # @param token_id TokenID (string)
    # @param product_id ProductID (string)
    @staticmethod
    def __add_token_to_counter(pysql, token_id, product_id):
        # Get the current quantity of products in the token
        sql_stmt = "SELECT `Quantity` \
                    FROM `TokensSelectProducts` \
                    WHERE `TokenID` = %s AND `ProductID` = %s"
        pysql.run(sql_stmt, (token_id, product_id))

        # Get the result quantity from the query
        quantity = pysql.scalar_result

        # End if quantity is none
        if not quantity:
            return

        # Remove the product from the product
        sql_stmt = "DELETE FROM `TokensSelectProducts` \
                    WHERE `TokenID` = %s AND `ProductID` = %s"
        pysql.run(sql_stmt, (token_id, product_id))

        # Add the required quantity to the counter
        sql_stmt = "UPDATE `Inventory` \
                    SET `DisplayedQuantity` = `DisplayedQuantity` + %s \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (quantity, product_id))

        # Log the transaction
        InventoryManager.log_transaction(pysql, "COUNTER_ADD", product_id, quantity)

    # @ref __add_counter_to_token
    @staticmethod
    def add_counter_to_token(pysql, token_id, product_id, quantity):
        return pysql.run_transaction(CounterManager.__add_counter_to_token,
                                     token_id,
                                     product_id,
                                     quantity)

    # @ref __add_inventory_to_counter
    @staticmethod
    def add_inventory_to_counter(pysql, product_id, quantity):
        return pysql.run_transaction(CounterManager.__add_inventory_to_counter,
                                     product_id,
                                     quantity)

    # @ref __add_token_to_counter
    @staticmethod
    def add_token_to_counter(pysql, token_id, product_id):
        return pysql.run_transaction(CounterManager.__add_token_to_counter,
                                     token_id,
                                     product_id)
