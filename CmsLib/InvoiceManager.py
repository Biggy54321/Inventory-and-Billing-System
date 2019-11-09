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
    # @retval 1 One of the tokens not found or not assigned
    # @retval 2 No products to be billed
    # @retval 3 Payment mode incorrect
    @staticmethod
    def __generate_invoice(pysql, token_ids, payment_mode):
        # Get the global variables
        global next_invoice_id
        global next_invoice_id_read

        # Read the next invoice id for once
        if not next_invoice_id_read:
            sql_stmt = "SELECT COUNT(*) \
                        FROM `Invoices`"
            pysql.run(sql_stmt)
            next_invoice_id = pysql.scalar_result
            next_invoice_id_read = 1

        # Check if tokens are all assigned and the total is not null
        invoice_has_products = 0
        for token in token_ids:
            # Get the token assignment status
            is_assigned = TokenManager._TokenManager__is_token_assigned(pysql, token)
            # Get the token product status
            token_has_products = TokenManager._TokenManager__token_has_products(pysql, token)

            # Check if token is assigned
            if not is_assigned:
                return 1

            # Update the total product status
            invoice_has_products = invoice_has_products or token_has_products

        if not invoice_has_products:
            return 2

        # Check the payment mode
        if payment_mode not in ["cash", "card", "wallet"]:
            return 3

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
        sql_stmt = "SELECT `ProductID`, `Name`, `SumQuantity`, `UnitPrice`, `GST`, `CGST`, `CurrentDiscount` \
                    FROM `Products` JOIN (SELECT `ProductID`, SUM(`Quantity`) AS `SumQuantity` \
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
                    VALUES ('{}', %s, %s, %s, %s, %s, %s, %s)".format(invoice_id)
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

        # Increment the global invoice id
        next_invoice_id += 1

        # Return the invoice id
        return invoice_id

    # @brief This method updates the discount for a particular invoice
    # @param pysql PySql object
    # @param invoice_id InvoiceID (string)
    # @param discount The discount amount given (float)
    # @retval 0 Discount given successfully
    # @retval 1 Invoice not found
    # @retval 2 Discount negative
    @staticmethod
    def __give_additional_discount(pysql, invoice_id, discount):
        # Check if invoice exists
        sql_stmt = "SELECT COUNT(*) \
                    FROM `Invoices` \
                    WHERE `InvoiceID` = %s"
        pysql.run(sql_stmt, (invoice_id, ))
        invoice_present = pysql.scalar_result

        if not invoice_present:
            return 1

        # Check if discount is negative
        if discount < 0:
            return 2

        # Update the discount value
        sql_stmt = "UPDATE `Invoices` \
                    SET `DiscountGiven` = %s \
                    WHERE `InvoiceID` = %s"
        pysql.run(sql_stmt, (discount, invoice_id))

        return 0

    # @brief This method returns the invoice details for the specified InvoiceID
    # @param pysql PySql object
    # @param invoice_id InvoiceID (string)
    # @retval (InvoiceID, InvoiceDate, GST, CGST, DiscountGiven, PaymentMode), (ProductID, Name, Quantity, UnitPrice, Discount)
    @staticmethod
    def __get_invoice_details(pysql, invoice_id):
        # Get the invoice parameters
        sql_stmt = "SELECT * \
                    FROM `Invoices` \
                    WHERE `InvoiceID` = %s"
        pysql.run(sql_stmt, (invoice_id, ))
        invoice_parameters = pysql.first_result

        # Get the invoice product details
        sql_stmt = "SELECT `ProductID`, `Name`, `Quantity`, `UnitPrice`, `Discount` \
                    FROM `ProductsInInvoices` \
                    WHERE `InvoiceID` = %s"
        pysql.run(sql_stmt, (invoice_id, ))
        invoice_details = pysql.result

        # Return the result
        return invoice_parameters, invoice_details

    # @brief This method returns the invoice parameters of all the invoices
    #        having their invoice dates on the given date
    # @param pysql PySql object
    # @param date On Date (string of format "YYYY-MM-DD")
    # @retval (InvoiceID, InvoiceDate, GST, CGST, DiscountGiven, PaymentMode) (list of tuples)
    @staticmethod
    def __get_invoices_by_date(pysql, date):
        # Get the invoice parameters on the specified date
        sql_stmt = "SELECT `InvoiceID`, TIME(`InvoiceDate`), `GST`, `CGST`, `DiscountGiven`, `PaymentMode` \
                    FROM `Invoices` \
                    WHERE DATE(`InvoiceDate`) = %s"
        pysql.run(sql_stmt, date)

        # Get the result invoice parameters
        invoices = pysql.result

        return invoices

    # @ref __generate_invoice
    @staticmethod
    def generate_invoice(pysql, token_ids, payment_mode):
        return pysql.run_transaction(InvoiceManager.__generate_invoice,
                                     token_ids,
                                     payment_mode)

    # @ref __give_additional_discount
    @staticmethod
    def give_additional_discount(pysql, invoice_id, discount):
        return pysql.run_transaction(InvoiceManager.__give_additional_discount,
                                     invoice_id,
                                     discount)

    # @ref __get_invoice_details
    @staticmethod
    def get_invoice_details(pysql, invoice_id):
        return pysql.run_transaction(InvoiceManager.__get_invoice_details,
                                     invoice_id,
                                     commit = False)

    # @ref __get_invoices_by_date
    @staticmethod
    def get_invoices_by_date(pysql, date):
        return pysql.run_transaction(InvoiceManager.__get_invoices_by_date,
                                     date,
                                     commit = False)
