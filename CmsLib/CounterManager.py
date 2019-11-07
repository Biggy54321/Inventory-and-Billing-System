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
    # @retval 0 Transaction successfull
    # @retval 1 Token not found or is not assigned
    # @retval 2 Quantity negative
    # @retval 3 Product not found in inventory
    # @retval 4 Quantity not sufficient in inventory
    @staticmethod
    def __add_counter_to_token(pysql, token_id, product_id, quantity):
        # Check if token is assigned
        if not TokenManager._TokenManager__is_token_assigned(pysql, token_id):
            return 1

        # Check if quantity is non zero and positive
        if quantity <= 0:
            return 2

        # Get the displayed quantity of the product
        displayed_quantity = InventoryManager._InventoryManager__get_displayed_quantity(pysql, product_id)

        # Check if product exists
        if not displayed_quantity:
            return 3

        # Check if quantity is sufficient
        if displayed_quantity < quantity:
            return 4

        # Remove from displayed quantity
        sql_stmt = "UPDATE `Inventory` \
                    SET `DisplayedQuantity` = `DisplayedQuantity` - %s \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (quantity, product_id))

        # Check if the token already has the product
        sql_stmt = "SELECT 1 \
                    FROM `TokensSelectProducts` \
                    WHERE `TokenID` = %s AND `ProductID` = %s"
        pysql.run(sql_stmt, (token_id, product_id))
        # Get the result
        product_present = pysql.scalar_result

        if product_present:
            # Update the product quantity if present already
            sql_stmt = "UPDATE `TokensSelectProducts` \
                        SET `Quantity` = `Quantity` + %s \
                        WHERE `TokenID` = %s AND `ProductID` = %s"
            pysql.run(sql_stmt, (quantity, token_id, product_id))
        else:
            # Insert the product quantity if product not already present
            sql_stmt = "INSERT INTO `TokensSelectProducts` \
                        VALUES (%s, %s, %s)"
            pysql.run(sql_stmt, (token_id, product_id, quantity))

        # Log the transaction
        InventoryManager._InventoryManager__log_transaction(pysql, "COUNTER_SUB", product_id, quantity)

        return 0

    # @brief This method adds the specified quantity of the product from
    #        the stored inventory to the counter inventory and also logs
    #        the transaction
    # @param pysql PySql object
    # @param product_id ProductID  (string)
    # @param quantity Product Quantity (float)
    # @retval 0 Transaction successfull
    # @retval 1 Quantity negative
    # @retval 2 Product not found in inventory
    # @retval 3 Quantity not sufficient
    @staticmethod
    def __add_inventory_to_counter(pysql, product_id, quantity):
        # Get the stored quantity
        stored_quantity = InventoryManager._InventoryManager__get_stored_quantity(pysql, product_id)

        # Check if quantity is negative
        if quantity <= 0:
            return 1

        # Check if product exists
        if not stored_quantity:
            return 2

        # Check if stored quantity is sufficient
        if stored_quantity < quantity:
            return 3

        # Remove from inventory
        sql_stmt = "UPDATE `Inventory` \
                    SET `DisplayedQuantity` = `DisplayedQuantity` + %s, \
                        `StoredQuantity` = `StoredQuantity` - %s \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (quantity, quantity, product_id))

        # Log the transaction
        InventoryManager._InventoryManager__log_transaction(pysql, "INVENTORY_TO_COUNTER", product_id, quantity)

        return 0

    # @brief This method adds the specified quantity of the product to
    #        the counter and logs the transaction
    # @param pysql PySql object
    # @param token_id TokenID (string)
    # @param product_id ProductID (string)
    # @retval 0 Transaction successfull
    # @retval 1 Product not owned by Token
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
            return 1

        # Remove the product from the product
        sql_stmt = "DELETE FROM `TokensSelectProducts` \
                    WHERE `TokenID` = %s AND `ProductID` = %s"
        pysql.run(sql_stmt, (token_id, product_id))

        # Check if the product is already in the inventory
        sql_stmt = "SELECT 1 \
                    FROM `Inventory` \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (product_id))
        # Get the result
        product_present = pysql.scalar_result

        if product_present:
            # Update the required quantity to the counter if already present
            sql_stmt = "UPDATE `Inventory` \
                        SET `DisplayedQuantity` = `DisplayedQuantity` + %s \
                        WHERE `ProductID` = %s"
            pysql.run(sql_stmt, (quantity, product_id))
        else:
            # Insert the the required quantity to the counter
            sql_stmt = "INSERT INTO `Inventory` \
                        VALUES (%s, %s, %s, %s)"
            pysql.run(sql_stmt, (product_id, 0, quantity, 0))

        # Log the transaction
        InventoryManager._InventoryManager__log_transaction(pysql, "COUNTER_ADD", product_id, quantity)

        return 0

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
