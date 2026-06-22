# Módulo de conexão com o banco de dados
# Responsável por configurar a conexão com MySQL usando SQLAlchemy

from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os


def get_connection():
    """
    Cria e retorna uma conexão com o banco de dados MySQL usando URL.create.
    
    Returns:
        engine: Engine do SQLAlchemy para conexão com o banco
    """
    # Carrega variáveis de ambiente
    load_dotenv()
    
    # Configurações de conexão
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')
    
    # Cria a URL de conexão usando URL.create (lida melhor com caracteres especiais)
    connection_url = URL.create(
        drivername="mysql+pymysql",
        username=db_user,
        password=db_password,
        host=db_host,
        port=int(db_port),
        database=db_name
    )
    
    # Cria o engine de conexão
    engine = create_engine(connection_url)
    
    return engine


def get_session():
    """
    Cria e retorna uma sessão do SQLAlchemy.
    
    Returns:
        Session: Sessão do SQLAlchemy para operações no banco
    """
    engine = get_connection()
    Session = sessionmaker(bind=engine)
    session = Session()
    
    return session
