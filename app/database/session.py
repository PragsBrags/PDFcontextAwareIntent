from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from models.documents import Base
from config import settings

class DatabaseConnection:
    def __init__(self, database):
        self.enabled = settings.enabled
        self.create_tables_startup = settings.create_tables
        self.engine = None
        self.session_factory = None

        if not self.enabled:
            print("Database initialization is disabled in the configuration.")
            return
        
        sql_config = {"echo": database["echo"], "future": True}
        sql_config["pool_size"] = database["pool_size"]
        sql_config["max_overflow"] = database["max_overflow"]

        self.engine = create_engine(settings.database_url, **sql_config)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)

    def create_tables(self) -> None:
        if self.engine is not None and self.create_tables_startup:
            Base.metadata.create_all(self.engine)
            
    @contextmanager
    def session(self):
        if self.session_factory is None:
            yield None
            return

        db: Session = self.session_factory()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()