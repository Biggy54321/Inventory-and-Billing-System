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
    # @retval 0 Added product successfully
    # @retval 1 Product id already used
    # @retval 2 Unit price not positive
    # @retval 3 Unit type not valid
    # @retval 4 GST and CGST not valid
    # @retval 5 Current discount not valid
    @staticmethod
    def __add_product(pysql, product_id, name, description, unit_price, unit_type, gst, cgst, current_discount):
        # Get the product existence status
        product_exists = ProductManager._ProductManager__product_exists(pysql, product_id)

        # Check if product already exists
        if product_exists:
            return 1

        # Check if unit price is positive
        if unit_price <= 0:
            return 2

        # Check if unit type is right
        if unit_type not in ["kg", "pcs", "ltrs"]:
            return 3

        # Check if gst and cgst are correct
        if 0 < gst or gst > 100:
            return 4
        if 0 < cgst or cgst > 100:
            return 4

        # Check if discount not negative
        if current_discount and current_discount < 0:
            return 5

        # Check if discount is specified
        if current_discount:
            sql_stmt = "INSERT INTO `Products` \
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            pysql.run(sql_stmt, (product_id, name, description, unit_price, unit_type, gst, cgst, current_discount))
        else:
            sql_stmt = "INSERT INTO `Products` (`ProductID`, `Name`, `Description`, `UnitPrice`, `UnitType`, `GST`, `CGST`) \
                        VALUES (%s, %s, %s, %s, %s, %s, %s)"
            pysql.run(sql_stmt, (product_id, name, description, unit_price, unit_type, gst, cgst))

            return 0

    # @brief This method updates the discount percentage of the product
    # @param pysql PySql object
    # @param product_id ProductID
    # @param discount New value of current discount
    # @retval 0 Updated successfully
    # @retval 1 Product not found
    # @retval 2 Discount negative
    @staticmethod
    def __update_product_discount(pysql, product_id, discount):
        # Get the product existence status
        product_exists = ProductManager._ProductManager__product_exists(pysql, product_id)

        # Check if product exists
        if not product_exists:
            return 1

        # Check if discount is negative
        if discount < 0:
            return 2

        # Update the current discount field
        sql_stmt = "UPDATE `Products` \
                    SET `CurrentDiscount` = %s \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (discount, product_id))

        return 0

    # @brief This method updates the discount percentage of the product
    # @param pysql PySql object
    # @param product_id ProductID
    # @param price New value of unit price
    # @retval 0 Updated successfully
    # @retval 1 Product not found
    # @retval 2 Price not positive
    @staticmethod
    def __update_product_price(pysql, product_id, price):
        # Get the product existence status
        product_exists = ProductManager._ProductManager__product_exists(pysql, product_id)

        # Check if product exists
        if not product_exists:
            return 1

        # Check if discount is not positive
        if price <= 0:
            return 2

        # Update the unit price field
        sql_stmt = "UPDATE `Products` \
                    SET `UnitPrice` = %s \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (price, product_id))

        return 0

    # @brief This method updates the discount percentage of the product
    # @param pysql PySql object
    # @param product_id ProductID
    # @param description New description for the product
    # @retval 0 Updated successfully
    # @retval 1 Product not found
    @staticmethod
    def __update_product_description(pysql, product_id, description):
        # Get the product existence status
        product_exists = ProductManager._ProductManager__product_exists(pysql, product_id)

        # Check if product exists
        if not product_exists:
            return 1

        # Update the description field
        sql_stmt = "UPDATE `Products` \
                    SET `Description` = %s \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (description, product_id))

        return 0

    # @brief This method updates the gst and cgst
    # @param pysql PySql object
    # @param product_id ProductID
    # @param gst GST percentage
    # @param cgst CGST percentage
    # @retval 0 Updated successfully
    # @retval 1 Product not found
    @staticmethod
    def __update_product_gst_cgst(pysql, product_id, gst, cgst):
        # Get the product existence status
        product_exists = ProductManager._ProductManager__product_exists(pysql, product_id)

        # Check if product exists
        if not product_exists:
            return 1

        # Update the gst and cgst fields
        sql_stmt = "UPDATE `Products` \
                    SET `GST` = %s,
                        `CGST` = %s \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (gst, cgst, product_id))

        return 0

    # @brief This method checks if the given product is already
    #        present in the Products relation
    # @param pysql PySql object
    # @param product_id ProductID
    # @retval 0 The product not present
    # @retval 1 The product already present
    @staticmethod
    def __product_exists(pysql, product_id):
        # Get the product id of the given product
        sql_stmt = "SELECT COUNT(*) \
                    FROM `Products` \
                    WHERE `ProductID` = %s"
        pysql.run(sql_stmt, (product_id, ))

        # Get the result
        product_exists = pysql.scalar_result

        return product_exists

    # @brief This method returns all the products information
    # @param pysql PySql object
    # @retval (ProductID, Name, Description, UnitPrice, UnitType, CurrentDiscount) (list of tuples)
    @staticmethod
    def __get_all_products(pysql):
        # Get the product id of the given product
        sql_stmt = "SELECT * \
                    FROM `Products`"
        pysql.run(sql_stmt)

        # Get the result
        products = pysql.result

        return products

    # @brief This method returns the product if from the name of the product
    # @param pysql PySql object
    # @param name Product name
    # @retval ProductID
    @staticmethod
    def __get_product_id_from_name(pysql, name):
        # Get the product id of the given product
        sql_stmt = "SELECT `ProductID` \
                    FROM `Products` \
                    WHERE `Name` = %s"
        pysql.run(sql_stmt, (name, ))

        # Get the result
        product_id = pysql.scalar_result

        return product_id

    # @ref __add_product
    @staticmethod
    def add_product(pysql, product_id, name, description, unit_price, unit_type, current_discount = None):
        return pysql.run_transaction(ProductManager.__add_product,
                                     product_id,
                                     name,
                                     description,
                                     unit_price,
                                     unit_type,
                                     current_discount)

    # @ref __update_product_discount
    @staticmethod
    def update_product_discount(pysql, product_id, discount):
        return pysql.run_transaction(ProductManager.__update_product_discount,
                                     product_id,
                                     discount)

    # @ref __update_product_price
    @staticmethod
    def update_product_price(pysql, product_id, price):
        return pysql.run_transaction(ProductManager.__update_product_price,
                                     product_id,
                                     price)

    # @ref __update_description
    @staticmethod
    def update_product_description(pysql, product_id, description):
        return pysql.run_transaction(ProductManager.__update_product_description,
                                     product_id,
                                     description)

    # @ref __update_product_gst_cgst
    @staticmethod
    def update_product_gst_cgst(pysql, product_id, gst, cgst):
        return pysql.run_transaction(ProductManager.__update_product_gst_cgst,
                                     product_id,
                                     gst,
                                     cgst)

    # @ref __is_product_id_used
    @staticmethod
    def product_exists(pysql, product_id):
        return pysql.run_transaction(ProductManager.__product_exists,
                                     product_id,
                                     commit = False)

    # @ref __get_all_products
    @staticmethod
    def get_all_products(pysql):
        return pysql.run_transaction(ProductManager.__get_all_products,
                                     commit = False)

    # @ref __get_product_id_from_name
    @staticmethod
    def get_product_id_from_name(pysql, name):
        return pysql.run_transaction(ProductManager.__get_product_id_from_name,
                                     name,
                                     commit = False)
