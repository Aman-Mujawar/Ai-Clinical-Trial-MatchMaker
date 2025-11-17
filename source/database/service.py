from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from source.database.config import db_config
from source.logger import service as logger_service

log = logger_service.get_logger(__name__)

# -------------------------
# Create database engines
# -------------------------
# App DB engine
engine = create_engine(db_config.database_url)

# Common DB engine (optional, fallback to app DB)
common_db_url = db_config.common_database_url
if not common_db_url or common_db_url.strip() == "":
    log.warning("COMMON_DB_URL is not set, using APP_DB_URL as fallback")
    common_db_url = db_config.database_url

engine_common = create_engine(common_db_url)

# -------------------------
# Session factories
# -------------------------
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
SessionCommon = sessionmaker(autocommit=False, autoflush=False, bind=engine_common)

# -------------------------
# Dependency for FastAPI
# -------------------------
def get_db():
    """
    Get a database session - App DB
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        log.error(f"get_db: Exception occurred, rolling back - {e}")
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
        log.error(f"get_common_db: Exception occurred, rolling back - {e}")
        db.rollback()
        raise e
    finally:
        db.close()
