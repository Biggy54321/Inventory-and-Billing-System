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
        # Create mysql cursor object
        self.mysql_cursor = self.mysql.connection.cursor()
        # Field to store the last select result
        self.last_result = None

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
    def get_results(self):
        try:
            # Fetch the result
            self.last_result = self.mysql_cursor.fetchall()
            # Save the result
            return self.last_result
        except InterfaceError:
            # If result cannot be fetched then return the last result
            return self.last_result

    # @brief This method updates the remote database with the updates
    #        made to the local database
    def commit(self):
         self.mysql.connection.commit()

    # @brief This method restores the local database with the remote
    #        database (hence ignoring any changes made to the local copy)
    def rollback(self):
        self.mysql.connection.rollback()

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
