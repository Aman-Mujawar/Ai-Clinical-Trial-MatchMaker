from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.config import DatabaseConfig
from logger import service as logger_service

log = logger_service.get_logger(__name__)

config = DatabaseConfig()

# Create the database engines
# app db engine
engine = create_engine(config.APP_DB_URL)
# common db engine
common_db_url = config.COMMON_DB_URL
if not common_db_url or len(common_db_url) == 0:
    log.error("common_db_url is not set, using app_db_url")
    common_db_url = config.APP_DB_URL
engine_common = create_engine(common_db_url)

# Configure session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionCommon = sessionmaker(autocommit=False, autoflush=False, bind=engine_common)


# Dependency for FastAPI
def get_db():
    """
    Get a database session - App DB
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        log.error(f"get_db: Caught exception: {e}, rolling back")
        db.rollback()
        raise e
    finally:
        db.close()


def get_common_db():
    """
    Get a database session - Common DB
    """
    db = SessionCommon()
    try:
        yield db
    except Exception as e:
        log.error(f"get_common_db: Caught exception: {e}, rolling back")
        db.rollback()
        raise e
    finally:
        db.close()