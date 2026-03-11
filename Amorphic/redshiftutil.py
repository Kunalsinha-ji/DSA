"""
This file has all the common functions that are related to redshift.
"""
# Here escape_string method of pymysql module is used
# to sanitise the input parameters passed in sql query statements
# in order to avoid SQL Injection vulnerabilities.

from __future__ import print_function  # Python 2/3 compatibility

import sys
import os
import string
import random
from datetime import datetime, timedelta
import time
import json
import re
import signal
import boto3
from loggingUtil import LOGGER
import errorUtil
from commonUtil import get_ssm_parameter
# pylint: disable=import-outside-toplevel
# pylint: disable=consider-iterating-dictionary


EVENT_INFO = errorUtil.EVENT_INFO
# REDSHIFT_TABLE_PERMISSIONS = ['INSERT', 'DELETE', 'UPDATE', 'REFERENCES']
REDSHIFT_TABLE_PERMISSIONS = {
    "owner" : ['INSERT', 'DELETE', 'UPDATE', 'REFERENCES'],
    "editor" : ['INSERT', 'DELETE', 'UPDATE', 'REFERENCES']
}

class TimeBounder():
    """
    Calling a function in a specified time.
    If you call it several times, any previously scheduled alarm
    will be canceled (only one alarm can be scheduled at any time).
    """
    def __init__(self, sec):
        self.sec = sec

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.timeout_handler)
        signal.alarm(self.sec)
        return self

    def __exit__(self, *args):
        signal.alarm(0)  # disable alarm

    def timeout_handler(self, *args):
        """
        Timed out before completing the operation
        """
        raise Exception("operation timed out after {} seconds".format(self.sec))

#https://docs.aws.amazon.com/redshift/latest/dg/r_pg_keywords.html
REDSHIFT_RESERVED_KEYWORDS = ['AES128', 'AES256', 'ALL', 'ALLOWOVERWRITE', 'ANALYSE', 'ANALYZE', 'AND', 'ANY', 'ARRAY',
'AS', 'ASC', 'AUTHORIZATION', 'AZ64', 'BACKUP', 'BETWEEN', 'BINARY', 'BLANKSASNULL', 'BOTH', 'BYTEDICT', 'BZIP2', 'CASE',
'CAST', 'CHECK', 'COLLATE', 'COLUMN', 'CONSTRAINT', 'CREATE', 'CREDENTIALS', 'CROSS', 'CURRENT_DATE', 'CURRENT_TIME',
'CURRENT_TIMESTAMP', 'CURRENT_USER', 'CURRENT_USER_ID', 'DEFAULT', 'DEFERRABLE', 'DEFLATE', 'DEFRAG', 'DELTA', 'DELTA32K',
'DESC', 'DISABLE', 'DISTINCT', 'DO', 'ELSE', 'EMPTYASNULL', 'ENABLE', 'ENCODE', 'ENCRYPT', 'ENCRYPTION', 'END', 'EXCEPT',
'EXPLICIT', 'FALSE', 'FOR', 'FOREIGN', 'FREEZE', 'FROM', 'FULL', 'GLOBALDICT256', 'GLOBALDICT64K', 'GRANT', 'GROUP',
'GZIP', 'HAVING', 'IDENTITY', 'IGNORE', 'ILIKE', 'IN', 'INITIALLY', 'INNER', 'INTERSECT', 'INTO', 'IS', 'ISNULL', 'JOIN',
'LANGUAGE', 'LEADING', 'LEFT', 'LIKE', 'LIMIT', 'LOCALTIME', 'LOCALTIMESTAMP', 'LUN', 'LUNS', 'LZO', 'LZOP', 'MINUS',
'MOSTLY16', 'MOSTLY32', 'MOSTLY8', 'NATURAL', 'NEW', 'NOT', 'NOTNULL', 'NULL', 'NULLS', 'OFF', 'OFFLINE', 'OFFSET',
'OID', 'OLD', 'ON', 'ONLY', 'OPEN', 'OR', 'ORDER', 'OUTER', 'OVERLAPS', 'PARALLEL', 'PARTITION', 'PERCENT',
'PERMISSIONS', 'PIVOT', 'PLACING', 'PRIMARY', 'PUBLIC', 'RAW', 'READRATIO', 'RECOVER', 'REFERENCES', 'RESPECT',
'REJECTLOG', 'RESORT', 'RESTORE', 'RIGHT', 'SELECT', 'SESSION_USER', 'SIMILAR', 'SNAPSHOT', 'SOME', 'SYSDATE', 'SYSTEM','TABLE', 'TAG', 'TDES', 'TEXT255', 'TEXT32K', 'THEN', 'TIMESTAMP', 'TO', 'TOP', 'TRAILING', 'TRUE', 'TRUNCATECOLUMNS',
'UNION', 'UNIQUE', 'UNNEST', 'UNPIVOT', 'USER', 'USING', 'VERBOSE', 'WALLET', 'WHEN', 'WHERE', 'WITH', 'WITHOUT']

#search pattern expressions for amorphic supported data types
DATA_TYPE_PATTERNS = {
    "INTEGER": r"^\s*INTEGER\s*$",
    "SMALLINT": r"^\s*SMALLINT\s*$",
    "BIGINT": r"^\s*BIGINT\s*$",
    "REAL": r"^\s*REAL\s*$",
    "DOUBLE PRECISION": r"^\s*DOUBLE PRECISION\s*$",
    "DECIMAL": r"^\s*DECIMAL\s*(?:\(\s*\d+,\s*\d+\s*\))?\s*$",
    "NUMERIC": r"^\s*NUMERIC\s*(?:\(\s*\d+(?:,\s*\d+)?\s*\))?\s*$",
    "DATE": r"^\s*DATE\s*$",
    "CHAR": r"^\s*CHAR\s*(?:(\(\s*\d+\s*\)|\(MAX\)))?\s*$",
    "VARCHAR": r"^\s*VARCHAR\s*(?:(\(\s*\d+\s*\)|\(MAX\)))?\s*$",
    "TIMETZ": r"^\s*TIMETZ\s*(?:\(\s*\d+\s*\))?\s*$",
    "TIME": r"^\s*TIME\s*(?:\(\s*\d+\s*\))?\s*$",
    "TIMESTAMPTZ": r"^\s*TIMESTAMPTZ\s*(?:\(\s*\d+\s*\))?\s*$",
    "TIMESTAMP": r"^\s*TIMESTAMP\s*(?:\(\s*\d+\s*\))?\s*$",
    "BOOLEAN": r"^\s*BOOLEAN\s*$",
    "SUPER": r"^\s*SUPER\s*$",
    "VARBYTE": r"^\s*VARBYTE\s*$",
    "VARBINARY": r"^\s*VARBINARY\s*(?:\(\s*\d+\s*\))?\s*$",
    "GEOMETRY": r"^\s*GEOMETRY\s*$",
    "GEOGRAPHY": r"^\s*GEOGRAPHY\s*$"
}

# column datatype - default value mapping
DATA_TYPE_DEFAULTS = {
    'varchar': "''",
    'integer': '0',
    'bigint': '0',
    'smallint': '0',
    'decimal': '0.0',
    'boolean': 'false',
    'real': '0.0',
    'double precision': '0.0',
    'date': "'1970-01-01'",
    'timestamp': "'1970-01-01 00:00:00'",
    'timestamptz': "'1970-01-01 00:00:00 UTC'",
    'time': "'00:00:00'",
    'timetz': "'00:00:00 UTC'",
    'super': "''",
    'varbyte': "''",
    'numeric': '0.0',
    'char': "''"
}

REDSHIFT_CLUSTER_TYPE = "single-node"
# Util is being referred in Glue job
if "AWS_LAMBDA_FUNCTION_NAME" not in os.environ:
    # Utils file invoked from a Glue Job
    from awsglue.utils import getResolvedOptions
    glue_job_args = getResolvedOptions(sys.argv, ["enableFips"])
    # For glue jobs, set the below environment variable for the boto3 SDK to use FIPS, if enabled
    os.environ["AWS_USE_FIPS_ENDPOINT"] = glue_job_args["enableFips"]

    # Setting up the redshift cluster type.(default to single-node)
    REDSHIFT_CLUSTER_TYPE_PARAM_KEY = "/adp/amorphic/config/rsclustertype"
    SSM_CLIENT = boto3.client("ssm")
    REDSHIFT_CLUSTER_TYPE = get_ssm_parameter(SSM_CLIENT, REDSHIFT_CLUSTER_TYPE_PARAM_KEY)
# Util is being referred in Lambda function
else:
    # SSM parameter value is being passed from cloudformation template
    REDSHIFT_CLUSTER_TYPE = os.environ['redshiftClusterType']

class RedshiftConnectionException(Exception):
    """
    Creating a custom exception when redshift fails to create the connection
    """

    def __init___(self, error_arguments):
        Exception.__init__(self, "%s", error_arguments)


class RedshiftTableException(Exception):
    """
    Creating a custom exception when table operations fail in redshift
    """

    def __init___(self, error_arguments):
        Exception.__init__(self, "%s", error_arguments)

def get_sleep_duration(current_try, min_sleep_millis, max_sleep_millis):
    """
    This function calculates the sleep duration of athena query
    :param current_try
    :type current_try: int
    :param min_sleep_millis
    :type min_sleep_millis: int
    :param max_sleep_millis
    :type max_sleep_millis: int
    """
    current_try = max(0, current_try)
    current_sleep_millis = min_sleep_millis*pow(2, current_try)

    return min(current_sleep_millis, max_sleep_millis)


def assign_permissions(table_update_type, dataset_name, user_name, domain, conn, access_type=None):
    """
    This function will assign permissions to the user for the table
    :param table_update_type
    :param dataset_name:
    :param user_name
    :param domain
    :param conn
    """
    try:
        LOGGER.info('In redshiftUtil.assign_permissions, Assigning the permissions to the user - %s for redshift table', str(user_name))
        cursor = conn.cursor()
        table_name = f'{domain}.{dataset_name}'
        grant_table_query = f"GRANT SELECT ON TABLE {table_name} TO {user_name};"
        grant_schema_query = f"GRANT USAGE ON SCHEMA {domain} to {user_name};"
        cursor.execute(grant_table_query)
        cursor.execute(grant_schema_query)
        if access_type in REDSHIFT_TABLE_PERMISSIONS.keys():
            grant_schema_create_query = f"GRANT CREATE ON SCHEMA {domain} to {user_name};"
            cursor.execute(grant_schema_create_query)
            for permission in REDSHIFT_TABLE_PERMISSIONS[access_type]:
                permission_query = f"GRANT {permission} ON TABLE {table_name} TO {user_name};"
                cursor.execute(permission_query)
        if table_update_type == "update":
            LOGGER.info('In redshiftUtil.assign_permissions, table_update type is update so granting permissions to the view')
            view_name = f'{domain}.{dataset_name}_latest'
            grant_view_query = f"GRANT SELECT ON TABLE {view_name} TO {user_name};"
            cursor.execute(grant_view_query)
            if access_type in REDSHIFT_TABLE_PERMISSIONS.keys():
                for permission in REDSHIFT_TABLE_PERMISSIONS[access_type]:
                    permission_query = f"GRANT {permission} ON TABLE {view_name} TO {user_name};"
                    cursor.execute(permission_query)
        conn.commit()
        LOGGER.info('In redshiftUtil.assign_permissions, Successfully assigned permissions to user - %s for redshift table %s', str(user_name), str(table_name))
    except Exception as ex:
        conn.commit()
        LOGGER.error('In redshiftUtil.assign_permissions, error while granting access for dataset %s.%s to user - %s', domain, dataset_name, str(ex))
        rs_ds_1008 = errorUtil.get_error_object("RS-1008")
        rs_ds_1008['Message'] = rs_ds_1008['Message'].format(str(user_name), "dataset", dataset_name, str(ex).rstrip())
        raise errorUtil.GenericFailureException(EVENT_INFO, rs_ds_1008)

def random_string_generator():
    """
    This function generates a random string
    """
    pwd = ""
    count = 0
    length = 14
    while count < length:
        upper = random.choice(string.ascii_uppercase)
        lower = random.choice(string.ascii_lowercase)
        num = random.choice(string.digits)
        everything = upper + lower + num
        pwd += everything
        count += 3
        continue

    if count >= length:
        return pwd


def get_redshift_connection(redshift_host, redshift_port, redshift_user,
                            redshift_password, redshift_database):
    """
    This function returns redshift connection
    :param redshift_host
    :param redshift_port
    :param redshift_user
    :param redshift_password
    :param redshift_database
    :return: connection string
    """
    LOGGER.info('In redshiftUtil.get_redshift_connection, Getting redshift connection details for database - %s', redshift_database)
    connection_args = {
        'host': redshift_host,
        'port': int(redshift_port),
        'user': redshift_user,
        'password': redshift_password,
        'database': redshift_database
    }
    try:
        if os.environ.get('PYSPARK_PYTHON'):
            # Utils file invoked from a Glue PySpark job
            # Glue spark jobs currently only supports pure python libraries. psycopg2 has a C dependency.
            import pg8000
            # connection_args['ssl'] = True
            conn = pg8000.connect(**connection_args)
            LOGGER.info('In redshiftUtil.get_redshift_connection, Successfully retrieved redshift connection details')
            return conn
    except Exception as ex:
        LOGGER.error("In redshiftUtil.get_redshift_connection, Error %s", str(ex))
        # Pyspark jobs takes a long time to run if we do a time.sleep() and retry the connection, so skipping retry attempts.
        # Returning None, because Data Profiling job has an alternative way to calculate size of redshift datasets.
        return None

    current_try = 0
    max_retries = 3
    while max_retries > 0:
        try:
            # Utils file invoked by a  Lambda function/ glue python shell job
            import psycopg2
            LOGGER.info("Current Try - %s", current_try)
            # Waits 3 seconds for establishing the connection before timing out.
            connection_args['connect_timeout'] = 3
            conn = psycopg2.connect(**connection_args)
            LOGGER.info('In redshiftUtil.get_redshift_connection, Successfully retrieved redshift connection details')
            return conn

        except Exception as ex:
            LOGGER.error("In redshiftUtil.get_redshift_connection, Error %s", str(ex))
            max_retries = max_retries - 1
            current_try = current_try + 1
            if max_retries > 0:
                back_off_duration = 1
                LOGGER.info("In redshiftUtil.get_redshift_connection, will re-try after %s seconds back-off", back_off_duration)
                time.sleep(back_off_duration)
            else:
                LOGGER.error("In redshiftUtil.get_redshift_connection, reached maximum retries for connection limit error")
                rs_ds_1017 = errorUtil.get_error_object("RS-1017")
                rs_ds_1017["Message"] = "Not able to establish connection with Redshift. If the redshift is in paused or unavailable state, please retry when it is available."
                raise errorUtil.GenericFailureException(EVENT_INFO, rs_ds_1017)

#pylint: disable=too-many-locals
def delete_redshift_user(user_name, user_tenant_domains, groups_list, redshift_host,
                         redshift_port, redshift_user, redshift_password, redshift_database):
    """
    This function deleted the user in redshift
    :param user_name:
    :param redshift_host:
    :param redshift_port:
    :param redshift_user:
    :param redshift_password:
    :param redshift_database:
    :param user_tenant_domains: Segregation of user accessible tenants and their domains
    :return:
    """
    LOGGER.info("In redshiftUtil.delete_redshift_user, Deleting user %s from redshift, user domains - %s, user groups - %s", user_name, user_tenant_domains, groups_list)
    # Adding imports inline to avoid requirements in dataProfiling Jobs
    import pymysql
    # Edge Case: get all databases user has access to
    conn = get_redshift_connection(redshift_host, redshift_port, redshift_user, redshift_password, redshift_database)
    cursor = conn.cursor()
    get_all_databases_query = "SELECT database_name, database_acl FROM SVV_REDSHIFT_DATABASES WHERE database_acl LIKE '%{user}%'".format(user=user_name)
    cursor.execute(get_all_databases_query)
    databases = cursor.fetchall()
    if databases:
        database_list = ",".join(row[0] for row in databases)
        for database_name, _ in databases:
            if database_name not in user_tenant_domains:
                user_tenant_domains.update({database_name: set()})
        revoke_all_databases_query = "REVOKE ALL ON DATABASE {databases} FROM {user}".format(databases=pymysql.converters.escape_string(database_list), user=pymysql.converters.escape_string(user_name))
        cursor.execute(revoke_all_databases_query)
    conn.commit()
    conn.close()
    # Drop user access on schemas
    for tenant_name in user_tenant_domains:
        database_name = tenant_name
        conn = get_redshift_connection(redshift_host, redshift_port, redshift_user, redshift_password, database_name)
        cursor = conn.cursor()
        # Removing user from all user related groups and group_name is already lowercase.
        for group_name in groups_list:
            try:
                drop_user_from_group = "ALTER GROUP {group_name} DROP USER {user}".format(group_name=group_name, user=user_name)
                LOGGER.info("In redshiftUtil.delete_redshift_user, Revoking user from group - %s", group_name)
                cursor.execute(drop_user_from_group)
            except Exception as ex:
                conn.rollback()
                if "does not exist" in str(ex):
                    is_user = bool("user" in str(ex))
                    LOGGER.info("In redshiftUtil.delete_redshift_user, Invalid %s - %s", "User" if is_user else "Group", user_name if is_user else group_name)
                    continue
                LOGGER.error("In redshiftUtil.delete_redshift_user, Error while removing user from group - %s", group_name)
                errorUtil.raise_exception(EVENT_INFO, "RST", "RS-1007", None, str(ex))
        # Retrieve all schemas in the tenant
        db_schema_list = extract_db_schemas(conn)
        revoke_public_access_query = f"REVOKE ALL ON SCHEMA PUBLIC,PG_CATALOG FROM {pymysql.converters.escape_string(user_name)};"
        revoke_public_tables_query = "REVOKE ALL ON ALL TABLES IN SCHEMA PUBLIC FROM {0};".format(pymysql.converters.escape_string(user_name))
        ########## IMPORTANT ##########
        # Perfoming revoke/alter actions for all the schemas in the tenant (db_schema_list)
        # instead of filtering only user schemas from DynamoDB metadata
        # because the same user might be in other environments with some dependency objects (schemas, tables, views etc)
        # which will cause user deletion error when tried in this environment (local feature branch).
        if db_schema_list:
            tenant_schema_list = ','.join(domain.lower() for domain in db_schema_list)
            revoke_privileges_query = f"REVOKE ALL ON SCHEMA {pymysql.converters.escape_string(tenant_schema_list)} FROM {pymysql.converters.escape_string(user_name)};"
            revoke_tables_query = f"REVOKE ALL ON ALL TABLES IN SCHEMA {pymysql.converters.escape_string(tenant_schema_list)} FROM { pymysql.converters.escape_string(user_name)};"
            # Alter default privileges which got added newly for CLOUD-2549 (Dataset Level Access)
            alter_default_privileges = f"ALTER DEFAULT PRIVILEGES IN SCHEMA {pymysql.converters.escape_string(tenant_schema_list)} REVOKE ALL ON TABLES FROM {pymysql.converters.escape_string(user_name)};"
            get_all_table_view_owner_query = f"SELECT n.nspname AS schema_name, c.relname AS table_name FROM pg_class As c LEFT JOIN pg_namespace n ON n.oid = c.relnamespace WHERE pg_get_userbyid(c.relowner) = '{user_name}' AND c.relkind IN('r', 'v')"
            cursor.execute(get_all_table_view_owner_query)
            for schema, table in cursor.fetchall():
                LOGGER.info("In redshiftUtil.delete_redshift_user, Changing owner - %s.%s", schema, table)
                change_owner_query = f"ALTER TABLE {pymysql.converters.escape_string(schema)}.{pymysql.converters.escape_string(table)} OWNER TO {pymysql.converters.escape_string(redshift_user)};"
                cursor.execute(change_owner_query)
            # Edge Case: Alter schema privileges for schemas created in redshift directly
            get_all_schema_owner_query = f"SELECT database_name, schema_name FROM  SVV_ALL_SCHEMAS, pg_user where schema_owner = usesysid and usename = '{user_name}';"
            cursor.execute(get_all_schema_owner_query)
            for database, schema in cursor.fetchall():
                LOGGER.info("In redshiftUtil.delete_redshift_user, Changing owner of schema - %s.%s", database, schema)
                change_owner_query = f"ALTER SCHEMA {pymysql.converters.escape_string(schema)} OWNER TO {pymysql.converters.escape_string(redshift_user)};"
                cursor.execute(change_owner_query)
            LOGGER.info("In redshiftUtil.delete_redshift_user, Revoking user schemas - %s, connection - %s", tenant_schema_list, conn)
            LOGGER.info("In redshiftUtil.delete_redshift_user, Revoking privileges - %s", revoke_privileges_query)
            cursor.execute(revoke_privileges_query)
            LOGGER.info("In redshiftUtil.delete_redshift_user, Revoking tables - %s", revoke_tables_query)
            cursor.execute(revoke_tables_query)
            LOGGER.info("In redshiftUtil.delete_redshift_user, Revoking default privileges - %s", alter_default_privileges)
            cursor.execute(alter_default_privileges)
            LOGGER.info("In redshiftUtil.delete_redshift_user, Revoking public access - %s", revoke_public_access_query)
            cursor.execute(revoke_public_access_query)
            LOGGER.info("In redshiftUtil.delete_redshift_user, Revoking public tables access - %s", revoke_public_tables_query)
            cursor.execute(revoke_public_tables_query)
            LOGGER.info("In redshiftUtil.delete_redshift_user, revoking queries completed successfully")
        else:
            LOGGER.error("In redshiftUtil.delete_redshift_user, No tenant schemas found for tenant - %s, schemas - %s", tenant_name, db_schema_list)
            cursor.execute(revoke_public_access_query)
            cursor.execute(revoke_public_tables_query)
        conn.commit()
        cursor.close()
        conn.close()
    LOGGER.info("In redshiftUtil.delete_redshift_user, dropping user - %s", user_name)
    # Drop user from cluster
    conn = get_redshift_connection(redshift_host, redshift_port, redshift_user,
                                   redshift_password, redshift_database)
    cursor = conn.cursor()
    try:
        delete_user_query = "DROP USER IF EXISTS {0};".format(user_name)
        cursor.execute(delete_user_query)
        # Commit the transaction to persist the changes, without it soon as the connection closes (or a rollback happens), the change will be discarded.
        conn.commit()
    except Exception as exc:
        # Rollback clears the failed transaction, puts the connection back into a clean state, and allows the user to retry the operation.
        conn.rollback()
        if "cannot be dropped" in str(exc):
            LOGGER.info("In redshiftUtil.delete_redshift_user, Trying another process to revoke dependencies.")
            for tenant_name in user_tenant_domains:
                database_name = tenant_name
                conn = get_redshift_connection(redshift_host, redshift_port, redshift_user, redshift_password, database_name)
                # getting list of schemas for current tenant tenant_name
                db_schema_list = extract_db_schemas(conn)
                if db_schema_list:
                    tenant_schema_list = ','.join(domain.lower() for domain in db_schema_list)
                    cursor = conn.cursor()
                    try:
                        grant_all_query = f"GRANT ALL ON SCHEMA {pymysql.converters.escape_string(tenant_schema_list)} TO {pymysql.converters.escape_string(user_name)};"
                        cursor.execute(grant_all_query)
                        alter_default_privileges = f"ALTER DEFAULT PRIVILEGES FOR USER {pymysql.converters.escape_string(user_name)} IN SCHEMA {pymysql.converters.escape_string(tenant_schema_list)} REVOKE ALL ON Tables FROM {pymysql.converters.escape_string(user_name)};"
                        cursor.execute(alter_default_privileges)
                        revoke_all_query = f"REVOKE ALL ON SCHEMA {pymysql.converters.escape_string(tenant_schema_list)} FROM {pymysql.converters.escape_string(user_name)};"
                        cursor.execute(revoke_all_query)
                    except Exception as ex:
                        if "does not exist" in str(ex):
                            LOGGER.error("In redshiftUtil.delete_redshift_user, Exception - %s", str(ex))
                            continue
            delete_user_query = f"DROP USER IF EXISTS {user_name};"
            cursor.execute(delete_user_query)
        else:
            LOGGER.error("In redshiftUtil.delete_redshift_user, Exception while deleting user %s - %s", user_name, str(exc))
            raise Exception(str(exc)) from exc
    conn.commit()
    cursor.close()
    conn.close()
    LOGGER.info("In redshiftUtil.delete_redshift_user, Successfully deleted the user in redshift.")


def disable_redshift_user(user_name, redshift_host, redshift_port, redshift_user,
                          redshift_password, redshift_database):
    """
    Disables user in redshift
    :param user_name:
    :param redshift_host:
    :param redshift_port:
    :param redshift_user:
    :param redshift_password:
    :param redshift_database:
    :return:
    """
    LOGGER.info("In redshiftUtil.disable_redshift_user, Disabling user %s in redshift", user_name)
    # Adding imports inline to avoid requirements in dataProfiling Jobs
    conn = get_redshift_connection(redshift_host, redshift_port, redshift_user,
                                   redshift_password, redshift_database)
    cursor = conn.cursor()
    yesterday = datetime.strftime((datetime.now() - timedelta(1)), '%Y-%m-%d')
    # Setting valid until to a past date makes the user's password only valid until that date and hence disables the user
    disable_user_query = "ALTER USER {0} VALID UNTIL '{1}';".format(user_name, yesterday)
    cursor.execute(disable_user_query)
    # Fetching user's active sessions
    get_active_sessions_query = ""
    if REDSHIFT_CLUSTER_TYPE == "serverless":
        #using sys_connection_log table to fetch user's active session since stv_sessions is not available for redshift serverless
        get_active_sessions_query = "select session_id from sys_connection_log where event = 'initiating session' and user_name = '{0}' and session_id not in (select session_id from sys_connection_log where event = 'disconnecting session');".format(user_name)
    else:
        get_active_sessions_query = "SELECT process FROM STV_SESSIONS WHERE USER_NAME='{0}'".format(user_name)
    cursor.execute(get_active_sessions_query)
    result = cursor.fetchall()
    for session in result:
        session_kill_query = "SELECT pg_terminate_backend({0})".format(session[0])
        cursor.execute(session_kill_query)
    conn.commit()
    cursor.close()
    conn.close()
    LOGGER.info("In redshiftUtil.disable_redshift_user, Successfully disabled the user in redshift.")

def enable_redshift_user(user_name, redshift_host, redshift_port, redshift_user,
                          redshift_password, redshift_database):
    """
    Enables user in redshift
    :param user_name:
    :param redshift_host:
    :param redshift_port:
    :param redshift_user:
    :param redshift_password:
    :param redshift_database:
    :return:
    """
    LOGGER.info("In redshiftUtil.enable_redshift_user, Enabling user %s in redshift", user_name)
    conn = get_redshift_connection(redshift_host, redshift_port, redshift_user,
                                   redshift_password, redshift_database)
    cursor = conn.cursor()
    enable_user_query = "ALTER USER {0} VALID UNTIL 'infinity';".format(user_name)
    cursor.execute(enable_user_query)
    conn.commit()
    cursor.close()
    conn.close()
    LOGGER.info("In redshiftUtil.enable_redshift_user, Successfully enabled the user in redshift.")

def create_redshift_user(user_name, redshift_host, redshift_port, redshift_user,
                         redshift_password, redshift_database):
    """
    This function creates/Altering the user in redshift.
    :param user_name: user to be created/altered in redshift
    :type user_name: str
    :param redshift_host
    :param redshift_port
    :param redshift_user
    :param redshift_password
    :param redshift_database
    :return: password
    :rtype: string
    """
    LOGGER.info('In redshiftUtil.create_redshift_user, Creating/Altering user in redshift')
    password = ""
    conn = get_redshift_connection(redshift_host, redshift_port, redshift_user,
                                   redshift_password, redshift_database)
    cursor = conn.cursor()
    count_query = 'SELECT COUNT(*) FROM PG_USER WHERE USENAME = %s;'
    user_name = user_name.lower()
    data = [user_name]
    cursor.execute(count_query, data)
    result = cursor.fetchone()
    conn.commit()
    if result[0] == 0:
        password = random_string_generator()
        create_user_query = "CREATE USER " + user_name + " WITH PASSWORD %s;"
        data = [password]
        cursor.execute(create_user_query, data)
        conn.commit()
        LOGGER.info('Successfully created the user in redshift')
    if result[0] > 0:
        password = random_string_generator()
        alter_user_query = "ALTER USER " + user_name + " WITH PASSWORD %s;"
        data = [password]
        cursor.execute(alter_user_query, data)
        conn.commit()
        LOGGER.info('In redshiftUtil.create_redshift_user, Altered user to change the password')
    cursor.close()
    return password


def create_redshift_table(redshift_schema_name, redshift_table_name, table_schema, user_name, conn, sort_dist_options=None, column_table_constraints=None):
    """
    This function will create table in redshift
    :param redshift_schema_name
    :param redshift_table_name
    :param table_schema
    :param user_name
    :param conn: redshift connection
    :param sort_dist_options: sort and distribution options for the table
    :param column_table_constraints: column and table atributes and constraints for the table
    """

    retry_num = 0
    error_message = ""
    unsupported_sortkey_datatype = False

    while retry_num < 2:
        LOGGER.info("In redshiftUtil.create_redshift_table, current retry number is %s", str(retry_num))
        if "concurrent transaction" in error_message or error_message == "":
            try:
                LOGGER.info('In redshiftUtil.create_redshift_table, Creating table %s in redshift with sort_dist_options %s and column_table_constraints %s', redshift_table_name, str(sort_dist_options), str(column_table_constraints))
                cursor = conn.cursor()
                if not sort_dist_options:
                    sort_dist_options = {}
                if not column_table_constraints:
                    column_table_constraints = {}
                sort_type = sort_dist_options.get('SortType', 'none')
                dist_type = sort_dist_options.get('DistType', 'even')
                sort_keys = sort_dist_options.get('SortKeys', [])
                dist_key = sort_dist_options.get('DistKey', "")
                primary_keys = column_table_constraints.get('PrimaryKeys', [])
                unique_columns = column_table_constraints.get('UniqueColumns', [])
                is_identity_needed = column_table_constraints.get('IsIdentityNeeded', 'no')
                identity_attribute_values = column_table_constraints.get('IdentityAttributeValues', [])
                # Add IDENTITY column if presents
                if is_identity_needed == "yes" and identity_attribute_values:
                    LOGGER.info('In redshiftUtil.create_redshift_table, Identiy Column is needed and passed IdentityAttributeValues, preparing table schema accordingly')
                    id_col_name, id_seed, id_step = identity_attribute_values[0], identity_attribute_values[1], identity_attribute_values[2]
                    table_schema += ', {col_name} bigint IDENTITY({seed}, {step})'.format(col_name=id_col_name, seed=id_seed, step=id_step)
                # Add primary key(s) to the table_schema
                if primary_keys:
                    LOGGER.info('In redshiftUtil.create_redshift_table, Primary key(s) passed in input body and preparing table schema accordingly')
                    table_schema += ', PRIMARY KEY({})'.format(str(', '.join(primary_keys)))
                # Add unique field values to the table_schema
                if unique_columns:
                    LOGGER.info('In redshiftUtil.create_redshift_table, Unique key(s) passed in input body and preparing table schema accordingly')
                    table_schema += ', UNIQUE({})'.format(str(', '.join(unique_columns)))
                create_table_query = "CREATE TABLE {redshift_table_name}( {table_schema} )" \
                                        .format(redshift_table_name=redshift_table_name, table_schema=table_schema)

                # Add distribution key to the query statement
                if dist_type == 'key' and not dist_key:
                    ec_ipv_1008 = errorUtil.get_error_object("IPV-1008")
                    ec_ipv_1008['Message'] = ec_ipv_1008['Message'].format("DistKey")
                    raise Exception(ec_ipv_1008['Message'])
                elif dist_type == 'key':
                    create_table_query += " DISTSTYLE key DISTKEY({})".format(str(dist_key))
                elif dist_type != 'auto':
                    create_table_query += " DISTSTYLE {}".format(dist_type)

                # Add sort key to the query statement
                if sort_type != 'none' and not sort_keys:
                    ec_ipv_1008 = errorUtil.get_error_object("IPV-1008")
                    ec_ipv_1008['Message'] = ec_ipv_1008['Message'].format("SortKeys")
                    raise Exception(ec_ipv_1008['Message'])
                elif sort_type == 'none':
                    create_table_query += ";"
                else:
                    sortkeys_map = ",".join(sort_keys)
                    create_table_query += " {sort_type} sortkey({sort_keys});".format(sort_type=sort_type, sort_keys=sortkeys_map)

                #Raise error if Sort type is Interleaved and one of the sort datatype used is Varbyte
                #We are raising this error because AWS have some compression incompatibility with this.
                if (sort_type == 'interleaved') and ('varbyte' in table_schema):
                    for col_schema in table_schema.split(","):
                        if 'varbyte' in col_schema:
                            if col_schema.split()[0] in sort_keys:
                                unsupported_sortkey_datatype = True

                if unsupported_sortkey_datatype:
                    ec_rs_1027 = errorUtil.get_error_object("RS-1027")
                    ec_rs_1027['Message'] = ec_rs_1027['Message'].format(sort_type, "varbyte")
                    raise Exception(ec_rs_1027['Message'])

                LOGGER.info("In redshiftUtil.create_redshift_table, query to create redshift table = %s", create_table_query)
                grant_schema_query = f"GRANT USAGE ON SCHEMA {redshift_schema_name} to {user_name};"
                grant_schema_create_query = f"GRANT CREATE ON SCHEMA {redshift_schema_name} to {user_name};"

                # Set up 10-second timeout using context manager, to time bound redshift table creation
                with TimeBounder(20):
                    cursor.execute(create_table_query)
                    cursor.execute(grant_schema_create_query)
                    cursor.execute(grant_schema_query)
                    for permission in REDSHIFT_TABLE_PERMISSIONS["owner"] + ['SELECT']:
                        permission_query = f"GRANT {permission} ON TABLE {redshift_table_name} TO {user_name};"
                        cursor.execute(permission_query)
                    conn.commit()
                LOGGER.info('In redshiftUtil.create_redshift_table, Successfully created table %s in redshift', redshift_table_name)
                return
            except Exception as ex:
                conn.rollback()
                error_message = 'Failed to create Redshift table with error - ' + str(ex).rstrip()
                LOGGER.error("In redshiftUtil.create_redshift_table, failed to create redshift table with error - %s", str(ex))
                # Raise exception if it failed in retry as well by adding sleep time of 1 sec
                time.sleep(1)
                if retry_num > 0 or "timed out after" in str(ex):
                    ec_rs_1001 = errorUtil.get_error_object("RS-1001")
                    ec_rs_1001['Message'] = ec_rs_1001['Message'].format(str(ex).rstrip())
                    raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1001) from ex

        else:
            LOGGER.error("In redshiftUtil.create_redshift_table, table creation failure is not because of concurrent transaction, error is - %s", str(error_message))
            ec_rs_1001 = errorUtil.get_error_object("RS-1001")
            ec_rs_1001['Message'] = error_message
            raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1001)

        # Increment the iterator
        retry_num += 1


def delete_redshift_table(redshift_table_name, conn, force_delete=False):
    """
    This function will delete table in redshift
    :param redshift_table_name
    :param conn: redshift connection
    """
    try:
        LOGGER.info('In redshiftUtil.delete_redshift_table, Deleting table %s in redshift', redshift_table_name)
        cursor = conn.cursor()
        if force_delete:
            delete_table_query = "DROP TABLE IF EXISTS {redshift_table_name} CASCADE;".format(redshift_table_name=redshift_table_name)
        else:
            delete_table_query = "DROP TABLE IF EXISTS {redshift_table_name};".format(redshift_table_name=redshift_table_name)
        cursor.execute(delete_table_query)
        conn.commit()
        LOGGER.info('In redshiftUtil.delete_redshift_table, Successfully deleted the table %s in redshift', redshift_table_name)
    except Exception as ex:
        ec_rs_1002 = errorUtil.get_error_object("RS-1002")
        ec_rs_1002['Message'] = ec_rs_1002['Message'].format(str(ex).rstrip())
        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1002) from ex


def delete_redshift_view(redshift_view_name, conn):
    """
    This function will delete views in redshift
    :param redshift_view_name
    :param conn: redshift connection
    """
    try:
        LOGGER.info('In redshiftUtil.delete_redshift_view, Deleting view %s in redshift', redshift_view_name)
        cursor = conn.cursor()
        delete_view_query = "DROP VIEW IF EXISTS {table_view_name};".format(table_view_name=redshift_view_name)
        cursor.execute(delete_view_query)
        conn.commit()
        LOGGER.info('In redshiftUtil.delete_redshift_view, Successfully deleted the view %s in redshift', redshift_view_name)
    except Exception as ex:
        ec_rs_1003 = errorUtil.get_error_object("RS-1003")
        ec_rs_1003['Message'] = ec_rs_1003['Message'].format(str(ex).rstrip())
        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1003) from ex


def condition_build(col_name):
    """
    This method build the conditions from the list of columns
    :param col_name
    """
    return "original.{col} = latest.{col}".format(col=col_name)


def create_redshift_view(redshift_view_name, redshift_table_name, latest_record_indicator, record_keys, user_name, conn):
    """
    This function will create view in redshift
    :param redshift_view_name
    :param redshift_table_name
    :param latest_record_indicator
    :param record_keys
    :param user_name
    :param conn: connection
    """
    LOGGER.info('In redshiftUtil.create_redshift_view, Creating view %s in redshift', redshift_view_name)
    record_keys_str = ", ".join(record_keys)
    record_keys_conditions = " AND ".join(map(condition_build, record_keys))
    create_view_str = """CREATE OR REPLACE VIEW {r_view_name} AS SELECT original.* FROM (SELECT * FROM {r_name}) original
JOIN
(SELECT {k_list}, MAX({l_ind}) AS {l_ind} FROM {r_name} GROUP BY {k_list}) latest
ON {key_cond}
AND original.{l_ind} = latest.{l_ind};
""".format(r_view_name=redshift_view_name, r_name=redshift_table_name, k_list=record_keys_str,
           l_ind=latest_record_indicator, key_cond=record_keys_conditions)
    cursor = conn.cursor()
    cursor.execute(create_view_str)
    for permission in REDSHIFT_TABLE_PERMISSIONS["owner"] + ['SELECT']:
        permission_query = f"GRANT {permission} ON TABLE {redshift_view_name} TO {user_name};"
        cursor.execute(permission_query)
    conn.commit()
    LOGGER.info('In redshiftUtil.create_redshift_view, Successfully created the %s view in redshift', redshift_view_name)


def parse_redshift_schema(schema_list):
    """
    Parses schema for redshift table creation
    :param schema_list
    :return schema
    """
    LOGGER.info("In redshiftUtil.parse_redshift_schema, entering method...")
    schema_items = []
    for item in schema_list:
        # adding space after column type for addition of not null constraint if any.
        # eg. single_column_definition = '"test_col" integer '
        single_column_definition = '"{name}" {type} ' .format(name=item['name'], type=item['type'])
        if 'is_not_null' in item and item['is_not_null']:
            # eg. single_column_definition = '"test_col" integer not null '
            single_column_definition += "not null "
        schema_items.append(single_column_definition)
    # eg. redshift_schema = '"test_col" integer not null , "test_col2" integer '
    redshift_schema = ', '.join(schema_items)
    LOGGER.info('In redshiftUtil.parse_redshift_schema, schema after parsing = %s', redshift_schema)
    return redshift_schema


def create_redshift_group(group_name, user_list, conn):
    """
    This function will create group in redshift
    :param group_name
    :param user_list
    :param conn: connection
    """
    try:
        LOGGER.info('In redshiftUtil.create_redshift_group, Creating group in redshift')
        cursor = conn.cursor()

        create_table_query = "CREATE GROUP {group_name} WITH USER {user_list}".format(group_name=group_name, user_list=user_list)
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        LOGGER.info('In redshiftUtil.create_redshift_group, Successfully created the group in redshift : %s', group_name)
    except Exception as ex:
        ec_rs_1004 = errorUtil.get_error_object("RS-1004")
        ec_rs_1004['Message'] = ec_rs_1004['Message'].format(str(ex).rstrip())
        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1004) from ex


def delete_redshift_group(group_name, conn):
    """
    This function will create group in redshift
    :param group_name
    :param conn: connection
    """
    try:
        # Adding imports inline to avoid requirements in dataProfiling Jobs
        import pymysql
        LOGGER.info('In redshiftUtil.delete_redshift_group, Deleting group in Redshift. Connection status - %s', conn.closed)
        cursor = conn.cursor()
        get_groups_query = f"select * from pg_group where groname= lower('{group_name}')"
        cursor.execute(get_groups_query)
        response = cursor.fetchall()
        LOGGER.info("In redshiftUtil.delete_redshift_group, response for %s is %s",get_groups_query,response)
        if len(response):
            LOGGER.info("In redshiftUtil.delete_redshift_group, Listing all the schema's present in Redshift cluster")
            schemas = "select * from pg_namespace"
            cursor.execute(schemas)
            response = cursor.fetchall()
            schema_list = [row[0] for row in response if "pg_" not in row[0]]
            string_schema_list = ','.join(schema_list)
            LOGGER.info("In redshiftUtil.delete_redshift_group, Revoking all access on schema & tables in Redshift before dropping the table")
            revoke_schema_query = "REVOKE ALL ON SCHEMA {string_schema_list} from group {group_name}".format(
                group_name=pymysql.converters.escape_string(group_name),
                string_schema_list=pymysql.converters.escape_string(string_schema_list)
            )
            revoke_tables_query = "REVOKE ALL ON ALL TABLES IN SCHEMA {string_schema_list} FROM group {group_name}".format(
                group_name=pymysql.converters.escape_string(group_name),
                string_schema_list=pymysql.converters.escape_string(string_schema_list)
            )
            drop_table_query = "DROP GROUP {group_name}".format(group_name=pymysql.converters.escape_string(group_name))
            db_schema_list = extract_db_schemas(conn)
            if db_schema_list:
                tenant_schema_list = ','.join(domain.lower() for domain in db_schema_list)
                revoke_default_privileges_query = "ALTER DEFAULT PRIVILEGES IN SCHEMA {tenant_schema_list} REVOKE ALL ON TABLES FROM GROUP {group_name}".format(
                    group_name=pymysql.converters.escape_string(group_name),
                    tenant_schema_list=pymysql.converters.escape_string(tenant_schema_list)
                )
                cursor.execute(revoke_default_privileges_query)
            cursor.execute(revoke_schema_query)
            cursor.execute(revoke_tables_query)
            cursor.execute(drop_table_query)
            conn.commit()
            cursor.close()
            LOGGER.info('In redshiftUtil.delete_redshift_group, Successfully deleted the group in redshift : %s', group_name)
        else:
            LOGGER.info('In redshiftUtil.delete_redshift_group, %s group does not exist in redshift', group_name)
    except Exception as ex:
        ec_rs_1005 = errorUtil.get_error_object("RS-1005")
        ec_rs_1005['Message'] = ec_rs_1005['Message'].format(str(ex).rstrip())
        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1005) from ex


def add_users_to_redshift_group(group_name, user_list, conn):
    """
    This function will create group in redshift
    :param group_name
    :param user_list
    :param conn: connection
    """
    try:
        LOGGER.info('In redshiftUtil.add_users_to_redshift_group, given list of users is %s', str(user_list))
        cursor = conn.cursor()

        create_table_query = "ALTER GROUP {group_name} ADD USER {user_list}".format(group_name=group_name, user_list=user_list)
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        LOGGER.info('In redshiftUtil.add_users_to_redshift_group, Successfully added users to group in redshift : %s', str(user_list))
    except Exception as ex:
        ec_rs_1006 = errorUtil.get_error_object("RS-1006")
        ec_rs_1006['Message'] = ec_rs_1006['Message'].format(str(ex).rstrip())
        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1006) from ex


def remove_users_in_redshift_group(group_name, user_list, conn):
    """
    This function will create group in redshift
    :param group_name
    :param user_list
    :param conn: connection
    """
    try:
        LOGGER.info('In redshiftUtil.remove_users_in_redshift_group, given list of users is %s', str(user_list))
        cursor = conn.cursor()

        create_table_query = "ALTER GROUP {group_name} DROP USER {user_list}".format(group_name=group_name, user_list=user_list)
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()
        LOGGER.info('In redshiftUtil.remove_users_in_redshift_group, Successfully removed users from group in redshift : %s', str(user_list))
    except Exception as ex:
        ec_rs_1007 = errorUtil.get_error_object("RS-1007")
        ec_rs_1007['Message'] = ec_rs_1007['Message'].format(str(ex).rstrip())
        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1007) from ex


def assign_permissions_redshift(table_update_type, dataset_name, group_name, domain, conn, access_type):
    """
    This function will assign permissions to the user for the table and view created
    :param table_update_type
    :param dataset_name:
    :param group_name
    :param domain
    :param conn
    :param access_type
    """
    LOGGER.info('In redshiftUtil.assign_permissions_redshift, assigning permissions to the %s for redshift table', group_name)
    try:
        cursor = conn.cursor()
        table_name = f'{domain}.{dataset_name}'
        grant_table_query = f"GRANT SELECT ON TABLE {table_name} TO GROUP {group_name};"
        grant_schema_query = f"GRANT USAGE ON SCHEMA {domain} to GROUP {group_name};"
        cursor.execute(grant_table_query)
        cursor.execute(grant_schema_query)
        if access_type in REDSHIFT_TABLE_PERMISSIONS.keys():
            grant_schema_create_query = f"GRANT CREATE ON SCHEMA {domain} to GROUP {group_name};"
            cursor.execute(grant_schema_create_query)
            for permission in REDSHIFT_TABLE_PERMISSIONS[access_type]:
                permission_query = f"GRANT {permission} ON TABLE {table_name} TO GROUP {group_name};"
                cursor.execute(permission_query)
        if table_update_type == "update":
            view_name = f'{domain}.{dataset_name}_latest'
            grant_view_query = f"GRANT SELECT ON TABLE {view_name} TO GROUP {group_name};"
            cursor.execute(grant_view_query)
            if access_type in REDSHIFT_TABLE_PERMISSIONS.keys():
                for permission in REDSHIFT_TABLE_PERMISSIONS[access_type]:
                    permission_query = f"GRANT {permission} ON TABLE {view_name} TO GROUP {group_name};"
                    cursor.execute(permission_query)
        conn.commit()
        cursor.close()
        LOGGER.info('In redshiftUtil.assign_permissions_redshift, successfully assigned permissions to %s for redshift table', group_name)
    except Exception as ex:
        conn.commit()
        ec_rs_1008 = errorUtil.get_error_object("RS-1008")
        ec_rs_1008['Message'] = ec_rs_1008['Message'].format(str(group_name), "dataset", dataset_name, str(ex).rstrip())
        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1008) from ex


def schema_access(access_type, schema_name, user_list, conn, group_access_type, group_name=""):
    """
    This method is used to revoke usage permission on schema
    """
    LOGGER.info("In redshiftUtil.schema_access method, with access type %s, schema name %s, user list %s", access_type, schema_name, user_list)
    try:
        if access_type.upper() == "GRANT":
            schema_usage_query = "{access_type} USAGE ON SCHEMA {schema_name} to {user_list};".format(
                access_type=access_type, schema_name=schema_name, user_list=user_list
            )
        if access_type.upper() == "REVOKE":
            schema_usage_query = "{access_type} USAGE ON SCHEMA {schema_name} from {user_list};".format(
                access_type=access_type, schema_name=schema_name, user_list=user_list
            )
        cursor = conn.cursor()
        cursor.execute(schema_usage_query)
        if group_access_type == 'owner':
            if access_type.upper() == "GRANT":
                schema_create_query = f"{access_type} CREATE ON SCHEMA {schema_name} to {user_list};"
            if access_type.upper() == "REVOKE":
                schema_create_query = f"{access_type} CREATE ON SCHEMA {schema_name} from {user_list};"
            cursor.execute(schema_create_query)
        conn.commit()
        cursor.close()
    except Exception as e_x:
        if access_type.upper() == "GRANT":
            error_object = errorUtil.get_error_object("RS-1008")
        if access_type.upper() == "REVOKE":
            error_object = errorUtil.get_error_object("RS-1009")
        error_object['Message'] = error_object['Message'].format(group_name, "domain", schema_name, str(e_x).rstrip())
        raise errorUtil.RedshiftTableException(EVENT_INFO, error_object) from e_x
    LOGGER.info("In redshiftUtil.schema_access method, exiting")


def revoke_permissions_redshift(dataset_item, group_name, conn, access_type):
    """
    This function will revoke permissions to the group for the table and view.
    :param dataset_item:
    :param group_name
    :param conn: connection
    """
    try:
        LOGGER.info('In redshiftUtil.revoke_permissions_redshift, revoking access to group %s on dataset %s from redshift', group_name, dataset_item['DatasetName'])
        cursor = conn.cursor()
        table_name = dataset_item['Domain'] + "." + dataset_item['DatasetName']
        revoke_table_query = f"REVOKE SELECT ON TABLE {table_name} FROM GROUP {group_name};"
        cursor.execute(revoke_table_query)
        if access_type in REDSHIFT_TABLE_PERMISSIONS.keys():
            revoke_schema_create_query = f"REVOKE CREATE ON SCHEMA {dataset_item['Domain']} FROM GROUP {group_name};"
            cursor.execute(revoke_schema_create_query)
            for permission in REDSHIFT_TABLE_PERMISSIONS[access_type]:
                permission_query = f"REVOKE {permission} ON TABLE {table_name} FROM GROUP {group_name};"
                cursor.execute(permission_query)
        if 'TableUpdate' in dataset_item.keys() and dataset_item['TableUpdate'] == 'update':
            view_name = f"{dataset_item['Domain']}.{dataset_item['DatasetName']}_latest"
            revoke_view_query = f"REVOKE SELECT ON TABLE {view_name} FROM GROUP {group_name};"
            cursor.execute(revoke_view_query)
            if access_type in REDSHIFT_TABLE_PERMISSIONS.keys():
                for permission in REDSHIFT_TABLE_PERMISSIONS[access_type]:
                    permission_query = f"REVOKE {permission} ON TABLE {view_name} FROM GROUP {group_name};"
                    cursor.execute(permission_query)
        conn.commit()
        cursor.close()
        LOGGER.info('In redshiftUtil.revoke_permissions_redshift, successfully revoked access to group %s on dataset %s', group_name, dataset_item['DatasetName'])
    except Exception as ex:
        conn.commit()
        ec_rs_1009 = errorUtil.get_error_object("RS-1009")
        ec_rs_1009['Message'] = ec_rs_1009['Message'].format(str(group_name), "dataset", dataset_item['DatasetName'], str(ex).rstrip())
        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1009) from ex


def assign_group_permissions_to_redshift_views(view_name, group_name, domain, conn, sql_statement, list_of_domains_from_db, access_type):
    """
    This function will assign permissions to the user for the table and view created
    :param view_name: Name of the view that should be given access to
    :param group_name: Name of the redshift data ware house group
    :param domain: Name of the domain/schema
    :param conn: psycopg2 connection to data ware house
    :param sql_statement: sql statement to run against data ware house
    :param list_of_domains_from_db: list of domains retrieved from dynamo db
    """
    LOGGER.info('In redshiftUtil.assign_group_permissions_to_redshift_views, assigning the permissions to the %s for redshift view', group_name)
    try:
        cursor = conn.cursor()
        table_name = f'{domain}.{view_name}'
        list_of_domains_from_sql = extract_domains_from_view_sql_statement(sql_statement, list_of_domains_from_db)
        comma_seperated_list_of_domains = ','.join(list_of_domains_from_sql)
        grant_table_query = f"GRANT SELECT ON TABLE {table_name} TO GROUP {group_name};"
        grant_schema_query = f"GRANT USAGE ON SCHEMA {comma_seperated_list_of_domains} TO GROUP {group_name};"
        cursor.execute(grant_table_query)
        cursor.execute(grant_schema_query)
        if access_type in REDSHIFT_TABLE_PERMISSIONS.keys():
            for permission in REDSHIFT_TABLE_PERMISSIONS[access_type]:
                permission_query = f"GRANT {permission} ON TABLE {table_name} TO GROUP {group_name};"
                cursor.execute(permission_query)
        conn.commit()
        cursor.close()
        LOGGER.info('In redshiftUtil.assign_group_permissions_to_redshift_views, successfully assigned permissions to %s for redshift view', group_name)
    except Exception as ex:
        ec_rs_1008 = errorUtil.get_error_object("RS-1008")
        ec_rs_1008['Message'] = ec_rs_1008['Message'].format(str(group_name), "view", view_name, str(ex).rstrip())
        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1008) from ex


def revoke_group_permissions_to_redshift_views(view_item, group_name, conn):
    """
    This function will revoke permissions to the group for the table and view.
    :param view_item:
    :param group_name
    :param conn: connection
    """
    try:
        LOGGER.info('In redshiftUtil.revoke_group_permissions_to_redshift_views, revoking access to group %s on view %s from redshift', group_name, view_item['DatasetName'])
        cursor = conn.cursor()
        table_name = view_item['Domain'] + "." + view_item['DatasetName']
        revoke_table_query = f"REVOKE ALL ON TABLE {table_name} FROM GROUP {group_name};"
        cursor.execute(revoke_table_query)
        conn.commit()
        cursor.close()
        LOGGER.info('In redshiftUtil.revoke_group_permissions_to_redshift_views, successfully revoked access to group %s on view %s', group_name, view_item['DatasetName'])
    except Exception as ex:
        ec_rs_1009 = errorUtil.get_error_object("RS-1009")
        ec_rs_1009['Message'] = ec_rs_1009['Message'].format(str(group_name), "view", view_item['DatasetName'], str(ex).rstrip())
        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1009) from ex


def extract_db_schemas(conn):
    """
    This method is to get list of all the existing schema's in the redshift cluster
    :param conn: Redshift connection
    :return: List of all existing schemas
    """
    try:
        LOGGER.info('In redshiftUtil.extract_db_schemas, Retrieving existing schemas')
        cursor = conn.cursor()
        ##### Very Important to include "nspowner != 1" in where-clause which excludes system schemas #####
        database_query = """select nspname from pg_catalog.pg_namespace
                            where nspname not in ('information_schema', 'pg_catalog', 'public')
                            and nspowner != 1
                            and nspname not like 'pg_toast%'
                            and nspname not like 'pg_temp_%';"""
        cursor.execute(database_query)
        response = cursor.fetchall()
        schema_list = []
        for row in response:
            if not "pg_" in row[0]:
                schema_list.append(row[0])
        conn.commit()
        cursor.close()
        LOGGER.info('In redshiftUtil.extract_db_schemas, schema list %s', schema_list)
    except Exception as ex:
        ec_rs_1010 = errorUtil.get_error_object("RS-1010")
        ec_rs_1010['Message'] = ec_rs_1010['Message'].format(str(ex).rstrip())
        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1010) from ex
    return schema_list


def extract_db_schema_tables(conn, schema_name):
    """
    This method is to get list of all the existing schema's in the redshift cluster
    :param conn: Redshift connection
    :param schema_name: Schema name for which the tables are retrieved
    :return: List of table names
    """
    try:
        LOGGER.info('In redshiftUtil.extract_db_schema_tables, Retrieving existing schemas')
        cursor = conn.cursor()
        tables_query = "select table_name from information_schema.tables where table_schema = '{0}'".format(schema_name)
        cursor.execute(tables_query)
        response = cursor.fetchall()
        table_list = []
        for row in response:
            table_list.append(row[0])
        conn.commit()
        cursor.close()
        LOGGER.info('In redshiftUtil.extract_db_schema_tables, table list %s', table_list)
    except Exception as ex:
        ec_rs_1010 = errorUtil.get_error_object("RS-1010")
        ec_rs_1010['Message'] = ec_rs_1010['Message'].format(str(ex).rstrip())
        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1010) from ex
    return table_list


def extract_rs_groups(conn):
    """
    This method is to get list of all the existing group's in the redshift cluster
    :param conn: Redshift connection
    :return: List of group names
    """
    try:
        LOGGER.info('In redshiftUtil.extract_rs_groups, Retrieving existing schemas')
        cursor = conn.cursor()
        cursor.execute("select * from pg_group")
        response = cursor.fetchall()
        groups_list = [row[0] for row in response]
        conn.commit()
        cursor.close()
        LOGGER.info('In redshiftUtil.extract_rs_groups, table list %s', groups_list)
    except Exception as ex:
        ec_rs_1023 = errorUtil.get_error_object("RS-1023")
        ec_rs_1023['Message'] = ec_rs_1023['Message'].format(str(ex).rstrip())
        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1023) from ex
    return groups_list

def validate_data_type(input_data_type):
    """
    This method is used to validate the data type
    """
    LOGGER.info("In redshiftUtil.validate_data_type method, with input data type %s", input_data_type)
    is_data_type_valid = False
    input_data_type_upper = input_data_type.upper()

    for data_type,value in DATA_TYPE_PATTERNS.items():
        #checking for the data type
        is_data_type_valid = input_data_type_upper.startswith(data_type) and re.match(value, input_data_type_upper)
        if is_data_type_valid:
            LOGGER.info("In redshiftUtil.validate_data_type method, input data type %s is valid", input_data_type)
            break

    if not is_data_type_valid:
        LOGGER.error("In redshiftUtil.validate_data_type method, input data type %s is invalid", input_data_type)
        ec_rs_1025 = errorUtil.get_error_object("RS-1025")
        ec_rs_1025['Message'] = ec_rs_1025['Message'].format(input_data_type)
        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1025)

def validate_schema(input_schema):
    """
    This method is used to validate schema of a table
    """
    LOGGER.info("In redshiftUtil.validate_schema method, with input schema %s", input_schema)
    # Read the allowed data types from the file
    try:
        with open("/var/lang/lib/python3.12/site-packages/redshift_data_types.json", 'r', encoding="utf8") as file_reader:
            allowed_data_types = json.load(file_reader)
    except Exception as ex:
        # Fallback for Glue jobs where file is in a different location
        LOGGER.error("In redshiftUtil.validate_schema method, error encountered is %s", ex)
        with open(errorUtil.get_referenced_filepath("redshift_data_types.json"), 'r', encoding="utf8") as file_reader:
            allowed_data_types = json.load(file_reader)
    for item in input_schema:
        # Validating regex for allowed data types
        validate_data_type(item["type"])

        # Extracting & Validating limit or precision/scale for ["NUMERIC", "DECIMAL", "VARCHAR", "CHAR"] data types
        if "(" in item["type"] and ")" in item["type"]:
            try:
                data_type, precision_scale = re.search(r'(.*?)\((.*?)\)', item["type"]).groups()
                if "," in precision_scale:
                    # Is decimal
                    precision, scale = list(map(int, precision_scale.split(",")))
                else:
                    # Retain varchar(max) as is and don't convert it to integer
                    precision = int(precision_scale) if "char(max)" not in item["type"].lower().replace(" ", "") else "max"
                    scale = 0
            except Exception as e_x:
                LOGGER.error("In redshiftUtil.validate_schema method, error encountered is %s", e_x)
                ec_rs_1011 = errorUtil.get_error_object("RS-1011")
                raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1011) from e_x
            # validating input data type
            data_type_uppercase = data_type.upper()
            if data_type_uppercase in ["NUMERIC", "DECIMAL", "VARCHAR", "CHAR", "VARBINARY"]:
                if scale and data_type_uppercase not in ["DECIMAL", "NUMERIC"]:
                    ec_rs_1012 = errorUtil.get_error_object("RS-1012")
                    ec_rs_1012['Message'] = ec_rs_1012['Message'].format(item["type"])
                    raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1012)
                elif precision == "max" and "CHAR" in data_type_uppercase:
                    LOGGER.info("In redshiftUtil.validate_schema method, doing nothing because column type is of char or varchar (max)")
                else:
                    if precision < 1:
                        ec_rs_1014 = errorUtil.get_error_object("RS-1014")
                        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1014)
                    if allowed_data_types[data_type_uppercase]["Precision"] < precision:
                        ec_rs_1015 = errorUtil.get_error_object("RS-1015")
                        ec_rs_1015['Message'] = ec_rs_1015['Message'].format(allowed_data_types[data_type_uppercase]["Precision"], data_type_uppercase)
                        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1015)
                    if scale > precision:
                        ec_rs_1016 = errorUtil.get_error_object("RS-1016")
                        ec_rs_1016['Message'] = ec_rs_1016['Message'].format(item["name"], item["type"])
                        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1016)
            else:
                ec_rs_1013 = errorUtil.get_error_object("RS-1013")
                ec_rs_1013['Message'] = ec_rs_1013['Message'].format(item["name"], list(allowed_data_types.keys()))
                raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1013)
        elif item["type"].upper() not in allowed_data_types:
            ec_rs_1013 = errorUtil.get_error_object("RS-1013")
            ec_rs_1013['Message'] = ec_rs_1013['Message'].format(item["name"], list(allowed_data_types.keys()))
            raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1013)

    LOGGER.info("In redshiftUtil.validate_schema method, exiting")


def extract_domains_from_view_sql_statement(sql_statement, list_of_domains_from_db):
    """
    Extracts domains from sql statements to check user dataset access
    :param sql_statement: sql statement entered by the user
    :param list_of_domains_from_db:
    :return: list of domains on which view is being created
    """
    LOGGER.info("In redshiftUtil.extract_domains_from_view_sql_statement, list of domains read - %s", list_of_domains_from_db)
    # Create a dict of domain names original and lower case
    domains_original_and_lower_case_dict = dict((domain_name['DomainName'].lower(), domain_name['DomainName']) for domain_name in list_of_domains_from_db)
    list_of_strings_after_splitting_sql_by_white_spaces = sql_statement.split()
    # Check if domain from query matches with lower case existing domains if yes
    # get the name of the original domains to perform further access checks
    # using rstrip to remove trailing ; ( ) in the domains names
    # removal of parenthesis is needed in case of queries containing sub-selects
    list_of_domain_names = [domains_original_and_lower_case_dict[domain_dataset_str.lower().split('.', 1)[0].rstrip(';()')]
                            for domain_dataset_str in list_of_strings_after_splitting_sql_by_white_spaces
                            if '.' in domain_dataset_str and domain_dataset_str.lower().split('.', 1)[0].rstrip(';()')
                            in domains_original_and_lower_case_dict.keys()]
    # return the list after removing duplicates
    return list(set(list_of_domain_names))


def get_redshift_cluster_details(dwh_cluster_endpoint):
    """
    This method retrieves the redshift cluster details.
    :param dwh_cluster_endpoint: redshift cluster endpoint eg: cluster-identifier.account_id.eu-west-1.redshift.amazonaws.com
    :return: Returns redshift raw cluster details
    """
    LOGGER.info("In redshiftUtil.get_redshift_cluster_details, Retrieving information for redshift cluster id - %s", dwh_cluster_endpoint)
    raw_cluster_details = []
    try:
        if REDSHIFT_CLUSTER_TYPE == "serverless":
            # get the serverless cluster details.
            client = boto3.client('redshift-serverless')
            dwh_workgroup_name = dwh_cluster_endpoint.split(".")[0]
            response = client.get_workgroup(workgroupName=dwh_workgroup_name)
            LOGGER.info("In redshiftUtil.get_redshift_cluster_status, redshift serverless workgroup response - %s", response)
            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                LOGGER.error("In redshiftUtil.get_redshift_cluster_status, Unable retrieve cluster information - %s, error response - %s", dwh_cluster_endpoint, response)
                ec_dwh_1002 = errorUtil.get_error_object("DWH-1002")
                ec_dwh_1002['Message'] = ec_dwh_1002['Message'].format("", response)
                raise errorUtil.GenericFailureException(EVENT_INFO, ec_dwh_1002)
            return response.get("workgroup", {})
        else:
            # get the regular redshift cluster details.
            client = boto3.client('redshift')
            dwh_cluster_name = dwh_cluster_endpoint.split(".")[0]
            response = client.describe_clusters(ClusterIdentifier=dwh_cluster_name)
            if response['ResponseMetadata']['HTTPStatusCode'] != 200:
                LOGGER.error("In redshiftUtil.get_redshift_cluster_status, Unable retrieve cluster information - %s, error response - %s", dwh_cluster_endpoint, response)
                ec_dwh_1002 = errorUtil.get_error_object("DWH-1002")
                ec_dwh_1002['Message'] = ec_dwh_1002['Message'].format("", response)
                raise errorUtil.GenericFailureException(EVENT_INFO, ec_dwh_1002)
            for cluster_info in response['Clusters']:
                if cluster_info['ClusterIdentifier'] == dwh_cluster_name:
                    raw_cluster_details.append(cluster_info)
            LOGGER.info("In redshiftUtil.get_redshift_cluster_details, Retrieved redshift raw cluster details - %s", raw_cluster_details)
            return raw_cluster_details
    except Exception as msg:
        LOGGER.error("In redshiftUtil.get_redshift_cluster_status, Exception occurred while retrieving cluster details - %s", msg)
        ec_ge_1016 = errorUtil.get_error_object("GE-1016")
        ec_ge_1016['Message'] = ec_ge_1016['Message'].format(msg)
        raise errorUtil.GenericFailureException(EVENT_INFO, ec_ge_1016)

def get_redshift_cluster_status(dwh_cluster_endpoint):
    """
    This method retrieves the redshift cluster status.
    :param dwh_cluster_endpoint: redshift cluster endpoint eg: cluster-identifier.account_id.eu-west-1.redshift.amazonaws.com
    :return: Returns redshift cluster status (eg: available, unavailable, paused, etc.)
    """
    LOGGER.info("In redshiftUtil.get_redshift_cluster_status, Retrieving information for redshift cluster id - %s", dwh_cluster_endpoint)
    cluster_status = "unavailable"
    raw_cluster_details = get_redshift_cluster_details(dwh_cluster_endpoint)
    if REDSHIFT_CLUSTER_TYPE == "serverless":
        cluster_status = raw_cluster_details.get("status", cluster_status).lower()
    elif raw_cluster_details:
        cluster_status = raw_cluster_details[0].get("ClusterAvailabilityStatus", cluster_status).lower()
    LOGGER.info("In redshiftUtil.get_redshift_cluster_status, Retrieved redshift cluster status - %s", cluster_status)
    return cluster_status

def is_redshift_cluster_available(dwh_cluster_endpoint):
    """
    This method raises exception if redshift cluster is not in available state
    """
    if get_redshift_cluster_status(dwh_cluster_endpoint) != "available":
        LOGGER.error('In redshiftUtil.is_redshift_cluster_available, redshift cluster is not available')
        ec_rs_1026 = errorUtil.get_error_object("RS-1026")
        raise errorUtil.GenericFailureException(EVENT_INFO, ec_rs_1026)


def extract_dbs(conn):
    """
    This method is to get list of all the existing databases in the redshift cluster
    :param conn: Redshift connection
    :return: List of all existing databases
    """
    try:
        LOGGER.info('In redshiftUtil.extract_dbs, Retrieving existing databases')
        cursor = conn.cursor()
        list_database_query = """SELECT * FROM pg_catalog.pg_database;"""
        cursor.execute(list_database_query)
        response = cursor.fetchall()
        db_list = [row[0] for row in response]
        conn.commit()
        cursor.close()
        LOGGER.info('In redshiftUtil.extract_db_schemas, database list %s', db_list)
    except Exception as ex:
        ec_rs_1010 = errorUtil.get_error_object("RS-1010")
        ec_rs_1010['Message'] = ec_rs_1010['Message'].format(str(ex).rstrip())
        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1010) from ex
    return db_list


def validate_rs_users(user_list, conn):
    """
    This method is to validate the list of users if they exist in the redshift cluster
    :param conn: Redshift connection
    :param user_list: List of users to validate
    :return: List of all existing databases
    """
    try:
        LOGGER.info('In redshiftUtil.validate_rs_users, Validating users - %s', user_list)
        cursor = conn.cursor()
        list_users_query = """SELECT * FROM PG_USER WHERE USENAME in ({});""".format(', '.join(["'{}'".format(user_name) for user_name in user_list]))
        cursor.execute(list_users_query)
        response = cursor.fetchall()
        existing_user_list = [row[0] for row in response]
        invalid_user_list = set(user_list) - set(existing_user_list)
        users_results_items = {"ValidUsers": existing_user_list, "InvalidUsers": list(invalid_user_list)}
        conn.commit()
        cursor.close()
        LOGGER.info('In redshiftUtil.validate_rs_users, redshift user response - %s', users_results_items)
    except Exception as ex:
        conn.commit()
        ec_rs_1017 = errorUtil.get_error_object("RS-1017")
        ec_rs_1017['Message'] = ec_rs_1017['Message'].format(str(ex).rstrip())
        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1017) from ex
    return users_results_items


def assign_dataset_level_perms_to_redshift_group(group_name, access_type, domain, conn):
    """
    This function will assign permissions of all the tables under a domain to the group
    :param group_name
    :param access_type
    :param domain
    :param conn
    """
    LOGGER.info('In redshiftUtil.assign_dataset_level_perms_to_redshift_group, Assigning permissions of \
        all tables under the domain %s to the group %s', domain, group_name)
    try:
        cursor = conn.cursor()
        grant_schema_query = f"GRANT USAGE ON SCHEMA {domain} TO GROUP {group_name};"
        grant_all_tables_in_schema = f"GRANT SELECT ON ALL TABLES IN SCHEMA {domain} TO GROUP {group_name};"
        # To enable access of new tables created later
        alter_default_privileges = f"ALTER DEFAULT PRIVILEGES IN SCHEMA {domain} GRANT SELECT ON TABLES TO GROUP {group_name};"
        cursor.execute(grant_schema_query)
        cursor.execute(grant_all_tables_in_schema)
        cursor.execute(alter_default_privileges)
        if access_type in REDSHIFT_TABLE_PERMISSIONS.keys():
            grant_schema_create_query = f"GRANT CREATE ON SCHEMA {domain} TO GROUP {group_name};"
            cursor.execute(grant_schema_create_query)
            permissions_query = f"GRANT {','.join(REDSHIFT_TABLE_PERMISSIONS[access_type])} ON ALL TABLES IN SCHEMA {domain} TO GROUP {group_name};"
            # To enable access of new tables created later
            alter_default_privileges_new_perms = f"ALTER DEFAULT PRIVILEGES IN SCHEMA {domain} GRANT {','.join(REDSHIFT_TABLE_PERMISSIONS[access_type])} ON TABLES TO GROUP {group_name};"
            cursor.execute(permissions_query)
            cursor.execute(alter_default_privileges_new_perms)
        conn.commit()
        cursor.close()
        LOGGER.info('In redshiftUtil.assign_dataset_level_perms_to_redshift_group, Successfully assigned permissions of \
            all tables under the domain %s to the group %s', domain, group_name)
    except Exception as ex:
        conn.commit()
        ec_rs_1008 = errorUtil.get_error_object("RS-1008")
        ec_rs_1008['Message'] = ec_rs_1008['Message'].format(str(group_name), "domain", domain, str(ex).rstrip())
        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1008) from ex


def revoke_dataset_level_perms_from_redshift_group(group_name, access_type, domain, conn):
    """
    This function will revoke permissions of all the tables under a domain from the group
    :param group_name
    :param access_type
    :param domain
    :param conn
    """
    LOGGER.info('In redshiftUtil.revoke_dataset_level_perms_from_redshift_group, Revoking permissions of \
        all tables under the domain %s from the group %s', domain, group_name)
    try:
        cursor = conn.cursor()
        revoke_all_tables_in_schema = f"REVOKE SELECT ON ALL TABLES IN SCHEMA {domain} FROM GROUP {group_name};"
        # Alter default privileges
        alter_default_privileges = f"ALTER DEFAULT PRIVILEGES IN SCHEMA {domain} REVOKE SELECT ON TABLES FROM GROUP {group_name};"
        cursor.execute(revoke_all_tables_in_schema)
        cursor.execute(alter_default_privileges)
        if access_type in REDSHIFT_TABLE_PERMISSIONS.keys():
            revoke_schema_create_query = f"REVOKE CREATE ON SCHEMA {domain} FROM GROUP {group_name};"
            cursor.execute(revoke_schema_create_query)
            permissions_query = f"REVOKE {','.join(REDSHIFT_TABLE_PERMISSIONS[access_type])} ON ALL TABLES IN SCHEMA {domain} FROM GROUP {group_name};"
            # To enable access of new tables created later
            alter_default_privileges_new_perms = f"ALTER DEFAULT PRIVILEGES IN SCHEMA {domain} REVOKE {','.join(REDSHIFT_TABLE_PERMISSIONS[access_type])} ON TABLES FROM GROUP {group_name};"
            cursor.execute(permissions_query)
            cursor.execute(alter_default_privileges_new_perms)
        conn.commit()
        cursor.close()
        LOGGER.info('In redshiftUtil.revoke_dataset_level_perms_from_redshift_group, Successfully revoked permissions of \
            all tables under the domain %s from the group %s', domain, group_name)
    except Exception as ex:
        conn.commit()
        ec_rs_1009 = errorUtil.get_error_object("RS-1009")
        ec_rs_1009['Message'] = ec_rs_1009['Message'].format(str(group_name), "domain", domain, str(ex).rstrip())
        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1009) from ex


def assign_dataset_level_perms_to_redshift_user(user_name, access_type, domain, conn):
    """
    This function will assign permissions of all the tables under a domain to the specified user
    :param user_name
    :param domain
    :param conn
    """
    LOGGER.info('In redshiftUtil.assign_dataset_level_perms_to_redshift_user, Assigning permissions of all tables under the domain %s to the user %s', domain, user_name)
    try:
        cursor = conn.cursor()
        grant_schema_query = f"GRANT USAGE ON SCHEMA {domain} TO {user_name};"
        grant_all_tables_in_schema = f"GRANT SELECT ON ALL TABLES IN SCHEMA {domain} TO {user_name};"
        # To enable access of new tables created later
        alter_default_privileges = f"ALTER DEFAULT PRIVILEGES IN SCHEMA {domain} GRANT SELECT ON TABLES TO {user_name};"
        cursor.execute(grant_schema_query)
        cursor.execute(grant_all_tables_in_schema)
        cursor.execute(alter_default_privileges)
        if access_type in REDSHIFT_TABLE_PERMISSIONS.keys():
            grant_schema_create_query = f"GRANT CREATE ON SCHEMA {domain} TO {user_name};"
            cursor.execute(grant_schema_create_query)
            permissions_query = f"GRANT {','.join(REDSHIFT_TABLE_PERMISSIONS[access_type])} ON ALL TABLES IN SCHEMA {domain} TO {user_name};"
            # To enable access of new tables created later
            alter_default_privileges_new_perms = f"ALTER DEFAULT PRIVILEGES IN SCHEMA {domain} GRANT {','.join(REDSHIFT_TABLE_PERMISSIONS[access_type])} ON TABLES TO {user_name};"
            cursor.execute(permissions_query)
            cursor.execute(alter_default_privileges_new_perms)
        conn.commit()
        cursor.close()
        LOGGER.info('In redshiftUtil.assign_dataset_level_perms_to_redshift_user, Successfully assigned permissions of \
            all tables under the domain %s to the user %s', domain, user_name)
    except Exception as ex:
        ec_rs_1008 = errorUtil.get_error_object("RS-1008")
        ec_rs_1008['Message'] = ec_rs_1008['Message'].format(str(user_name), "domain", domain, str(ex).rstrip())
        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1008) from ex


def revoke_dataset_level_perms_from_redshift_user(user_name, access_type, domain, conn):
    """
    This function will revoke permissions of all the tables under a domain from the specified user
    :param user_name
    :param domain
    :param conn
    """
    LOGGER.info('In redshiftUtil.revoke_dataset_level_perms_from_redshift_user, Revoking permissions of all tables under the domain %s from the user %s', domain, user_name)
    try:
        cursor = conn.cursor()
        revoke_all_tables_in_schema = f"REVOKE SELECT ON ALL TABLES IN SCHEMA {domain} FROM {user_name};"
        # Alter default privileges
        alter_default_privileges = f"ALTER DEFAULT PRIVILEGES IN SCHEMA {domain} REVOKE SELECT ON TABLES FROM {user_name};"
        cursor.execute(revoke_all_tables_in_schema)
        cursor.execute(alter_default_privileges)
        if access_type in REDSHIFT_TABLE_PERMISSIONS.keys():
            revoke_schema_create_query = f"REVOKE CREATE ON SCHEMA {domain} FROM {user_name};"
            cursor.execute(revoke_schema_create_query)
            permissions_query = f"REVOKE {','.join(REDSHIFT_TABLE_PERMISSIONS[access_type])} ON ALL TABLES IN SCHEMA {domain} FROM {user_name};"
            # To enable access of new tables created later
            alter_default_privileges_new_perms = f"ALTER DEFAULT PRIVILEGES IN SCHEMA {domain} REVOKE {','.join(REDSHIFT_TABLE_PERMISSIONS[access_type])} ON TABLES FROM {user_name};"
            cursor.execute(permissions_query)
            cursor.execute(alter_default_privileges_new_perms)
        conn.commit()
        cursor.close()
        LOGGER.info('In redshiftUtil.revoke_dataset_level_perms_from_redshift_user, Successfully revoked permissions of all tables under the domain %s from the user %s', domain, user_name)
    except Exception as ex:
        ec_rs_1009 = errorUtil.get_error_object("RS-1009")
        ec_rs_1009['Message'] = ec_rs_1009['Message'].format(str(user_name), "domain", domain, str(ex).rstrip())
        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1009) from ex

def add_column_description(table_name, input_schema, conn):
    """
    This function will add description of all the columns in a table
    :param table_name: name of redshift table
    :param input_schema: schema of redshift table that includes name, type and description of columns
    :param conn: redshift connection
    """
    LOGGER.info('In redshiftUtil.update_column_description, Updating description of all columns in the table %s, schema %s', table_name, input_schema)
    try:
        cursor = conn.cursor()
        for item in input_schema:
            if 'description' in item:
                add_comment_query = "COMMENT ON COLUMN {}.{} is '{}'".format(table_name, item["name"], item["description"])
                cursor.execute(add_comment_query)
        conn.commit()
        cursor.close()
    except Exception as ex:
        LOGGER.error('In redshiftUtil.update_column_description, error while updating column description - %s', str(ex))
        rs_ds_1017 = errorUtil.get_error_object("RS-1017")
        rs_ds_1017["Message"] = str(ex)
        raise errorUtil.GenericFailureException(EVENT_INFO, rs_ds_1017)

def validate_views_exists_in_redshift(domain_name, view_name, conn):
    """
    This method is to validate the view exist in the redshift cluster
    :param conn: Redshift connection
    :param view_name: View to validate
    :param domain_name: Domain name
    :param tenant_name: Tenant name
    :return: List of all existing views
    """
    try:
        LOGGER.info('In redshiftUtil.validate_views_exists_in_redshift, Validating view - %s', view_name)
        cursor = conn.cursor()
        check_view_exists_query = f"SELECT 1 FROM SVV_REDSHIFT_TABLES WHERE schema_name = '{domain_name}' AND table_name = '{view_name}';"
        cursor.execute(check_view_exists_query)
        response = cursor.fetchall()
        if response:
            view_result = {"ValidViews": view_name}
        else:
            view_result = {'InvalidViews': view_name}
        LOGGER.info('In redshiftUtil.validate_views_exists_in_redshift, response - %s', response)
        conn.commit()
        cursor.close()
        view_result = {"ValidViews": view_name}
    except Exception as ex:
        conn.commit()
        if 'does not exist' in str(ex):
            LOGGER.error("In redshiftUtil.validate_views_exists_in_redshift, exception since view does not exist in redshift")
            view_result = {'InvalidViews': view_name}
        else:
            LOGGER.error("In redshiftUtil.validate_views_exists_in_redshift, exception while trying to execute redshift query - %s", str(ex))
            raise ex
    LOGGER.info('In redshiftUtil.validate_views_exists_in_redshift, redshift user response - %s', view_result)
    return view_result


# ---------- Redshift Role per Tag (for RLS/CLS) ----------
REDSHIFT_ROLE_NAME_PREFIX = "role_"
REDSHIFT_RLS_POLICY_NAME_PREFIX = "rls_"
REDSHIFT_IDENTIFIER_MAX_LEN = 127


def get_tag_redshift_role_name(tag_key, tag_value):
    """
    Return Redshift role name for a tag: role_{TagKey}_{TagValue}.
    Must be valid Redshift identifier (lowercase, no #; use _).
    :param tag_key: Tag key
    :param tag_value: Tag value
    :return: role name string (max 127 chars)
    """
    safe_key = (tag_key or "").strip().lower().replace("-", "_")[:64]
    safe_value = (tag_value or "").strip().lower().replace("-", "_")[:64]
    name = f"{REDSHIFT_ROLE_NAME_PREFIX}{safe_key}_{safe_value}"[:REDSHIFT_IDENTIFIER_MAX_LEN]
    return name


def create_redshift_role(role_name, creator_username, conn):
    """
    Create a Redshift role and grant it to the creator user.
    :param role_name: Role name (e.g. from get_tag_redshift_role_name)
    :param creator_username: Redshift username of the creator
    :param conn: Redshift connection
    """
    try:
        LOGGER.info("In redshiftUtil.create_redshift_role, Creating role - %s", role_name)
        cursor = conn.cursor()
        cursor.execute("CREATE ROLE %s" % (role_name,))
        cursor.execute("GRANT ROLE %s TO %s" % (role_name, creator_username))
        conn.commit()
        cursor.close()
        LOGGER.info("In redshiftUtil.create_redshift_role, Successfully created role and granted to creator - %s", role_name)
    except Exception as ex:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        ec_rs_1004 = errorUtil.get_error_object("RS-1004")
        ec_rs_1004["Message"] = ec_rs_1004["Message"].format(str(ex).rstrip())
        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1004) from ex


def grant_redshift_role_to_users(role_name, user_list, conn):
    """
    Grant the Redshift role to the given users.
    :param role_name: Role name
    :param user_list: Comma-separated string or list of Redshift usernames
    :param conn: Redshift connection
    """
    if isinstance(user_list, list):
        user_list = ",".join(user_list)
    if not user_list or not user_list.strip():
        return
    try:
        LOGGER.info("In redshiftUtil.grant_redshift_role_to_users, Granting role %s to users - %s", role_name, user_list)
        cursor = conn.cursor()
        for user in [u.strip() for u in user_list.split(",") if u.strip()]:
            cursor.execute("GRANT ROLE %s TO %s" % (role_name, user))
        conn.commit()
        cursor.close()
        LOGGER.info("In redshiftUtil.grant_redshift_role_to_users, Successfully granted role to users")
    except Exception as ex:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        ec_rs_1006 = errorUtil.get_error_object("RS-1006")
        ec_rs_1006["Message"] = ec_rs_1006["Message"].format(str(ex).rstrip())
        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1006) from ex


def revoke_redshift_role_from_users(role_name, user_list, conn):
    """
    Revoke the Redshift role from the given users.
    :param role_name: Role name
    :param user_list: Comma-separated string or list of Redshift usernames
    :param conn: Redshift connection
    """
    if isinstance(user_list, list):
        user_list = ",".join(user_list)
    if not user_list or not user_list.strip():
        return
    try:
        LOGGER.info("In redshiftUtil.revoke_redshift_role_from_users, Revoking role %s from users - %s", role_name, user_list)
        cursor = conn.cursor()
        for user in [u.strip() for u in user_list.split(",") if u.strip()]:
            try:
                cursor.execute("REVOKE ROLE %s FROM %s" % (role_name, user))
            except Exception as rev_ex:
                if "does not have role" in str(rev_ex).lower() or "not a member" in str(rev_ex).lower():
                    LOGGER.info("In redshiftUtil.revoke_redshift_role_from_users, User %s did not have role, skipping", user)
                else:
                    raise rev_ex
        conn.commit()
        cursor.close()
        LOGGER.info("In redshiftUtil.revoke_redshift_role_from_users, Successfully revoked role from users")
    except Exception as ex:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        ec_rs_1007 = errorUtil.get_error_object("RS-1007")
        ec_rs_1007["Message"] = ec_rs_1007["Message"].format(str(ex).rstrip())
        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1007) from ex


def delete_redshift_role(role_name, conn):
    """
    Revoke role from all users, detach RLS policies from the role, then drop the role.
    :param role_name: Role name
    :param conn: Redshift connection
    """
    try:
        LOGGER.info("In redshiftUtil.delete_redshift_role, Deleting Redshift role - %s", role_name)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT user_name FROM SVV_USER_GRANTS WHERE role_name = %s",
                (role_name,)
            )
            members = cursor.fetchall()
            for row in members:
                try:
                    cursor.execute("REVOKE ROLE %s FROM %s" % (role_name, row[0]))
                except Exception as rev_ex:
                    LOGGER.info("In redshiftUtil.delete_redshift_role, Revoke from %s: %s", row[0], rev_ex)
        except Exception as list_ex:
            LOGGER.info("In redshiftUtil.delete_redshift_role, Listing role members: %s", list_ex)
        try:
            cursor.execute(
                "SELECT polname, relschema, relname FROM SVV_RLS_ATTACHED_POLICY WHERE grantee = %s AND granteekind = 'role'",
                (role_name,)
            )
            for row in cursor.fetchall():
                full_table = "%s.%s" % (row[1], row[2])
                cursor.execute("DETACH RLS POLICY %s ON TABLE %s FROM ROLE %s" % (row[0], full_table, role_name))
        except Exception as detach_ex:
            LOGGER.info("In redshiftUtil.delete_redshift_role, Detach RLS (may not exist): %s", detach_ex)
        cursor.execute("DROP ROLE %s" % (_sanitize_identifier(role_name),))
        conn.commit()
        cursor.close()
        LOGGER.info("In redshiftUtil.delete_redshift_role, Successfully deleted role - %s", role_name)
    except Exception as ex:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        if "does not exist" in str(ex).lower():
            LOGGER.info("In redshiftUtil.delete_redshift_role, Role %s does not exist, skipping", role_name)
            return
        ec_rs_1005 = errorUtil.get_error_object("RS-1005")
        ec_rs_1005["Message"] = ec_rs_1005["Message"].format(str(ex).rstrip())
        raise errorUtil.RedshiftTableException(EVENT_INFO, ec_rs_1005) from ex


# ---------- Redshift RLS/CLS helpers ----------
def _sanitize_identifier(name):
    """Return a safe Redshift identifier (max 127 chars, no double quotes in value)."""
    s = (name or "").strip().replace(" ", "_").replace("-", "_")[:REDSHIFT_IDENTIFIER_MAX_LEN]
    return s


def get_redshift_rls_policy_name(domain, dataset_name, filter_name):
    """Build RLS policy name: rls_{domain}_{dataset_name}_{filter_name} (max 127 chars)."""
    base = "%s%s_%s_%s" % (
        REDSHIFT_RLS_POLICY_NAME_PREFIX,
        _sanitize_identifier(domain),
        _sanitize_identifier(dataset_name),
        _sanitize_identifier(filter_name),
    )
    return base[:REDSHIFT_IDENTIFIER_MAX_LEN]


def enable_rls_on_table(table_name, conn):
    """
    Enable row-level security on the table (if supported).
    :param table_name: schema.table
    :param conn: Redshift connection
    """
    try:
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE %s ROW LEVEL SECURITY ON" % (table_name,))
        conn.commit()
        cursor.close()
        LOGGER.info("In redshiftUtil.enable_rls_on_table, Enabled RLS on %s", table_name)
    except Exception as ex:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        LOGGER.info("In redshiftUtil.enable_rls_on_table, RLS enable (may already be enabled): %s", ex)


def create_rls_policy(policy_name, using_predicate, conn, with_columns=None):
    """
    Create an RLS policy with USING (predicate).
    :param policy_name: Policy name
    :param using_predicate: SQL expression for USING (e.g. "region = 'US'" or "true")
    :param conn: Redshift connection
    :param with_columns: List of dicts [{"name": "col", "type": "varchar"}, ...] for the WITH clause.
                         Required when the USING predicate references table columns.
    """
    try:
        cursor = conn.cursor()
        with_clause = ""
        if with_columns:
            col_defs = ", ".join("%s %s" % (c["name"], c["type"]) for c in with_columns)
            with_clause = "WITH (%s) " % col_defs
        sql = "CREATE RLS POLICY %s %sUSING (%s)" % (policy_name, with_clause, using_predicate)
        LOGGER.info("In redshiftUtil.create_rls_policy, SQL: %s", sql)
        cursor.execute(sql)
        conn.commit()
        cursor.close()
        LOGGER.info("In redshiftUtil.create_rls_policy, Created RLS policy - %s", policy_name)
    except Exception as ex:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        raise ex


def attach_rls_policy_to_role(policy_name, table_name, role_name, conn):
    """Attach RLS policy on table to role."""
    try:
        cursor = conn.cursor()
        cursor.execute("ATTACH RLS POLICY %s ON TABLE %s TO ROLE %s" % (policy_name, table_name, role_name))
        conn.commit()
        cursor.close()
    except Exception as ex:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        raise ex


def attach_rls_policy_to_user(policy_name, table_name, user_name, conn):
    """Attach RLS policy on table to user."""
    try:
        cursor = conn.cursor()
        cursor.execute("ATTACH RLS POLICY %s ON TABLE %s TO %s" % (policy_name, table_name, user_name))
        conn.commit()
        cursor.close()
    except Exception as ex:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        raise ex


def detach_rls_policy_from_role(policy_name, table_name, role_name, conn):
    """Detach RLS policy on table from role."""
    try:
        cursor = conn.cursor()
        cursor.execute("DETACH RLS POLICY %s ON TABLE %s FROM ROLE %s" % (policy_name, table_name, role_name))
        conn.commit()
        cursor.close()
    except Exception as ex:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        LOGGER.info("In redshiftUtil.detach_rls_policy_from_role, %s", ex)


def detach_rls_policy_from_user(policy_name, table_name, user_name, conn):
    """Detach RLS policy on table from user."""
    try:
        cursor = conn.cursor()
        cursor.execute("DETACH RLS POLICY %s ON TABLE %s FROM %s" % (policy_name, table_name, user_name))
        conn.commit()
        cursor.close()
    except Exception as ex:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        LOGGER.info("In redshiftUtil.detach_rls_policy_from_user, %s", ex)


def drop_rls_policy(policy_name, conn, cascade=True):
    """
    Drop RLS policy. Use CASCADE to detach from all before dropping.
    :param policy_name: Policy name
    :param conn: Redshift connection
    :param cascade: If True, use DROP RLS POLICY ... CASCADE
    """
    try:
        cursor = conn.cursor()
        cursor.execute("DROP RLS POLICY %s %s" % (policy_name, "CASCADE" if cascade else "RESTRICT"))
        conn.commit()
        cursor.close()
        LOGGER.info("In redshiftUtil.drop_rls_policy, Dropped RLS policy - %s", policy_name)
    except Exception as ex:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        if "does not exist" in str(ex).lower():
            LOGGER.info("In redshiftUtil.drop_rls_policy, Policy %s does not exist", policy_name)
            return
        raise ex


def revoke_table_select_redshift(table_name, principal_name, conn, is_role=True):
    """
    REVOKE SELECT ON TABLE from a user or role.
    Must be done before granting column-level SELECT so that only specific columns are accessible.
    :param table_name: schema.table
    :param principal_name: Role or user name
    :param conn: Redshift connection
    :param is_role: If True, principal is a ROLE; else USER
    """
    try:
        cursor = conn.cursor()
        from_clause = "ROLE %s" % principal_name if is_role else principal_name
        cursor.execute("REVOKE SELECT ON TABLE %s FROM %s" % (table_name, from_clause))
        conn.commit()
        cursor.close()
    except Exception as ex:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        LOGGER.info("In redshiftUtil.revoke_table_select_redshift, %s", ex)


def grant_select_columns_redshift(table_name, columns_list, principal_name, conn, is_role=True):
    """
    GRANT SELECT (col1, col2, ...) ON table TO ROLE role_name / TO user_name.
    :param table_name: schema.table
    :param columns_list: List of column names
    :param principal_name: Role or user name
    :param conn: Redshift connection
    :param is_role: If True, principal is a ROLE; else USER
    """
    if not columns_list:
        return
    try:
        cursor = conn.cursor()
        cols = ", ".join(columns_list)
        to_clause = "ROLE %s" % principal_name if is_role else principal_name
        cursor.execute("GRANT SELECT (%s) ON TABLE %s TO %s" % (cols, table_name, to_clause))
        conn.commit()
        cursor.close()
    except Exception as ex:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        raise ex


def revoke_select_columns_redshift(table_name, columns_list, principal_name, conn, is_role=True):
    """
    REVOKE SELECT (col1, ...) ON table FROM ROLE role_name / FROM user_name.
    :param table_name: schema.table
    :param columns_list: List of column names
    :param principal_name: Role or user name
    :param conn: Redshift connection
    :param is_role: If True, principal is a ROLE; else USER
    """
    if not columns_list:
        return
    try:
        cursor = conn.cursor()
        cols = ", ".join(columns_list)
        from_clause = "ROLE %s" % principal_name if is_role else principal_name
        cursor.execute("REVOKE SELECT (%s) ON TABLE %s FROM %s" % (cols, table_name, from_clause))
        conn.commit()
        cursor.close()
    except Exception as ex:
        if conn:
            try:
                conn.rollback()
            except Exception:
                pass
        LOGGER.info("In redshiftUtil.revoke_select_columns_redshift, %s", ex)
