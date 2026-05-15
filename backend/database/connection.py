from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.models import Base
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from config import DB_PATH

_engine = None
_SessionLocal = None


from sqlalchemy import event

def get_engine():
    global _engine
    if _engine is None:
        _engine = create_engine(
            f"sqlite:///{DB_PATH}",
            connect_args={"check_same_thread": False},
            echo=False,
        )
        
        @event.listens_for(_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            # DELETE mode is more reliable on certain cloud filesystems than WAL
            cursor.execute("PRAGMA journal_mode=DELETE")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.close()
            
        Base.metadata.create_all(_engine)
    return _engine


def get_session():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), autocommit=False, autoflush=False)
    return _SessionLocal()


def init_db():
    engine = get_engine()
    Base.metadata.create_all(engine)
    
    # Auto-seed if database is empty
    from backend.database.queries import run_query
    try:
        check = run_query("SELECT COUNT(*) as cnt FROM web_logs")
        if not check or check[0]['cnt'] == 0:
            csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "cybernova_web_logs_500k.csv")
            if os.path.exists(csv_path):
                import pandas as pd
                print(f"Database empty. Seeding from {csv_path}...")
                df = pd.read_csv(csv_path)
                df.to_sql("web_logs", con=engine, if_exists="append", index=False, chunksize=5000)
                print("Seeding complete.")
    except Exception as e:
        print(f"Auto-seed warning: {e}")
        
    # Auto-seed default users if table is empty
    try:
        user_check = run_query("SELECT COUNT(*) as cnt FROM users")
        if not user_check or user_check[0]['cnt'] == 0:
            print("Users table empty. Seeding default accounts...")
            from backend.auth.auth_manager import AuthManager
            AuthManager.register("admin", "admin@cybernova.com", "Admin@2026!", role="admin")
            AuthManager.register("analyst", "analyst@cybernova.com", "Analyst@2026!", role="analyst")
            AuthManager.register("user", "user@cybernova.com", "User@2026!", role="website_user")
            print("Default users seeded.")
    except Exception as e:
        print(f"User auto-seed warning: {e}")
        
    return engine
