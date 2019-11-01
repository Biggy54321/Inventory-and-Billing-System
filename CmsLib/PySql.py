# Import the required modules
from mysql.connector import connect, ProgrammingError, InterfaceError
import sys

# @brief This class can be used to connect python to sql and to run
#        commands from python to make actual changes to the database
class PySql:

    # @brief This method initializes the PySql object
    # @param user_name Host user name
    # @param pass_word Host password
    # @param db_name Database name
    # @param host_name Host server name
    def __init__(self, user_name, pass_word, db_name, host_name = "localhost"):
        self.user_name = user_name
        self.__pass_word = pass_word
        self.db_name = db_name
        self.host_name = host_name
        self.database = None
        self.cursor = None
        self.last_result = None

    # @brief This method connects python to mysql and initializes the handle
    def connect_py_sql(self):
        try:
            # Connect to the mysql database
            self.database = connect(host = self.host_name,
                                    user = self.user_name,
                                    passwd = self.__pass_word,
                                    db = self.db_name,)
            # Create the mysql cursor to execute queries
            self.cursor = self.database.cursor()
            # Set autocommit to false
            # self.database.autocommit(False)
        except InterfaceError:
            # Signal the user
            print("** Host name incorrect")
            sys.exit()
        except ProgrammingError:
            # Signal the user
            print("** User name, Password or Database name incorrect")
            sys.exit()

    # @brief This method executes a single sql query
    # @param sql_stmt The sql statement to be executed (string)
    # @param params The arguments for the sql_stmt (tuple)
    def run(self, sql_stmt, params = None):
        # Run the sql query
        self.cursor.execute(sql_stmt, params)

    # @brief This method executes the same sql query for each of the parameter
    # @param sql_stmt The sql statement to be executed (string)
    # @param params The arguments for the sql_stmt (list of tuples)
    def run_many(self, sql_stmt, params):
        # Run the sql query
        self.cursor.executemany(sql_stmt, params)

    # @brief This method fetches the result of the previously ran sql query
    # @return last_result The result of the previously ran sql query
    def get_results(self):
        try:
            # Fetch the result
            self.last_result = self.cursor.fetchall()
            # Save the result
            return self.last_result
        except InterfaceError:
            # If result cannot be fetched then return the last result
            return self.last_result

    # @brief This method updates the remote database with the updates
    #        made to the local database
    def commit(self):
         self.database.commit()

    # @brief This method restores the local database with the remote
    #        database (hence ignoring any changes made to the local copy)
    def rollback(self):
        self.database.rollback()

    # @brief This method indicates the error that has been raised
    def print_error(self):
        # Get the traceback
        tb = sys.exc_info()[2]

        # Get the filename
        filename = tb.tb_frame.f_code.co_filename

        # Get the line number
        lineno = tb.tb_lineno

        # Print the line number as error
        print("** Error occurred at line number {} in file {}".format(lineno, filename))

    # @brief This method returns the host server name
    # @return host_name The host server name
    def get_host_name(self):
        return self.host_name

    # @brief This method returns the host user name
    # @return user_name The host user name
    def get_user_name(self):
        return self.user_name

    # @brief This method returns the database name
    # @return db_name The database name
    def get_database_name(self):
        return self.db_name
