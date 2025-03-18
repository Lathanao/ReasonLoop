"""
MySQL database abilities for data analysis
"""

import logging
import mysql.connector
from mysql.connector import pooling
from typing import Optional, Dict, Any, List, Tuple
import pandas as pd
import time
from config.settings import get_setting

logger = logging.getLogger(__name__)

# Connection pool for MySQL
_connection_pool = None

def get_connection_pool():
    """Initialize and return the MySQL connection pool"""
    global _connection_pool

    if _connection_pool is None:
        try:
            db_config = get_setting("DB_CONFIG")
            _connection_pool = mysql.connector.pooling.MySQLConnectionPool(
                pool_name="reasonloop_pool",
                pool_size=5,
                **db_config
            )
            logger.info("MySQL connection pool initialized")
        except Exception as e:
            logger.error(f"Error initializing MySQL connection pool: {str(e)}")
            raise

    return _connection_pool

def execute_query(query: str, params: Optional[Tuple] = None, fetch: bool = True) -> Any:
    """Execute a query and return results"""
    conn = None
    cursor = None

    try:
        pool = get_connection_pool()
        conn = pool.get_connection()
        cursor = conn.cursor(dictionary=True)

        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        if fetch:
            return cursor.fetchall()
        else:
            conn.commit()
            return cursor.rowcount

    except Exception as e:
        logger.error(f"Query execution error: {str(e)}")
        logger.error(f"Query: {query}")
        if params:
            logger.error(f"Parameters: {params}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def mysql_schema_ability(table_name: Optional[str] = None) -> str:
    """
    Analyze and return MySQL schema information
    If table_name is provided, returns detailed info for that table
    Otherwise returns overview of all tables
    """
    logger.debug(f"ABILITY CALLED: mysql-schema for table: {table_name}")
    start_time = time.time()

    try:
        if table_name:
            # Get column information
            columns = execute_query("""
                SELECT
                    COLUMN_NAME, DATA_TYPE,
                    IS_NULLABLE, COLUMN_KEY,
                    COLUMN_DEFAULT, EXTRA,
                    CHARACTER_MAXIMUM_LENGTH,
                    NUMERIC_PRECISION, NUMERIC_SCALE
                FROM INFORMATION_SCHEMA.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
                ORDER BY ORDINAL_POSITION
            """, (table_name,))

            # Get table statistics
            stats = execute_query("""
                SELECT
                    TABLE_ROWS, AVG_ROW_LENGTH,
                    DATA_LENGTH, INDEX_LENGTH
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
            """, (table_name,))

            # Get index information
            indexes = execute_query("""
                SELECT
                    INDEX_NAME, COLUMN_NAME, NON_UNIQUE,
                    SEQ_IN_INDEX, CARDINALITY
                FROM INFORMATION_SCHEMA.STATISTICS
                WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
                ORDER BY INDEX_NAME, SEQ_IN_INDEX
            """, (table_name,))

            # Format detailed table information
            result = f"Table: {table_name}\n\nColumns:\n"
            for col in columns:
                result += (f"- {col['COLUMN_NAME']} ({col['DATA_TYPE']}"
                          f"{f'({col['CHARACTER_MAXIMUM_LENGTH']})' if col['CHARACTER_MAXIMUM_LENGTH'] else ''}"
                          f") {'PRIMARY KEY' if col['COLUMN_KEY'] == 'PRI' else ''}"
                          f" {'NOT NULL' if col['IS_NULLABLE'] == 'NO' else ''}\n")

            if stats and stats[0]:
                result += f"\nStatistics:\n"
                result += f"- Approximate rows: {stats[0]['TABLE_ROWS']:,}\n"
                result += f"- Average row length: {stats[0]['AVG_ROW_LENGTH']:,} bytes\n"
                result += f"- Data size: {stats[0]['DATA_LENGTH']/1024/1024:.2f} MB\n"
                result += f"- Index size: {stats[0]['INDEX_LENGTH']/1024/1024:.2f} MB\n"

            # Format index information
            if indexes:
                result += f"\nIndexes:\n"
                current_index = None
                for idx in indexes:
                    if current_index != idx['INDEX_NAME']:
                        current_index = idx['INDEX_NAME']
                        result += f"- {current_index} ({'Non-unique' if idx['NON_UNIQUE'] else 'Unique'}):\n"
                    result += f"  - Column: {idx['COLUMN_NAME']} (Position: {idx['SEQ_IN_INDEX']})\n"

            # Get sample data
            sample_data = execute_query(f"SELECT * FROM {table_name} LIMIT 5")
            if sample_data:
                result += f"\nSample Data (5 rows):\n"
                df = pd.DataFrame(sample_data)
                result += df.to_string()

        else:
            # Get overview of all tables
            tables = execute_query("""
                SELECT
                    TABLE_NAME,
                    TABLE_ROWS,
                    DATA_LENGTH/1024/1024 as data_size_mb,
                    INDEX_LENGTH/1024/1024 as index_size_mb,
                    CREATE_TIME,
                    UPDATE_TIME
                FROM INFORMATION_SCHEMA.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
                ORDER BY TABLE_ROWS DESC
            """)

            result = "Database Schema Overview:\n\n"
            for table in tables:
                result += f"Table: {table['TABLE_NAME']}\n"
                result += f"- Approximate rows: {table['TABLE_ROWS']:,}\n"
                result += f"- Data size: {table['data_size_mb']:.2f} MB\n"
                result += f"- Index size: {table['index_size_mb']:.2f} MB\n"
                if table['CREATE_TIME']:
                    result += f"- Created: {table['CREATE_TIME']}\n"
                if table['UPDATE_TIME']:
                    result += f"- Last updated: {table['UPDATE_TIME']}\n"
                result += "\n"

            # Add database size information
            db_size = execute_query("""
                SELECT
                    SUM(data_length + index_length) / 1024 / 1024 AS size_mb
                FROM information_schema.TABLES
                WHERE table_schema = DATABASE()
            """)

            if db_size and db_size[0]['size_mb']:
                result += f"Total Database Size: {db_size[0]['size_mb']:.2f} MB\n"

        execution_time = time.time() - start_time
        logger.debug(f"MySQL schema analysis completed in {execution_time:.2f}s")

        return result

    except Exception as e:
        logger.error(f"Error in MySQL schema analysis: {str(e)}")
        return f"Error analyzing MySQL schema: {str(e)}"

def mysql_query_ability(query: str) -> str:
    """
    Execute a MySQL query and return formatted results
    Supports SELECT queries only for safety
    """
    logger.debug(f"ABILITY CALLED: mysql-query with query: {query[:100]}...")
    start_time = time.time()

    # Basic security check
    query_lower = query.strip().lower()
    if not query_lower.startswith('select'):
        return "Error: Only SELECT queries are allowed for safety reasons."

    # Additional security checks
    dangerous_keywords = ['drop', 'delete', 'update', 'insert', 'alter', 'truncate', 'create']
    for keyword in dangerous_keywords:
        if f" {keyword} " in f" {query_lower} ":
            return f"Error: Potentially dangerous keyword '{keyword}' detected in query."

    try:
        # Use pandas to execute query and format results
        pool = get_connection_pool()
        conn = pool.get_connection()

        try:
            df = pd.read_sql_query(query, conn)
        finally:
            conn.close()

        # Generate summary statistics
        summary = f"Query Results Summary:\n"
        summary += f"- Rows returned: {len(df):,}\n"
        summary += f"- Columns: {', '.join(df.columns)}\n\n"

        # Add basic statistical analysis for numeric columns
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        if len(numeric_cols) > 0:
            summary += "Numeric Column Statistics:\n"
            for col in numeric_cols:
                stats = df[col].describe()
                summary += f"\n{col}:\n"
                summary += f"- Mean: {stats['mean']:.2f}\n"
                summary += f"- Std Dev: {stats['std']:.2f}\n"
                summary += f"- Min: {stats['min']:.2f}\n"
                summary += f"- Max: {stats['max']:.2f}\n"

                # Add distribution information
                summary += f"- Distribution: "
                try:
                    # Calculate quartiles
                    q1, q2, q3 = df[col].quantile([0.25, 0.5, 0.75])
                    summary += f"Q1={q1:.2f}, Median={q2:.2f}, Q3={q3:.2f}\n"

                    # Check for outliers
                    iqr = q3 - q1
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col]
                    if len(outliers) > 0:
                        summary += f"- Outliers: {len(outliers)} values outside range [{lower_bound:.2f}, {upper_bound:.2f}]\n"
                except:
                    summary += "Could not calculate distribution\n"

        # Add categorical column analysis
        cat_cols = df.select_dtypes(include=['object']).columns
        if len(cat_cols) > 0:
            summary += "\nCategorical Column Analysis:\n"
            for col in cat_cols:
                if df[col].nunique() <= 10:  # Only show distribution for columns with few unique values
                    summary += f"\n{col} value counts:\n"
                    value_counts = df[col].value_counts().head(5)
                    for val, count in value_counts.items():
                        summary += f"- {val}: {count} ({count/len(df)*100:.1f}%)\n"
                else:
                    summary += f"\n{col}:\n"
                    summary += f"- Unique values: {df[col].nunique()}\n"
                    summary += f"- Most common: {df[col].value_counts().index[0]} ({df[col].value_counts().iloc[0]} occurrences)\n"

        # Format results as string table
        if len(df) > 0:
            summary += "\nFirst 10 rows of results:\n"
            summary += df.head(10).to_string()

            if len(df) > 10:
                summary += f"\n\n[{len(df)-10} more rows not shown]"
        else:
            summary += "\nNo results returned by query."

        execution_time = time.time() - start_time
        logger.debug(f"MySQL query completed in {execution_time:.2f}s")
        logger.debug(f"Returned {len(df)} rows")

        return summary

    except Exception as e:
        logger.error(f"Error executing MySQL query: {str(e)}")
        return f"Error executing MySQL query: {str(e)}"

# Register these abilities
if __name__ != "__main__":
    from abilities.ability_registry import register_ability
    register_ability("mysql-schema", mysql_schema_ability)
    register_ability("mysql-query", mysql_query_ability)