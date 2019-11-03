# @brief This class is used to handle the product management in CMS
# @note  There is not need to create an object of this class as all
#        methods in this class are static
class ProductManager:

    # @brief This method adds a new product to the global information
    #        of products
    # @param pysql PySql object
    # @param product_id ProductID (string)
    # @param name Product Name (string)
    # @param description Product Description (string)
    # @param unit_price Price per unit (float)
    # @param unit_type Type of units (enum string)
    # @param current_discount Discount in percentage (float)
    @staticmethod
    def add_product(pysql, product_id, name, description, unit_price, unit_type, current_discount = None):
        # Initialize the pysql object
        pysql.init()

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

        # Denitialize the pysql object
        pysql.deinit()

    # @brief This method updates the discount percentage of the product
    # @param pysql PySql object
    # @param product_id ProductID
    # @param discount New value of current discount
    @staticmethod
    def update_product_discount(pysql, product_id, discount):
        # Initialize the pysql object
        pysql.init()

        # Update the current discount field
        sql_stmt = "UPDATE `Products` \
                    SET `CurrentDiscount` = %s \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (discount, product_id))

        # Commit the changes
        pysql.commit()

        # Denitialize the pysql object
        pysql.deinit()

    # @brief This method updates the discount percentage of the product
    # @param pysql PySql object
    # @param product_id ProductID
    # @param price New value of unit price
    @staticmethod
    def update_product_price(pysql, product_id, price):
        # Initialize the pysql object
        pysql.init()

        # Update the unit price field
        sql_stmt = "UPDATE `Products` \
                    SET `UnitPrice` = %s \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (price, product_id))

        # Commit the changes
        pysql.commit()

        # Denitialize the pysql object
        pysql.deinit()

    # @brief This method updates the discount percentage of the product
    # @param pysql PySql object
    # @param product_id ProductID
    # @param description New description for the product
    @staticmethod
    def update_description(pysql, product_id, description):
        # Initialize the pysql object
        pysql.init()

        # Update the description field
        sql_stmt = "UPDATE `Products` \
                    SET `Description` = %s \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (description, product_id))

        # Commit the changes
        pysql.commit()

        # Denitialize the pysql object
        pysql.deinit()

    # @brief This method checks if the given primary key is already
    #        present in the Products relation
    # @param pysql PySql object
    # @param product_id ProductID
    # @retval 0 The product id is not used
    # @retval 1 The product id is already used
    @staticmethod
    def is_product_id_used(pysql, product_id):
        # Initialize the pysql object
        pysql.init()

        # Get the product id of the given product
        sql_stmt = "SELECT `ProductID` \
                    FROM `Products` \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (product_id, ))

        # Get the result
        is_used = len(pysql.result)

        # Denitialize the pysql object
        pysql.deinit()

        return is_used


    # @brief This method returns all the products information
    # @param pysql PySql object
    # @retval (ProductID, Name, Description, UnitPrice, UnitType, CurrentDiscount) (list of tuples)
    @staticmethod
    def get_all_products(pysql):
        # Initialize the pysql object
        pysql.init()

        # Get the product id of the given product
        sql_stmt = "SELECT * \
                    FROM `Products`"
        pysql.run(sql_stmt)

        # Get the result
        products = pysql.result

        # Denitialize the pysql object
        pysql.deinit()

        return products

    # @brief This method returns the product if from the name of the product
    # @param pysql PySql object
    # @param name Product name
    # @retval ProductID
    @staticmethod
    def get_product_id_from_name(pysql, name):
        # Initialize the pysql object
        pysql.init()

        # Get the product id of the given product
        sql_stmt = "SELECT `ProductID` \
                    FROM `Products` \
                    WHERE `Name` = %s"
        pysql.run(sql_stmt, (name, ))

        # Get the result
        product_id = pysql.scalar_result

        # Denitialize the pysql object
        pysql.deinit()

        return product_id


