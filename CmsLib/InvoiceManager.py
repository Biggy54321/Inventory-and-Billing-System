# Import the required libraries
from CmsLib.TokenManager import *

# This variable stores the next InvoiceID integer
next_invoice_id = None
# This variable indicates whether the next_invoice_id has been initialized
next_invoice_id_read = 0

# @brief This class is used to handle the invoice management in CMS
# @note  There is not need to create an object of this class as all
#        methods in this class are static
class InvoiceManager:

    # @brief This method creates an invoice for the given tokens
    # @param pysql PySql object
    # @param token_ids Token Ids (list of strings)
    # @param payment_mode Payment mode (enum string)
    # @retval invoice_id The invoice id created (string)
    # @retval None For discrepancy in the tokens
    @staticmethod
    def generate_invoice(pysql, token_ids, payment_mode):
        # Get the global variables
        global next_invoice_id
        global next_invoice_id_read

        # Initialize the pysql object
        pysql.init()

        # Read the next invoice id for once
        if not next_invoice_id_read:
            sql_stmt = "SELECT COUNT(*) \
                        FROM `Invoices`"
            pysql.run(sql_stmt)
            next_invoice_id = pysql.scalar_result
            next_invoice_id_read = 1

        # Check if tokens are all assigned and the total is not null
        has_products = 0
        for token in token_ids:
            # Check if token is assigned
            if not TokenManager.is_token_assigned(pysql, token):
                return None
            # Check if token has any products
            token_details = TokenManager.get_token_details(pysql, token)
            # Update the total product status
            has_products = has_products or bool(token_details)

        if not has_products:
            return None

        # Create an invoice id
        invoice_id = "INV-" + format(next_invoice_id, "010d")

        # Create an invoice
        sql_stmt = "INSERT INTO `Invoices`(`InvoiceID`, `InvoiceDate`, `PaymentMode`) \
                    VALUES (%s, (SELECT CURRENT_TIMESTAMP), %s)"
        pysql.run(sql_stmt, (invoice_id, payment_mode))

        # Link the invoice with each of the token ids
        token_ids = [(token, ) for token in token_ids]
        sql_stmt = "UPDATE `Tokens` \
                    SET `InvoiceID` = '{}' \
                    WHERE `TokenID` = %s".format(invoice_id)
        pysql.run_many(sql_stmt, token_ids)

        # Add the invoice product details
        sql_stmt = "SELECT `ProductID`, `Name`, `SumQuantity`, `UnitPrice`, `CurrentDiscount` \
                    FROM Products JOIN (SELECT `ProductID`, SUM(`Quantity`) AS `SumQuantity` \
                                        FROM `TokensSelectProducts` \
                                        WHERE `TokenID` IN (SELECT `TokenID` \
                                                            FROM `Tokens` \
                                                            WHERE `InvoiceID` = %s) \
                                        GROUP BY `ProductID`) AS `ProductsQuantities` \
                                  USING (`ProductID`)"
        pysql.run(sql_stmt, (invoice_id, ))
        invoice_details = pysql.result

        # Add these product details with the corresponding invoice
        sql_stmt = "INSERT INTO `ProductsInInvoices` \
                    VALUES ('{}', %s, %s, %s, %s, %s)".format(invoice_id)
        pysql.run_many(sql_stmt, invoice_details)

        # Make the assigned status false and make the invoice id null
        sql_stmt = "UPDATE `Tokens` \
                    SET `Assigned?` = false, \
                        `InvoiceID` = NULL \
                    WHERE `TokenID` = %s"
        pysql.run_many(sql_stmt, token_ids)

        # Remove all the products selected by this token
        sql_stmt = "DELETE FROM `TokensSelectProducts` \
                    WHERE `TokenID` = %s"
        pysql.run_many(sql_stmt, token_ids)

        # Commit the changes
        pysql.commit()

        # Increment the global invoice id
        next_invoice_id += 1

        # Deinitialize the pysql object
        pysql.deinit()

        # Return the invoice id
        return invoice_id

    # @brief This method updates the default values of GST and CGST
    # @param pysql PySql object
    # @param gst New value of GST in percentage (float)
    # @param cgst New value of CGST in percentage (float)
    @staticmethod
    def update_gst_cgst(pysql, gst, cgst):
        # Initialize the pysql object
        pysql.init()

        # Update GST
        sql_stmt = "ALTER TABLE `Invoices` \
                    ALTER `GST` SET DEFAULT %s"
        pysql.run(sql_stmt, (gst, ))
        # Update CGST
        sql_stmt = "ALTER TABLE `Invoices` \
                    ALTER `CGST` SET DEFAULT %s"
        pysql.run(sql_stmt, (cgst, ))

        # Commit the changes
        pysql.commit()

        # Deinitialize the pysql object
        pysql.deinit()

    # @brief This method updates the discount for a particular invoice
    # @param pysql PySql object
    # @param invoice_id InvoiceID (string)
    # @param discount The discount amount given (float)
    @staticmethod
    def give_additional_discount(pysql, invoice_id, discount):
        # Initialize the pysql object
        pysql.init()

        # Update the discount value
        sql_stmt = "UPDATE `Invoices` \
                    SET `DiscountGiven` = %s \
                    WHERE `InvoiceID` = %s"
        pysql.run(sql_stmt, (discount, invoice_id))

        # Commit the changes
        pysql.commit()

        # Deinitialize the pysql object
        pysql.deinit()

    # @brief This method prints the invoice for the specified InvoiceID
    # @param pysql PySql object
    # @param invoice_id InvoiceID (string)
    @staticmethod
    def get_invoice(pysql, invoice_id):
        pass
