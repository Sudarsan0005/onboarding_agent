import mysql.connector
from mysql.connector import Error
import logging
from contextlib import contextmanager
from typing import Optional, List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self,DB_HOST,DB_PORT,DB_USER,DB_PASSWORD,DB_DATABASE):
        """Initialize the DatabaseManager with database credentials"""
        self.config = {
            'host': DB_HOST,
            'port': DB_PORT,
            'user': DB_USER,
            'password': DB_PASSWORD,
            'database': DB_DATABASE,
            'autocommit': False
        }

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        connection = None
        cursor = None
        try:
            connection = mysql.connector.connect(**self.config)
            cursor = connection.cursor(dictionary=True)
            yield connection, cursor
        except Error as e:
            logger.error(f"Database error: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    # MOD_SETTING table operations
    def insert_mod_setting(self, assistant_id: str=None, openai_key: str=None) -> bool:
        """Insert a new mod setting record"""
        try:
            with self.get_connection() as (conn, cursor):
                if assistant_id:
                    query = """
                    INSERT INTO mod_setting (assistant_id) 
                    VALUES (%s)
                    """
                    cursor.execute(query, assistant_id)

                if openai_key:
                    query = """
                            INSERT INTO mod_setting (openai_key) 
                            VALUES (%s)
                            """
                    cursor.execute(query, openai_key)
                conn.commit()

                return True
        except Error as e:
            logger.error(f"Error inserting mod setting: {e}")
            return False

    def get_mod_setting(self, assistant_id: str) -> Optional[Dict[str, Any]]:
        """Get mod setting by assistant_id"""
        try:
            with self.get_connection() as (conn, cursor):
                query = "SELECT * FROM mod_setting WHERE assistant_id = %s"
                cursor.execute(query, (assistant_id,))
                result = cursor.fetchone()
                return result
        except Error as e:
            logger.error(f"Error getting mod setting: {e}")
            return None

    def get_openai_key(self) -> Optional[Dict[str,Any]]:
        try:
            with self.get_connection() as (conn, cursor):
                query = "SELECT openai_key FROM mod_setting WHERE id = 1"
                cursor.execute(query)
                result = cursor.fetchone()
                return result
        except Error as e:
            logger.error(f"Error getting mod setting: {e}")
            return None
    def get_assistant_id(self) -> Optional[Dict[str,Any]]:
        try:
            with self.get_connection() as (conn, cursor):
                query = "SELECT assistant_id FROM mod_setting WHERE id = 1"
                cursor.execute(query)
                result = cursor.fetchone()
                return result
        except Error as e:
            logger.error(f"Error getting mod setting: {e}")
            return None

    def update_mod_setting(self, assistant_id: str=None, openai_key: str=None, assistant_prompt:str=None) -> bool:
        """Update mod setting openai_key"""
        try:
            with self.get_connection() as (conn, cursor):
                if assistant_id:
                    query = """
                            UPDATE mod_setting 
                            SET assistant_id = %s, updated_at = CURRENT_TIMESTAMP 
                            WHERE id = 1
                            """
                    cursor.execute(query, assistant_id)
                if openai_key:
                    query = """
                            UPDATE mod_setting 
                            SET openai_key = %s, updated_at = CURRENT_TIMESTAMP 
                            WHERE id = 1
                            """
                    cursor.execute(query,openai_key)
                if assistant_prompt:
                    query = """
                            UPDATE mod_setting 
                            SET assistant_prompt = %s, updated_at = CURRENT_TIMESTAMP 
                            WHERE id = 1
                            """
                    cursor.execute(query,assistant_prompt)
                conn.commit()

                if cursor.rowcount > 0:
                    # logger.info(f"Mod setting updated for assistant_id: {assistant_id}")
                    return True
                else:
                    # logger.warning(f"No mod setting found for assistant_id: {assistant_id}")
                    return False
        except Error as e:
            logger.error(f"Error updating mod setting: {e}")
            return False

    def delete_mod_setting(self, assistant_id: str) -> bool:
        """Delete mod setting by assistant_id"""
        try:
            with self.get_connection() as (conn, cursor):
                query = "DELETE FROM mod_setting WHERE assistant_id = %s"
                cursor.execute(query, (assistant_id,))
                conn.commit()

                if cursor.rowcount > 0:
                    logger.info(f"Mod setting deleted for assistant_id: {assistant_id}")
                    return True
                else:
                    logger.warning(f"No mod setting found for assistant_id: {assistant_id}")
                    return False
        except Error as e:
            logger.error(f"Error deleting mod setting: {e}")
            return False

    # USER_SETTING table operations
    def insert_user_setting(self, phone_no: str, thread_id: str) -> bool:
        """Insert a new user setting record"""
        try:
            with self.get_connection() as (conn, cursor):
                query = """
                INSERT INTO user_setting (phone_no, thread_id) 
                VALUES (%s, %s)
                """
                cursor.execute(query, (phone_no, thread_id))
                conn.commit()
                logger.info(f"User setting inserted for phone_no: {phone_no}")
                return True
        except Error as e:
            logger.error(f"Error inserting user setting: {e}")
            return False

    def get_user_setting(self, phone_no: str) -> Optional[Dict[str, Any]]:
        """Get user setting by phone_no"""
        try:
            with self.get_connection() as (conn, cursor):
                query = "SELECT * FROM user_setting WHERE phone_no = %s"
                cursor.execute(query, (phone_no,))
                result = cursor.fetchone()
                return result
        except Error as e:
            logger.error(f"Error getting user setting: {e}")
            return None

    def update_user_setting(self, phone_no: str, thread_id: str) -> bool:
        """Update user setting thread_id"""
        try:
            with self.get_connection() as (conn, cursor):
                query = """
                UPDATE user_setting 
                SET thread_id = %s, updated_at = CURRENT_TIMESTAMP 
                WHERE phone_no = %s
                """
                cursor.execute(query, (thread_id, phone_no))
                conn.commit()

                if cursor.rowcount > 0:
                    logger.info(f"User setting updated for phone_no: {phone_no}")
                    return True
                else:
                    logger.warning(f"No user setting found for phone_no: {phone_no}")
                    return False
        except Error as e:
            logger.error(f"Error updating user setting: {e}")
            return False

    def delete_user_setting(self, phone_no: str) -> bool:
        """Delete user setting by phone_no"""
        try:
            with self.get_connection() as (conn, cursor):
                query = "DELETE FROM user_setting WHERE phone_no = %s"
                cursor.execute(query, (phone_no,))
                conn.commit()

                if cursor.rowcount > 0:
                    logger.info(f"User setting deleted for phone_no: {phone_no}")
                    return True
                else:
                    logger.warning(f"No user setting found for phone_no: {phone_no}")
                    return False
        except Error as e:
            logger.error(f"Error deleting user setting: {e}")
            return False

    # USER_CONVERSATION table operations
    def insert_user_conversation(self, actor: str, phone_no: str,
                                 message: Optional[str] = None,
                                 doc_type: Optional[str] = None,
                                 doc_path: Optional[str] = None) -> bool:
        """Insert a new user conversation record"""
        try:
            with self.get_connection() as (conn, cursor):
                query = """
                INSERT INTO user_conversation (actor, phone_no, message, doc_type, doc_path) 
                VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(query, (actor, phone_no, message, doc_type, doc_path))
                conn.commit()
                logger.info(f"User conversation inserted for phone_no: {phone_no}, actor: {actor}")
                return True
        except Error as e:
            logger.error(f"Error inserting user conversation: {e}")
            return False

    def get_user_conversations(self, phone_no: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get user conversations by phone_no with optional limit"""
        try:
            with self.get_connection() as (conn, cursor):
                query = """
                SELECT * FROM user_conversation 
                WHERE phone_no = %s 
                ORDER BY created_at DESC 
                LIMIT %s
                """
                cursor.execute(query, (phone_no, limit))
                results = cursor.fetchall()
                return results if results else []
        except Error as e:
            logger.error(f"Error getting user conversations: {e}")
            return []

    def get_conversation_by_id(self, conversation_id: int) -> Optional[Dict[str, Any]]:
        """Get specific conversation by ID"""
        try:
            with self.get_connection() as (conn, cursor):
                query = "SELECT * FROM user_conversation WHERE id = %s"
                cursor.execute(query, (conversation_id,))
                result = cursor.fetchone()
                return result
        except Error as e:
            logger.error(f"Error getting conversation by ID: {e}")
            return None

    def delete_user_conversation(self, conversation_id: int) -> bool:
        """Delete user conversation by ID"""
        try:
            with self.get_connection() as (conn, cursor):
                query = "DELETE FROM user_conversation WHERE id = %s"
                cursor.execute(query, (conversation_id,))
                conn.commit()

                if cursor.rowcount > 0:
                    logger.info(f"User conversation deleted with ID: {conversation_id}")
                    return True
                else:
                    logger.warning(f"No conversation found with ID: {conversation_id}")
                    return False
        except Error as e:
            logger.error(f"Error deleting user conversation: {e}")
            return False

    def delete_all_user_conversations(self, phone_no: str) -> bool:
        """Delete all conversations for a specific phone number"""
        try:
            with self.get_connection() as (conn, cursor):
                query = "DELETE FROM user_conversation WHERE phone_no = %s"
                cursor.execute(query, (phone_no,))
                conn.commit()

                deleted_count = cursor.rowcount
                logger.info(f"Deleted {deleted_count} conversations for phone_no: {phone_no}")
                return True
        except Error as e:
            logger.error(f"Error deleting user conversations: {e}")
            return False

    # Utility methods
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.get_connection() as (conn, cursor):
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                logger.info("Database connection test successful")
                return result is not None
        except Error as e:
            logger.error(f"Database connection test failed: {e}")
            return False

    def get_table_count(self, table_name: str) -> int:
        """Get count of records in a table"""
        try:
            with self.get_connection() as (conn, cursor):
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                result = cursor.fetchone()
                return result['count'] if result else 0
        except Error as e:
            logger.error(f"Error getting table count: {e}")
            return 0


# Usage example
if __name__ == "__main__":
    # Initialize database manager
    db_manager = DatabaseManager()

    # Test connection
    if db_manager.test_connection():
        print("Database connection successful!")
        key = db_manager.get_openai_key()
        print(key)
        # Example operations
        # print("\n--- Example Operations ---")

        # Insert mod setting
    #     db_manager.insert_mod_setting("assistant_123", "sk-1234567890abcdef")
    #
    #     # Insert user setting
    #     db_manager.insert_user_setting("+1234567890", "thread_abc123")
    #
    #     # Insert user conversation
    #     db_manager.insert_user_conversation(
    #         actor="user",
    #         phone_no="+1234567890",
    #         message="Hello, how are you?",
    #         doc_type=None,
    #         doc_path=None
    #     )
    #
    #     # Get user conversations
    #     conversations = db_manager.get_user_conversations("+1234567890")
    #     print(f"Found {len(conversations)} conversations")
    #
    #     # Get table counts
    #     print(f"Mod settings count: {db_manager.get_table_count('mod_setting')}")
    #     print(f"User settings count: {db_manager.get_table_count('user_setting')}")
    #     print(f"User conversations count: {db_manager.get_table_count('user_conversation')}")
    #
    # else:
    #     print("Database connection failed!")