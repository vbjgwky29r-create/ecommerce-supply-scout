import os
import time
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
import logging
logger = logging.getLogger(__name__)

MAX_RETRY_TIME = 20  # 连接最大重试时间（秒）
# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

def get_db_url() -> str:
    """Build database URL from environment."""
    url = os.getenv("PGDATABASE_URL") or ""
    if url is not None and url != "":
        return url
    from coze_workload_identity import Client
    try:
        client = Client()
        env_vars = client.get_project_env_vars()
        client.close()
        for env_var in env_vars:
            if env_var.key == "PGDATABASE_URL":
                url = env_var.value.replace("'", "'\\''")
                return url
    except Exception as e:
        logger.error(f"Error loading PGDATABASE_URL: {e}")
        raise e
    finally:
        if url is None or url == "":
            logger.error("PGDATABASE_URL is not set")
    return url
_engine = None
_SessionLocal = None

def _create_engine_with_retry():
    url = get_db_url()
    if url is None or url == "":
        logger.error("PGDATABASE_URL is not set")
        raise ValueError("PGDATABASE_URL is not set")
    size = 5
    overflow = 10
    recycle = 600
    timeout = 30
    engine = create_engine(
        url,
        pool_size=size,
        max_overflow=overflow,
        pool_pre_ping=True,
        pool_recycle=recycle,
        pool_timeout=timeout,
        connect_args={
            "connect_timeout": 10
        },
        echo=False
    )
    # 验证连接，带重试
    start_time = time.time()
    last_error = None
    while time.time() - start_time < MAX_RETRY_TIME:
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return engine
        except OperationalError as e:
            last_error = e
            elapsed = time.time() - start_time
            logger.warning(f"Database connection failed, retrying... (elapsed: {elapsed:.1f}s)")
            time.sleep(min(1, MAX_RETRY_TIME - elapsed))
    logger.error(f"Database connection failed after {MAX_RETRY_TIME}s: {last_error}")
    raise last_error  # pyright: ignore [reportGeneralTypeIssues]

def get_engine():
    global _engine
    if _engine is None:
        _engine = _create_engine_with_retry()
    return _engine

def get_sessionmaker():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal

def get_session():
    """获取数据库会话，每次都创建新会话"""
    session = get_sessionmaker()()
    try:
        # 测试连接是否有效
        session.execute(text("SELECT 1"))
    except Exception as e:
        session.close()
        # 如果连接失败，重新创建会话
        session = get_sessionmaker()()
    return session

def execute_with_retry(func, max_retries=3, retry_delay=1):
    """
    带重试机制的数据库操作执行器

    Args:
        func: 要执行的函数，接受 db 参数，返回一个字典或简单值
        max_retries: 最大重试次数
        retry_delay: 重试延迟（秒）

    Returns:
        函数执行结果（字典或简单值）
    """
    from sqlalchemy.exc import OperationalError, DisconnectionError, InterfaceError, DatabaseError
    import logging
    logger = logging.getLogger(__name__)

    last_error = None
    for attempt in range(max_retries + 1):
        db = None
        try:
            db = get_session()
            result = func(db)

            # 确保在返回前关闭会话
            if db:
                try:
                    db.close()
                except Exception:
                    pass

            return result
        except (OperationalError, DisconnectionError, InterfaceError) as e:
            last_error = e
            error_msg = str(e).lower()

            # 检查是否是连接错误
            if any(keyword in error_msg for keyword in [
                'terminating connection',
                'server closed the connection',
                'connection already closed',
                'could not connect',
                'connection refused'
            ]):
                logger.warning(f"Database connection error on attempt {attempt + 1}: {e}")

                # 关闭失败的会话
                if db:
                    try:
                        db.close()
                    except Exception:
                        pass

                # 如果不是最后一次尝试，等待并重试
                if attempt < max_retries:
                    import time
                    time.sleep(retry_delay * (attempt + 1))  # 指数退避
                    continue

            # 其他错误直接抛出
            raise
        except DatabaseError as e:
            last_error = e
            logger.error(f"Database error: {e}")

            # 关闭会话
            if db:
                try:
                    db.close()
                except Exception:
                    pass

            raise
        except Exception as e:
            last_error = e
            logger.error(f"Unexpected error: {e}")

            # 关闭会话
            if db:
                try:
                    db.close()
                except Exception:
                    pass

            raise

    # 所有重试都失败
    if last_error:
        raise last_error
    raise Exception("Database operation failed after retries")

__all__ = [
    "get_db_url",
    "get_engine",
    "get_sessionmaker",
    "get_session",
    "execute_with_retry",
]
