# @brief This class is used to handle the product management in CMS
# @note  There is not need to create an object of this class as all
#        methods in this class are static
class ProductManager:

    # @brief This method adds a new product to the global information
    #        of products
    # @param pysql PySql object
    # @param product_id ProductID of new product (string)
    # @param name Name of new product (string)
    # @param description Description of new product (string)
    # @param unit_price Price per unit of new product (float)
    # @param unit_type Type of unit i.e. Enum ("kg" or "pcs") (string)
    # @param current_discount Discount on the product in percentage (float)
    @staticmethod
    def add_product(pysql, product_id, name, description, unit_price, unit_type, current_discount = None):
        # Check if discount is specified
        if current_discount:
            sql_stmt = "INSERT INTO `Products` \
                        VALUES (%s, %s, %s, %s, %s, %s)"
            pysql.run(sql_stmt, (product_id, name, description, unit_price, unit_type, current_discount))
        else:
            sql_stmt = "INSERT INTO `Products` (`ProductID`, `Name`, `Description`, `UnitPrice`, `UnitType`) \
                        VALUES (%s, %s, %s, %s, %s)"
            pysql.run(sql_stmt, (product_id, name, description, unit_price, unit_type))
        # Commit the changes
        pysql.commit()

    # @brief This method updates the discount percentage of the product
    # @param pysql PySql object
    # @param product_id ProductID of product to be updated
    # @param discount New value of current discount
    @staticmethod
    def update_product_discount(pysql, product_id, discount):
        # Update the current discount field
        sql_stmt = "UPDATE `Products` \
                    SET `CurrentDiscount` = %s \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (discount, product_id))
        # Commit the changes
        pysql.commit()

    # @brief This method updates the discount percentage of the product
    # @param pysql PySql object
    # @param product_id ProductID of product to be updated
    # @param price New value of unit price
    @staticmethod
    def update_product_price(pysql, product_id, price):
        # Update the unit price field
        sql_stmt = "UPDATE `Products` \
                    SET `UnitPrice` = %s \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (price, product_id))
        # Commit the changes
        pysql.commit()

    # @brief This method updates the discount percentage of the product
    # @param pysql PySql object
    # @param product_id ProductID of product to be updated
    # @param description New description for the product
    @staticmethod
    def update_description(pysql, product_id, description):
        # Update the description field
        sql_stmt = "UPDATE `Products` \
                    SET `Description` = %s \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (description, product_id))
        # Commit the changes
        pysql.commit()

    # @brief This method checks if the given primary key is already
    #        present in the Products relation
    # @param pysql PySql object
    # @param product_id ProductID of product to be updated
    # @retval 0 The product id is not used
    # @retval 1 The product id is already used
    @staticmethod
    def is_product_id_used(pysql, product_id):
        # Get the product id of the given product
        sql_stmt = "SELECT `ProductID` \
                    FROM `Products` \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (product_id, ))

        return len(pysql.get_results())
