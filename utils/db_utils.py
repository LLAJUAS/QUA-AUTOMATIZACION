import pymysql
from config import DB_CONFIG

class DatabaseUtils:
    @staticmethod
    def get_connection():
        """Establece conexión con la base de datos"""
        return pymysql.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            port=DB_CONFIG['port']
        )

    @staticmethod
    def verify_user_credentials(email, password):
        """Verifica si las credenciales existen en la base de datos"""
        try:
            conn = DatabaseUtils.get_connection()
            with conn.cursor() as cursor:
                sql = "SELECT id FROM users WHERE email = %s AND password = %s"
                cursor.execute(sql, (email, password))
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            print(f"Error al verificar credenciales: {str(e)}")
            return False
        finally:
            conn.close()