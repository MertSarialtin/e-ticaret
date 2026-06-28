#db_connection.py
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# .env dosyasındaki değişkenleri sisteme yüklüyoruz
load_dotenv()

def get_db_engine():
    """PostgreSQL bağlantı motorunu (engine) döndürür."""
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    
    connection_string = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    
    # engine oluşturup geri döndürüyoruz
    return create_engine(connection_string)