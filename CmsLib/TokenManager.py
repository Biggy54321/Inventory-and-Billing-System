# @brief This class is used to handle the token management in CMS
# @note  There is not need to create an object of this class as all
#        methods in this class are static
class TokenManager:

    # @brief This method adds a token to the list of tokens with default state
    # @param PySql object
    # @retval token_id TokenID of the newly added token
    # @retval 1 New token cannot be added
    @staticmethod
    def __add_token(pysql):
        # Get all the current token ids
        sql_stmt = "SELECT `TokenID` \
                    FROM `Tokens`"
        pysql.run(sql_stmt)
        tokens = [int(token[0][4:]) for token in pysql.result]

        # For every token in the existing list of tokens
        token_i = 0
        for token in tokens:
            # If the token 'i' is not in the list
            if token_i != token:
                break
            token_i += 1

        # Check if token number to be added is out of limit
        if token_i >= 100:
            return 1

        # Create the token id
        token_id = "TOK-" + format(token_i, "02d")

        # Add the token with number 'i'
        sql_stmt = "INSERT INTO `Tokens` (`TokenID`) \
                    VALUES (%s)"
        pysql.run(sql_stmt, (token_id, ))

        return token_id

    # @brief This method removes a token from the list of tokens which
    #        is in default state only
    # @param PySql object
    # @param TokenID (string)
    # @retval 0 Token removed successfully
    # @retval 1 Token has products
    # @retval 2 Token is already assigned
    # @retval 3 Token not found
    @staticmethod
    def __remove_token(pysql, token_id):
        # Get the token product status
        has_products = TokenManager._TokenManager__token_has_products(pysql, token_id)
        # Get the assignment status of token
        is_assigned = TokenManager._TokenManager__is_token_assigned(pysql, token_id)

        # If token has products
        if has_products:
            return 1
        # If token is already assigned
        if is_assigned:
            return 2
        # Check if token exists
        if is_assigned == None:
            return 3

        # Remove the token
        sql_stmt = "DELETE \
                    FROM `Tokens` \
                    WHERE `TokenID` = %s"
        pysql.run(sql_stmt, (token_id, ))

        return 0

    # @brief This method returns the first available unassigned token
    # @param pysql PySql object
    # @retval TokenID (string)
    # @retval None Free token not found
    @staticmethod
    def __get_token(pysql):
        # Run the query to get the unassigned tokens
        sql_stmt = "SELECT `TokenID` \
                    FROM `Tokens` \
                    WHERE `Assigned?` = 0 \
                    LIMIT 1"
        pysql.run(sql_stmt)

        # Get the first unassigned token
        token_id = pysql.scalar_result

        # If return value is none
        if not token_id:
            return None

        # Update the token assigned status to true
        sql_stmt = "UPDATE `Tokens` \
                    SET `Assigned?` = true \
                    WHERE `TokenID` = %s"
        pysql.run(sql_stmt, (token_id, ))

        # Return the token found
        return token_id

    # @brief This method puts the token back to the default state
    #        only if the token has no linked products and is assigned
    # @param pysql PySql object
    # @param token_id TokenID (string)
    # @retval 0 Token returned successfully
    # @retval 1 Token has products
    # @retval 2 Token is already not assigned
    # @retval 3 Token not found
    @staticmethod
    def __put_token(pysql, token_id):
        # Get the token product status
        has_products = TokenManager._TokenManager__token_has_products(pysql, token_id)
        # Get the assignment status of token
        is_assigned = TokenManager._TokenManager__is_token_assigned(pysql, token_id)

        # If token has products
        if has_products:
            return 1
        # If token is already not assigned
        if is_assigned == 0:
            return 2
        # If token is not existing
        if is_assigned == None:
            return 3

        # Make the assigned status false and make the invoice id null
        sql_stmt = "UPDATE `Tokens` \
                    SET `Assigned?` = false, \
                        `InvoiceID` = NULL \
                    WHERE `TokenID` = %s"
        pysql.run(sql_stmt, (token_id, ))

        return 0

    # @brief This method checks if the given token is assigned
    # @param pysql PySql object
    # @param token_id TokenID (string)
    # @retval 0 Token not assigned
    # @retval 1 Token assigned
    # @retval None TokenID not found
    @staticmethod
    def __is_token_assigned(pysql, token_id):
        # Get the assignment status
        sql_stmt = "SELECT `Assigned?` \
                    FROM `Tokens` \
                    WHERE `TokenID` = %s"
        pysql.run(sql_stmt, (token_id, ))

        # Get the assignment status
        is_assigned = pysql.scalar_result

        return is_assigned

    # @brief This method checks if the given token is assigned
    # @param pysql PySql object
    # @param token_id TokenID (string)
    # @retval Number of products linked with the token
    @staticmethod
    def __token_has_products(pysql, token_id):
        # Get the product status
        sql_stmt = "SELECT COUNT(*) \
                    FROM `TokensSelectProducts` \
                    WHERE `TokenID` = %s"
        pysql.run(sql_stmt, (token_id, ))

        # Get the result
        no_of_products = pysql.scalar_result

        return no_of_products

    # @brief This method returns the products currently added to the
    #        specified token
    # @param pysql PySql object
    # @param token_id TokenID (string)
    # @retval (ProductID, Quantity) (list of tuples)
    @staticmethod
    def __get_token_details(pysql, token_id):
        # Get the all the products of the given token
        sql_stmt = "SELECT `ProductID`, `Quantity` \
                    FROM `TokensSelectProducts` \
                    WHERE `TokenID` = %s"
        pysql.run(sql_stmt, (token_id, ))

        # Get the token product details
        token_details = pysql.result

        return token_details

    # @brief This method returns the all the tokens assignment status
    #        specified token
    # @param pysql PySql object
    # @retval (TokenID, Assigned?) (list of tuples)
    @staticmethod
    def __get_all_tokens_status(pysql):
        # Get the all the products of the given token
        sql_stmt = "SELECT `TokenID`, `Assigned?` \
                    FROM `Tokens`"
        pysql.run(sql_stmt)

        # Get the token statuses
        token_status = pysql.result

        return token_status

    # @ref __add_token
    @staticmethod
    def add_token(pysql):
        return pysql.run_transaction(TokenManager.__add_token)

    # @ref __remove_token
    @staticmethod
    def remove_token(pysql, token_id):
        return pysql.run_transaction(TokenManager.__remove_token,
                                     token_id)

    # @ref __get_token
    @staticmethod
    def get_token(pysql):
        return pysql.run_transaction(TokenManager.__get_token)

    # @ref __put_token
    @staticmethod
    def put_token(pysql, token_id):
        return pysql.run_transaction(TokenManager.__put_token,
                                     token_id)

    # @ref __is_token_assigned
    @staticmethod
    def is_token_assigned(pysql, token_id):
        return pysql.run_transaction(TokenManager.__is_token_assigned,
                                     token_id,
                                     commit = False)

    @staticmethod
    def token_has_products(pysql, token_id):
        return pysql.run_transaction(TokenManager.__token_has_products,
                                     token_id,
                                     commit = False)

    # @ref __get_all_tokens_status
    @staticmethod
    def get_all_tokens_status(pysql):
        return pysql.run_transaction(TokenManager.__get_all_tokens_status,
                                     commit = False)

    # @ref __get_token_details
    @staticmethod
    def get_token_details(pysql, token_id):
        return pysql.run_transaction(TokenManager.__get_token_details,
                                     token_id,
                                     commit = False)
