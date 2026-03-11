"""
Lambda for async Redshift RLS/CLS data permissions (prepare, grant, revoke, delete).
Invoked by RedshiftDataPermissionsStateMachine.
"""
import sys
import os
import copy
import boto3
import commonUtil
import dynamodbUtil
import authUtil
import errorUtil
import redshiftUtil
from loggingUtil import LOGGER
import heartbeatUtil

LOGGER.info("In redshiftDataPermissions, Loading Function")

try:
    DATASET_TABLE = dynamodbUtil.DATASET_TABLE
    DATA_FILTER_TABLE = dynamodbUtil.DATA_FILTER_TABLE
    USER_TABLE = dynamodbUtil.USER_TABLE
    AWS_REGION = os.environ["awsRegion"]
    ACCOUNT_ID = os.environ["accountId"]
    BATCH_SIZE = 20
    EVENT_INFO = errorUtil.EVENT_INFO
    DWH_HOST = os.environ.get("DWHHost")
    DWH_PORT = os.environ.get("DWHPort")
    DWH_USER = os.environ.get("DWHUser")
    DWH_DATABASE = os.environ.get("DWHDatabase")
    DWH_PASSWORD_SECRET_ARN = os.environ.get("redshiftServiceUserSecretArn") or os.environ.get("DWHServiceUserSecretArn")
except Exception as ex:
    LOGGER.error("In redshiftDataPermissions, Failed to set environment variables: %s", ex)
    sys.exit()


def get_redshift_conn():
    """Get Redshift connection using env credentials."""
    password = commonUtil.get_dwh_service_user_password(AWS_REGION, DWH_PASSWORD_SECRET_ARN)
    return redshiftUtil.get_redshift_connection(DWH_HOST, DWH_PORT, DWH_USER, password, DWH_DATABASE)


def prepare_redshift_data_permissions_metadata(event, dynamodb_resource, audit_log_config):
    """
    Resolve AuthorizedTags to user IDs; build Redshift usernames and tag role names; build grant/revoke batches.
    """
    LOGGER.info("In redshiftDataPermissions.prepare_redshift_data_permissions_metadata, event: %s", event)
    body = event.get("DataPermissionsMetadata") or {}
    users_added = []
    users_removed = []
    tags_added = body.get("AuthorizedTags", [])
    tags_removed = body.get("RemovedAuthorizedTags", [])
    dataset_id = event["DatasetId"]
    user_id = event["UserId"]

    for tag_id in tags_added:
        tag_key = tag_id.split("#")[0]
        tag_value = tag_id.split("#")[-1]
        tag_users = (
            authUtil.check_user_access_on_tag(tag_key, tag_value, user_id, dynamodb_resource, audit_log_config).get("UsersAttached", [])
            if tag_key != "user"
            else [tag_value]
        )
        if tag_users:
            users_added.extend(tag_users)

    for tag_id in tags_removed:
        tag_key = tag_id.split("#")[0]
        tag_value = tag_id.split("#")[-1]
        tag_users = (
            authUtil.check_user_access_on_tag(tag_key, tag_value, user_id, dynamodb_resource, audit_log_config).get("UsersAttached", [])
            if tag_key != "user"
            else [tag_value]
        )
        if tag_users:
            users_removed.extend(tag_users)

    data_filter_name = body.get("Name")
    dataset_item = dynamodbUtil.get_item_with_key(dynamodb_resource.Table(DATASET_TABLE), {"DatasetId": dataset_id}, audit_log_config)
    if not dataset_item:
        raise errorUtil.InvalidInputException(EVENT_INFO, {"Message": "Dataset not found: %s" % dataset_id})

    granted_permitted = list(set(users_added))
    revoked_permitted = list(set(users_removed))

    event["details"] = {"items": [], "removed_items": []}
    obj = {
        "Operation": "grant_permission",
        "DataFilterName": data_filter_name,
        "DatasetId": dataset_id,
        "DatasetName": dataset_item.get("DatasetName"),
        "Domain": dataset_item.get("Domain"),
        "AccountId": dataset_item.get("CatalogId", ACCOUNT_ID),
        "DataPermissions": body.get("DataPermissions", body),
    }
    remove_obj = copy.deepcopy(obj)
    remove_obj["Operation"] = "revoke_permission"
    remove_obj["AuthorizedTags"] = list(tags_removed)
    for i in range(0, len(granted_permitted), BATCH_SIZE):
        obj_copy = copy.deepcopy(obj)
        obj_copy["Users"] = granted_permitted[i : i + BATCH_SIZE]
        obj_copy["AuthorizedTags"] = list(tags_added)
        event["details"]["items"].append(obj_copy)
    for j in range(0, len(revoked_permitted), BATCH_SIZE):
        remove_obj_copy = copy.deepcopy(remove_obj)
        remove_obj_copy["Users"] = revoked_permitted[j : j + BATCH_SIZE]
        event["details"]["removed_items"].append(remove_obj_copy)
    if body.get("DeleteFilter"):
        del_obj = copy.deepcopy(remove_obj)
        del_obj["Users"] = []
        del_obj["delete_filter"] = True
        del_obj["AuthorizedTags"] = list(tags_removed)
        event["details"]["removed_items"].append(del_obj)
    return event


def grant_redshift_data_permissions(event, dynamodb_resource, audit_log_config):
    """Create RLS policy (if needed), attach to users and tag roles, grant SELECT on columns."""
    LOGGER.info("In redshiftDataPermissions.grant_redshift_data_permissions, event: %s", event)
    report = {"success": [], "error": []}
    users = event.get("Users", [])
    if not users:
        event["report"] = report
        return event
    data_filter_name = event["DataFilterName"]
    domain = event["Domain"]
    dataset_name = event["DatasetName"]
    table_name = "%s.%s" % (domain, dataset_name)
    dp = event.get("DataPermissions", {})
    rows_expr = (dp.get("Rows") or {}).get("Expression") or "true"
    if (dp.get("Rows") or {}).get("Condition", "").lower() == "all":
        rows_expr = "true"
    cols_cfg = dp.get("Columns") or {}
    col_condition = cols_cfg.get("Condition", "all").lower()
    col_expression = cols_cfg.get("Expression") or []
    dataset_item = dynamodbUtil.get_item_with_key(dynamodb_resource.Table(DATASET_TABLE), {"DatasetId": event["DatasetId"]}, audit_log_config)
    all_cols = [c["name"] for c in (dataset_item.get("DatasetSchema") or [])]
    if col_condition == "all":
        grant_cols = all_cols
    elif col_condition == "include":
        grant_cols = col_expression
    else:
        grant_cols = [c for c in all_cols if c not in col_expression]
    policy_name = redshiftUtil.get_redshift_rls_policy_name(domain, dataset_name, data_filter_name.replace("%s_%s_" % (domain, dataset_name), "").strip("_") or data_filter_name)
    schema_cols = dataset_item.get("DatasetSchema") or []
    with_columns = [{"name": c["name"], "type": c.get("type", "varchar")} for c in schema_cols] if rows_expr != "true" else None
    conn = None
    try:
        conn = get_redshift_conn()
        redshiftUtil.enable_rls_on_table(table_name, conn)
        try:
            redshiftUtil.create_rls_policy(policy_name, rows_expr, conn, with_columns=with_columns)
        except Exception as create_ex:
            if "already exists" not in str(create_ex).lower():
                raise create_ex
        for user_id in users:
            try:
                user_item = dynamodbUtil.get_item_with_key(dynamodb_resource.Table(USER_TABLE), {"UserId": user_id}, audit_log_config)
                rs_username = (user_item or {}).get("UserName") or ("u_%s" % user_id)
                redshiftUtil.attach_rls_policy_to_user(policy_name, table_name, rs_username, conn)
                if grant_cols and col_condition != "all":
                    redshiftUtil.revoke_table_select_redshift(table_name, rs_username, conn, is_role=False)
                    redshiftUtil.grant_select_columns_redshift(table_name, grant_cols, rs_username, conn, is_role=False)
                report["success"].append(user_id)
            except Exception as uex:
                LOGGER.error("In redshiftDataPermissions.grant_redshift_data_permissions, user %s: %s", user_id, uex)
                report["error"].append(user_id)
        for tag_id in event.get("DataPermissions", {}).get("AuthorizedTags", event.get("AuthorizedTags", [])):
            tag_key = tag_id.split("#")[0]
            tag_value = tag_id.split("#")[-1]
            if tag_key == "user":
                continue
            role_name = redshiftUtil.get_tag_redshift_role_name(tag_key, tag_value)
            try:
                redshiftUtil.attach_rls_policy_to_role(policy_name, table_name, role_name, conn)
                if grant_cols and col_condition != "all":
                    redshiftUtil.revoke_table_select_redshift(table_name, role_name, conn, is_role=True)
                    redshiftUtil.grant_select_columns_redshift(table_name, grant_cols, role_name, conn, is_role=True)
                report["success"].append("role:%s" % role_name)
            except Exception as rex:
                if "does not exist" not in str(rex).lower():
                    LOGGER.error("In redshiftDataPermissions.grant_redshift_data_permissions, role %s: %s", role_name, rex)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
    event["report"] = report
    return event


def revoke_redshift_data_permissions(event, dynamodb_resource, audit_log_config):
    """Detach RLS policy from users/roles and revoke column SELECT."""
    LOGGER.info("In redshiftDataPermissions.revoke_redshift_data_permissions, event: %s", event)
    report = {"success": [], "error": []}
    users = event.get("Users", [])
    data_filter_name = event["DataFilterName"]
    domain = event["Domain"]
    dataset_name = event["DatasetName"]
    table_name = "%s.%s" % (domain, dataset_name)
    dp = event.get("DataPermissions", {})
    cols_cfg = dp.get("Columns") or {}
    col_condition = cols_cfg.get("Condition", "all").lower()
    col_expression = cols_cfg.get("Expression") or []
    dataset_item = dynamodbUtil.get_item_with_key(dynamodb_resource.Table(DATASET_TABLE), {"DatasetId": event["DatasetId"]}, audit_log_config)
    all_cols = [c["name"] for c in (dataset_item.get("DatasetSchema") or [])]
    if col_condition == "all":
        revoke_cols = all_cols
    elif col_condition == "include":
        revoke_cols = col_expression
    else:
        revoke_cols = [c for c in all_cols if c not in col_expression]
    policy_name = redshiftUtil.get_redshift_rls_policy_name(domain, dataset_name, data_filter_name.replace("%s_%s_" % (domain, dataset_name), "").strip("_") or data_filter_name)
    conn = None
    try:
        conn = get_redshift_conn()
        for user_id in users:
            try:
                user_item = dynamodbUtil.get_item_with_key(dynamodb_resource.Table(USER_TABLE), {"UserId": user_id}, audit_log_config)
                rs_username = (user_item or {}).get("UserName") or ("u_%s" % user_id)
                redshiftUtil.detach_rls_policy_from_user(policy_name, table_name, rs_username, conn)
                if revoke_cols and col_condition != "all":
                    redshiftUtil.revoke_select_columns_redshift(table_name, revoke_cols, rs_username, conn, is_role=False)
                    redshiftUtil.grant_select_columns_redshift(table_name, all_cols, rs_username, conn, is_role=False)
                report["success"].append(user_id)
            except Exception as uex:
                LOGGER.error("In redshiftDataPermissions.revoke_redshift_data_permissions, user %s: %s", user_id, uex)
                report["error"].append(user_id)
        for tag_id in event.get("DataPermissions", {}).get("AuthorizedTags", event.get("AuthorizedTags", [])):
            tag_key = tag_id.split("#")[0]
            tag_value = tag_id.split("#")[-1]
            if tag_key == "user":
                continue
            role_name = redshiftUtil.get_tag_redshift_role_name(tag_key, tag_value)
            try:
                redshiftUtil.detach_rls_policy_from_role(policy_name, table_name, role_name, conn)
                if revoke_cols and col_condition != "all":
                    redshiftUtil.revoke_select_columns_redshift(table_name, revoke_cols, role_name, conn, is_role=True)
                    redshiftUtil.grant_select_columns_redshift(table_name, all_cols, role_name, conn, is_role=True)
                report["success"].append("role:%s" % role_name)
            except Exception as rex:
                LOGGER.info("In redshiftDataPermissions.revoke_redshift_data_permissions, role %s: %s", role_name, rex)
        if event.get("delete_filter"):
            redshiftUtil.drop_rls_policy(policy_name, conn, cascade=True)
            key = {"Name": data_filter_name, "DatasetId": event["DatasetId"]}
            dynamodbUtil.delete_item_by_key(dynamodb_resource.Table(DATA_FILTER_TABLE), key, audit_log_config)
            report["success"].append("Deleted filter: %s" % data_filter_name)
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
    event["report"] = report
    return event


# pylint: disable=C0415,W0621,W0603
@heartbeatUtil.heartbeat_handler
def lambda_handler(event, context):
    """Dispatch by Operation: prepare, grant_permission, revoke_permission."""
    event = commonUtil.RedactAuthTokensClass(event)
    audit_log_config = {
        "region": AWS_REGION,
        "environment": os.environ.get("environment", ""),
        "log_payload": {
            "User": event.get("UserId", "N/A"),
            "FunctionName": context.function_name,
        },
    }
    try:
        dynamodb_resource = boto3.resource("dynamodb", AWS_REGION)
        if event.get("Operation") == "prepare":
            return prepare_redshift_data_permissions_metadata(event, dynamodb_resource, audit_log_config)
        if event.get("Operation") == "grant_permission":
            return grant_redshift_data_permissions(event, dynamodb_resource, audit_log_config)
        if event.get("Operation") == "revoke_permission":
            return revoke_redshift_data_permissions(event, dynamodb_resource, audit_log_config)
        LOGGER.error("In redshiftDataPermissions.lambda_handler, unknown Operation: %s", event.get("Operation"))
        raise errorUtil.GenericFailureException(EVENT_INFO, {"Message": "Unknown operation"})
    except Exception as ex:
        LOGGER.error("In redshiftDataPermissions.lambda_handler, %s", ex)
        event["LambdaException"] = str(ex)
        raise
