import mysql.connector
import os
from mysql.connector import Error
import logging
from dotenv import load_dotenv
load_dotenv()

HOST= os.getenv("DB_host")
PORT=os.getenv("DB_port")
USER=os.getenv("DB_user")
PASSWORD=os.getenv("DB_password")
DATABASE=os.getenv("DB_database")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SchemaCreator:
    def __init__(self):
        """Initialize the SchemaCreator with database credentials"""
        self.config = {
            'host': HOST,
            'port': PORT,
            'user': USER,
            'password': PASSWORD,
            'database': DATABASE
        }
        self.connection = None
        self.cursor = None

    def connect_to_database(self):
        """Establish connection to MySQL database"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
                logger.info("Successfully connected to MySQL database")
                return True
        except Error as e:
            logger.error(f"Error connecting to MySQL database: {e}")
            return False

    def create_database_if_not_exists(self, database_name):
        """Create database if it doesn't exist"""
        try:
            # Connect without specifying database
            temp_config = self.config.copy()
            del temp_config['database']
            temp_connection = mysql.connector.connect(**temp_config)
            temp_cursor = temp_connection.cursor()

            temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {database_name}")
            logger.info(f"Database '{database_name}' created or already exists")

            temp_cursor.close()
            temp_connection.close()

            # Update config with database name
            self.config['database'] = database_name

        except Error as e:
            logger.error(f"Error creating database: {e}")

    def table_exists(self, table_name):
        """Check if a table exists in the database"""
        try:
            query = """
            SELECT COUNT(*)
            FROM information_schema.tables 
            WHERE table_schema = %s AND table_name = %s
            """
            self.cursor.execute(query, (self.config['database'], table_name))
            result = self.cursor.fetchone()
            return result[0] > 0
        except Error as e:
            logger.error(f"Error checking if table exists: {e}")
            return False

    def create_mod_setting_table(self):
        """Create mod_setting table if it doesn't exist"""
        table_name = 'mod_setting'

        if self.table_exists(table_name):
            logger.info(f"Table '{table_name}' already exists. Skipping creation.")
            return True

        try:
            create_table_query = """
           CREATE TABLE mod_setting (
    id INT AUTO_INCREMENT PRIMARY KEY,
    assistant_id VARCHAR(255) UNIQUE,
    openai_key VARCHAR(500) NOT NULL,
    assistant_prompt TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)   
            """
            self.cursor.execute(create_table_query)
            logger.info(f"Table '{table_name}' created successfully")
            return True

        except Error as e:
            logger.error(f"Error creating table '{table_name}': {e}")
            return False

    def create_user_setting_table(self):
        """Create user_setting table if it doesn't exist"""
        table_name = 'user_setting'

        if self.table_exists(table_name):
            logger.info(f"Table '{table_name}' already exists. Skipping creation.")
            return True

        try:
            create_table_query = """
            CREATE TABLE user_setting (
                id INT AUTO_INCREMENT PRIMARY KEY,
                phone_no VARCHAR(20) NOT NULL UNIQUE,
                thread_id VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """
            self.cursor.execute(create_table_query)
            logger.info(f"Table '{table_name}' created successfully")
            return True

        except Error as e:
            logger.error(f"Error creating table '{table_name}': {e}")
            return False

    def create_twilio_setting_table(self):
        """Create user_setting table if it doesn't exist"""
        table_name = 'twilio_setting'

        if self.table_exists(table_name):
            logger.info(f"Table '{table_name}' already exists. Skipping creation.")
            return True

        try:
            create_table_query = """
            CREATE TABLE twilio (
                id INT AUTO_INCREMENT PRIMARY KEY,
                twilio_no VARCHAR(20) NOT NULL UNIQUE,
                account_sid VARCHAR(255) NOT NULL,
                auth_token VARCHAR(255) NOT NULL
            )
            """
            self.cursor.execute(create_table_query)
            logger.info(f"Table '{table_name}' created successfully")
            return True

        except Error as e:
            logger.error(f"Error creating table '{table_name}': {e}")
            return False

    def create_user_conversation_table(self):
        """Create user_conversation table if it doesn't exist"""
        table_name = 'user_conversation'

        if self.table_exists(table_name):
            logger.info(f"Table '{table_name}' already exists. Skipping creation.")
            return True

        try:
            create_table_query = """
            CREATE TABLE user_conversation (
                id INT AUTO_INCREMENT PRIMARY KEY,
                actor VARCHAR(50) NOT NULL,
                phone_no VARCHAR(20) NOT NULL,
                message TEXT DEFAULT NULL,
                doc_type VARCHAR(100) DEFAULT NULL,
                doc_path VARCHAR(500) DEFAULT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                INDEX idx_phone_no (phone_no),
                INDEX idx_actor (actor)
            )
            """
            self.cursor.execute(create_table_query)
            logger.info(f"Table '{table_name}' created successfully")
            return True

        except Error as e:
            logger.error(f"Error creating table '{table_name}': {e}")
            return False

    def create_all_tables(self, database_name='your_database_name'):
        """Create all tables in the schema"""
        try:
            # Create database if not exists
            self.create_database_if_not_exists(database_name)

            # Connect to database
            if not self.connect_to_database():
                return False

            # Create all tables
            tables_created = []

            if self.create_mod_setting_table():
                tables_created.append('mod_setting')

            if self.create_user_setting_table():
                tables_created.append('user_setting')

            if self.create_user_conversation_table():
                tables_created.append('user_conversation')

            # Commit changes
            self.connection.commit()
            logger.info(f"Schema creation completed. Tables processed: {tables_created}")
            return True

        except Error as e:
            logger.error(f"Error in schema creation: {e}")
            if self.connection:
                self.connection.rollback()
            return False

        finally:
            self.close_connection()

    def close_connection(self):
        """Close database connection"""
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
                logger.info("Database connection closed")
        except Error as e:
            logger.error(f"Error closing connection: {e}")


# Usage example
if __name__ == "__main__":
    schema_creator = SchemaCreator()

    # Create all tables
    success = schema_creator.create_all_tables(DATABASE)  # Replace with your database name

    if success:
        print("Schema creation completed successfully!")
    else:
        print("Schema creation failed. Check the logs for details.")