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
            connect_args={
                "check_same_thread": False,
                "timeout": 30,          # wait up to 30s for a lock to clear
            },
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False,
        )
        
        @event.listens_for(_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")      # write-ahead log
            cursor.execute("PRAGMA synchronous=NORMAL")    # safe + fast
            cursor.execute("PRAGMA busy_timeout=30000")    # 30s lock wait
            cursor.execute("PRAGMA cache_size=-64000")     # 64MB cache
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
        
    return engine
