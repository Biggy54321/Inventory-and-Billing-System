# Import the required modules
from flask_mysqldb import MySQL
import yaml
import sys

# @brief This class can be used to connect python to sql and to run
#        commands from python to make actual changes to the database
class PySql:

    # @brief This method initializes the PySql object
    # @param flask_app Flask object to be initialized
    # @param path_to_yaml Path to the .yaml file
    def __init__(self, flask_app, path_to_yaml):

        # Load the yaml file
        db_details = yaml.load(open(path_to_yaml), Loader = yaml.FullLoader)

        # Configure the flask object
        flask_app.config['MYSQL_HOST'] = db_details['mysql_host']
        flask_app.config['MYSQL_USER'] = db_details['mysql_user']
        flask_app.config['MYSQL_PASSWORD'] = db_details['mysql_password']
        flask_app.config['MYSQL_DB'] = db_details['mysql_db']

        # Create the mysql object
        self.mysql = MySQL(flask_app)
        # Set cursor to none
        self.mysql_cursor = None
        # Field to store the last select result
        self.__last_result = None

    # @brief This function initializes the flask sql cursor
    def init(self):
        self.mysql_cursor = self.mysql.connection.cursor()

    # @brief This function deinitializes the flask sql cursor
    def deinit(self):
        self.mysql_cursor.close()

    # @brief This method executes a single sql query
    # @param sql_stmt The sql statement to be executed (string)
    # @param params The arguments for the sql_stmt (tuple)
    def run(self, sql_stmt, params = None):
        # Run the sql query
        self.mysql_cursor.execute(sql_stmt, params)

    # @brief This method executes the same sql query for each of the parameter
    # @param sql_stmt The sql statement to be executed (string)
    # @param params The arguments for the sql_stmt (list of tuples)
    def run_many(self, sql_stmt, params):
        # Run the sql query
        self.mysql_cursor.executemany(sql_stmt, params)

    # @brief This method fetches the result of the previously ran sql query
    # @return last_result The result of the previously ran sql query
    def __result(self):
        try:
            # Fetch the result
            self.__last_result = self.mysql_cursor.fetchall()
            # Save the result
            return self.__last_result
        except InterfaceError:
            # If result cannot be fetched then return the last result
            return self.__last_result

    # @brief This property can be used as a normal field of the pysql object
    #        to get the result of a previous query
    @property
    def result(self):
        return self.__result()

    # @brief This property can be used as a normal field of the pysql object
    #        to get the scalar result (i.e. single element) of a previous query
    @property
    def scalar_result(self):
        try:
            return self.__result()[0][0]
        except IndexError:
            return None

    # @brief This method updates the remote database with the updates
    #        made to the local database
    def commit(self):
         self.mysql.connection.commit()

    # @brief This method restores the local database with the remote
    #        database (hence ignoring any changes made to the local copy)
    def rollback(self):
        self.mysql.connection.rollback()

    # @brief This method calls a function wrapped around a try except block
    #        to provide robust error handling
    # @param function Function object or pointer to be called
    # @param args List of arguments to the function
    # @param commit Boolean to specify wether to commit or not
    # @retval Return value of the function
    # @retval None For error
    def run_transaction(self, function, *args, commit = True):
        try:
            # Initialize the pysql object
            self.init()

            # Execute the function
            result = function(self, *args)
        except:
            # Rollback the changes
            self.rollback()

            # Return failure
            return None
        else:
            # Commit the changes is specified
            if commit:
                self.commit()

            # Return the resutl
            return result
        finally:
            # Deinitialize the pysql object
            self.deinit()
