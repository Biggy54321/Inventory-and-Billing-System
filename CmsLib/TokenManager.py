# @brief This class is used to handle the token management in CMS
# @note  There is not need to create an object of this class as all
#        methods in this class are static
class TokenManager:

    # @brief This method returns the first available unassigned token
    # @param pysql PySql object
    # @retval TokenID When unassigned token is found
    # @retval None When all tokens are assigned
    @staticmethod
    def get_token(pysql):
        try:
            # Run the query to get the unassigned tokens
            sql_stmt = "SELECT `TokenID` \
                        FROM `Tokens` \
                        WHERE `Assigned?` = 0 \
                        LIMIT 1"
            pysql.run(sql_stmt)

            # Get the first unassigned token
            token = pysql.get_results()[0][0]

            # Update the token assigned status to true
            sql_stmt = "UPDATE `Tokens` \
                        SET `Assigned?` = true \
                        WHERE `TokenID` = %s"
            pysql.run(sql_stmt, (token, ))

            # Commit the changes
            pysql.commit()
        except IndexError:
            # Set token to None
            token = None
        except:
            # Print error
            pysql.print_error()
            # Revert the changes
            pysql.rollback()

        # Return the token found
        return token

    # @brief This method checks if the given token is assigned
    # @param pysql PySql object
    # @param token_id TokenID to be checked (string)
    # @retval 0 Token not assigned or Token invalid
    # @retval 1 Token assigned
    @staticmethod
    def is_token_assigned(pysql, token_id):
        try:
            # Get the assignment status
            sql_stmt = "SELECT `Assigned?` \
                        FROM `Tokens` \
                        WHERE `TokenID` = %s"
            pysql.run(sql_stmt, (token_id, ))

            # Return the assignment status
            return pysql.get_results()[0][0]
        except IndexError:
            return 0
        except:
            # Print error
            pysql.print_error()
            # Revert the changes
            pysql.rollback()

    # @brief This method puts the token back to the default state
    #        only if the token has no linked products and is assigned
    # @param pysql PySql object
    # @param token_id The TokenID to be returned back (string)
    @staticmethod
    def put_token(pysql, token_id):
        # Get the token details
        token_details = TokenManager.get_token_details(pysql, token_id)
        # Get the assignment status of token
        is_assigned = TokenManager.is_token_assigned(pysql, token_id)

        # If token details are not null or token not assigned
        if bool(token_details) or not is_assigned:
            return

        try:
            # Make the assigned status false and make the invoice id null
            sql_stmt = "UPDATE `Tokens` \
                        SET `Assigned?` = false, \
                            `InvoiceID` = NULL \
                        WHERE `TokenID` = %s"
            pysql.run(sql_stmt, (token_id, ))

            # Commit the changes
            pysql.commit()
        except:
            # Print error
            pysql.print_error()
            # Revert the changes
            pysql.rollback()

    # @brief This method returns the products currently added to the
    #        specified token
    # @param pysql PySql object
    # @param token_id The TokenID to be returned back (string)
    # @retval List of tuples of form (ProductID, Quantity)
    @staticmethod
    def get_token_details(pysql, token_id):
        try:
            # Get the all the products of the given token
            sql_stmt = "SELECT `ProductID`, `Quantity` \
                        FROM `TokensSelectProducts` \
                        WHERE `TokenID` = %s"
            pysql.run(sql_stmt, (token_id, ))

            return pysql.get_results()
        except:
            # Print error
            pysql.print_error()
            # Revert the changes
            pysql.rollback()

    # @brief This method returns the all the tokens assignment status
    #        specified token
    # @param pysql PySql object
    # @retval List of tuple of format (TokenID, Assigned?)
    # @retval List of tuple of format (TokenID, Assigned?)
    @staticmethod
    def get_all_tokens_status(pysql):
        try:
            # Get the all the products of the given token
            sql_stmt = "SELECT `TokenID`, `Assigned?` \
                        FROM `Tokens`"
            pysql.run(sql_stmt, (token_id, ))

            return pysql.get_results()
        except:
            # Print error
            pysql.print_error()
