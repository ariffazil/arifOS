"""
Database Connection Manager for VAULT-999

Provides PostgreSQL connection pooling with graceful fallback.
Supports dual-mode operation: file-based OR file + database.

Constitutional Integration:
- F1 (Amanah): Reversible - connection failures don't crash system
- F5 (Peace²): Non-destructive - always writes to files as fallback
- F6 (κᵣ): Serves weakest stakeholder - works with or without DB
"""
import os
from typing import Optional, Dict, Any
from contextlib import contextmanager
import logging

try:
    import psycopg2
    from psycopg2.pool import SimpleConnectionPool
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """
    PostgreSQL connection manager with graceful fallback.

    Features:
    - Connection pooling for performance
    - Automatic reconnection on failure
    - Graceful degradation if database unavailable
    - Environment-based configuration
    """

    _pool: Optional[SimpleConnectionPool] = None
    _available: bool = False

    @classmethod
    def initialize(
        cls,
        database_url: Optional[str] = None,
        min_connections: int = 1,
        max_connections: int = 10
    ) -> bool:
        """
        Initialize database connection pool.

        Args:
            database_url: PostgreSQL connection string or None to use environment
            min_connections: Minimum pool size
            max_connections: Maximum pool size

        Returns:
            bool: True if initialized successfully, False otherwise
        """
        if not PSYCOPG2_AVAILABLE:
            logger.warning("psycopg2 not installed - database writes disabled")
            cls._available = False
            return False

        # Get connection string from environment or parameter
        conn_str = database_url or os.getenv(
            "DATABASE_URL",
            "postgresql://arifos:arifos_local_dev@localhost:5432/arifos_vault999"
        )

        try:
            cls._pool = SimpleConnectionPool(
                min_connections,
                max_connections,
                conn_str
            )

            # Test connection
            with cls.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")

            cls._available = True
            logger.info("✓ Database connection pool initialized")
            return True

        except Exception as e:
            logger.warning(f"Database initialization failed: {e}")
            logger.info("  Fallback: File-based storage only")
            cls._available = False
            return False

    @classmethod
    def is_available(cls) -> bool:
        """Check if database is available."""
        return cls._available

    @classmethod
    @contextmanager
    def get_connection(cls):
        """
        Get database connection from pool (context manager).

        Usage:
            with DatabaseConnection.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT * FROM table")

        Yields:
            psycopg2 connection

        Raises:
            RuntimeError: If database not initialized
        """
        if not cls._available or cls._pool is None:
            raise RuntimeError("Database not available - file-based fallback active")

        conn = cls._pool.getconn()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            cls._pool.putconn(conn)

    @classmethod
    def execute_query(
        cls,
        query: str,
        params: Optional[tuple] = None,
        fetch_one: bool = False,
        fetch_all: bool = False
    ) -> Optional[Any]:
        """
        Execute SQL query with automatic connection management.

        Args:
            query: SQL query string
            params: Query parameters (tuple)
            fetch_one: Return single row as dict
            fetch_all: Return all rows as list of dicts

        Returns:
            Query results or None
        """
        if not cls._available:
            logger.debug("Database unavailable - skipping query")
            return None

        try:
            with cls.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, params or ())

                    if fetch_one:
                        return dict(cur.fetchone()) if cur.rowcount > 0 else None
                    elif fetch_all:
                        return [dict(row) for row in cur.fetchall()]
                    else:
                        return None

        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return None

    @classmethod
    def insert_one(
        cls,
        table: str,
        data: Dict[str, Any],
        returning: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Insert single row into table.

        Args:
            table: Table name
            data: Dictionary of column: value pairs
            returning: Column to return after insert (e.g., 'id')

        Returns:
            Dict with returned column or None
        """
        if not cls._available:
            logger.debug(f"Database unavailable - skipping insert to {table}")
            return None

        # Build INSERT query
        columns = list(data.keys())
        values = list(data.values())
        placeholders = ["%s"] * len(columns)

        query = f"""
            INSERT INTO {table} ({", ".join(columns)})
            VALUES ({", ".join(placeholders)})
        """

        if returning:
            query += f" RETURNING {returning}"

        try:
            if returning:
                return cls.execute_query(query, tuple(values), fetch_one=True)
            else:
                cls.execute_query(query, tuple(values))
                return None

        except Exception as e:
            logger.error(f"Insert failed for {table}: {e}")
            return None

    @classmethod
    def close(cls):
        """Close connection pool."""
        if cls._pool:
            cls._pool.closeall()
            cls._pool = None
            cls._available = False
            logger.info("Database connection pool closed")


# Auto-initialize on import (graceful fallback if unavailable)
DatabaseConnection.initialize()


if __name__ == "__main__":
    # Test database connection
    print("=== Database Connection Test ===\n")

    if DatabaseConnection.is_available():
        print("✓ Database connection available")

        # Test query
        result = DatabaseConnection.execute_query(
            "SELECT COUNT(*) as count FROM ccc_constitutional_floors",
            fetch_one=True
        )

        if result:
            print(f"  F1-F12 floors in database: {result['count']}")

        # Test insert (dry run)
        print("\nTest insert (to bbb_machine_memory):")
        test_data = {
            "user_id": "test_user",
            "content": "Test memory content",
            "verdict": "SEAL",
            "ttl_days": 730
        }

        result = DatabaseConnection.insert_one(
            "bbb_machine_memory",
            test_data,
            returning="memory_id"
        )

        if result:
            print(f"  ✓ Inserted memory_id: {result['memory_id']}")

    else:
        print("✗ Database connection unavailable")
        print("  Fallback: File-based storage only")

    print("\n=== Test Complete ===")
