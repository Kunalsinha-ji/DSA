"""
###########################################################################################################
# File: authUtil.py
# Location: /cloudwick-datalake/amorphic-common-modules/infrastructure/auth-util/authUtil.py
#
# This file contains all functions related to handling of Access Control v2 actions.
#
# The Access Control Resources Table sits at the core of this functionality and is structured as follows:
#   Partition Key: ResourceId -> UUID representing the Resource ID
#   Sort Key: TagAccessKey -> <resource_type>#<tag_key>#<tag_value>#<access_type>
#                         Separator used is #, since it's ASCII value is lower than all alphanumeric characters.
#                         For representing individual user access: tag_key = user, tag_value = user_id.
#
# Modification History:
# ====================================================================
# Date                 Who                       Description
# ==========      =================     ==============================
#
# Aug 22 2024      Adithya Vimalan              Initial Commit
#
###########################################################################################################
"""
import functools
import os
import sys
from typing import Optional
import time
import re
from copy import deepcopy
from functools import wraps
import inspect
from collections import defaultdict
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed
import boto3
from boto3.dynamodb.conditions import Key, Attr

from loggingUtil import LOGGER
# from cacheUtil import MAX_CACHE_SIZE
import commonUtil
import dynamodbUtil
import errorUtil
import redshiftUtil
import redshiftDataUtil
import dwhQueryUtil
# Adding pylint disable at file level to avoid -> Instance of 'OWNER/EDITOR/READONLY' has no 'label' member (no-member)
# pylint: disable=no-member

EVENT_INFO = errorUtil.EVENT_INFO

try:
    if "AWS_LAMBDA_FUNCTION_NAME" in os.environ:
        # Utils file invoked from a Lambda Function
        AWS_REGION = os.environ["awsRegion"]
        AWS_PARTITION = os.environ["awsPartition"]
        ACCOUNT_ID = os.environ["accountId"]
        MULTI_TENANCY = os.environ["enableMultiTenancy"]
        ENABLE_HCLS = os.environ["enableHcls"]
        ENABLED_HCLS_LIST = os.environ["enabledHclsList"]
        PROJECT_SHORT_NAME = os.environ["projectShortName"]
        ENVIRONMENT = os.environ["environment"]
        ENABLE_AI_SERVICES = os.environ.get("enableAIServices", "no")
        # PROJECT_NAME = os.environ['projectName']

    else:
        # Utils file invoked from a Glue Job
        from awsglue.utils import getResolvedOptions

        glue_job_args = getResolvedOptions(
            sys.argv, ["projectShortName", "awsRegion", "awsPartition", "accountId", "enableMultiTenancy", "enableFips", "enableHcls", "enabledHclsList", "enableAIServices"]
        )
        PROJECT_SHORT_NAME = glue_job_args["projectShortName"]
        AWS_REGION = glue_job_args["awsRegion"]
        AWS_PARTITION = glue_job_args["awsPartition"]
        ACCOUNT_ID = glue_job_args["accountId"]
        MULTI_TENANCY = glue_job_args["enableMultiTenancy"]
        ENABLE_HCLS = glue_job_args["enableHcls"]
        ENABLED_HCLS_LIST = glue_job_args["enabledHclsList"]
        ENABLE_AI_SERVICES = glue_job_args.get("enableAIServices", "no")
        # For glue jobs, set the below environment variable for the boto3 SDK to use FIPS, if enabled
        os.environ["AWS_USE_FIPS_ENDPOINT"] = glue_job_args["enableFips"]

    # Access Control Related Tables
    ACL_TAGS_TABLE = dynamodbUtil.ACL_TAGS_TABLE
    ACL_RESOURCES_TABLE = dynamodbUtil.ACL_RESOURCES_TABLE
    ACL_RESOURCES_TABLE_RESOURCETYPE_INDEX = dynamodbUtil.ACL_RESOURCES_TABLE_RESOURCETYPE_INDEX
    USER_TABLE = dynamodbUtil.USER_TABLE
    DOMAINS_TABLE = dynamodbUtil.DOMAIN_TABLE
    DATASET_TABLE = dynamodbUtil.DATASET_TABLE
    DATA_FILTER_TABLE = dynamodbUtil.DATA_FILTER_TABLE
    DASHBOARD_INDEX_NAME = dynamodbUtil.DASHBOARD_INDEX_NAME
    JOBS_INDEX_NAME = dynamodbUtil.JOB_NAME_INDEX
    ML_MODELS_NAME_GSI = dynamodbUtil.ML_MODELS_NAME_GSI
    JOB_SHARED_LIB_TABLE_GSI = dynamodbUtil.JOB_SHARED_LIB_TABLE_GSI
    # DATA_QUALITY_CHECKS_INDEX = dynamodbUtil.DATA_QUALITY_CHECKS_INDEX
    DATA_PIPELINES_TABLE_DATA_PIPELINE_NAME_INDEX = dynamodbUtil.DATA_PIPELINES_TABLE_DATA_PIPELINE_NAME_INDEX
    DATASOURCES_INDEX_NAME = dynamodbUtil.DATASOURCES_TABLE_DATASOURCE_NAME_INDEX
    DATA_QUALITY_CHECKS_TABLE = dynamodbUtil.DATA_QUALITY_CHECKS_TABLE
    DATASOURCE_FLOWS_TABLE = dynamodbUtil.DATASOURCE_FLOWS_TABLE
    DATALAB_LIFECYCLE_CONFIGURATION_NAME_INDEX = dynamodbUtil.DATALAB_LIFECYCLE_CONFIGURATION_NAME_INDEX
    QS_VERTICAL_NAME = commonUtil.QS_VERTICAL_NAME
    VERTICALS_TABLE = dynamodbUtil.VERTICALS_TABLE

    DATASET_BATCH_SIZE = 100

    DYNAMODB_RES = boto3.resource("dynamodb", AWS_REGION)

    ### Resource related metadata map of ALL the resources in Amorphic.
    ### Total 25 with Glossaries, Datalabs and Datalab LCC's
    ### Please follow the order and add at the end and before the HCLS if condition
    ###  Editing any resource here must reflect across the sytem
    RESOURCE_DETAILS_MAP = {
        "datasets": {
            "ResourceId": "DatasetId",
            "ResourceType": "Dataset",
            "ResourceTable": dynamodbUtil.DATASET_TABLE,
            "ResourceNameKey": "DatasetName",
        },
        "dashboards": {
            "ResourceId": "DashboardId",
            "ResourceType": "Dashboard",
            "ResourceTable": dynamodbUtil.DASHBOARD_TABLE,
            "ResourceNameKey": "DashboardName",
            "ResourceNameIndexGroupsResourceTable": DASHBOARD_INDEX_NAME,
        },
        "jobs": {
            "ResourceId": "Id",
            "ResourceType": "Job",
            "ResourceTable": dynamodbUtil.JOBS_TABLE,
            "ResourceNameKey": "JobName",
            "ResourceTypeKey": "ETLJobType",
            "ResourceNameIndexGroupsResourceTable": JOBS_INDEX_NAME,
        },
        "schedules": {
            "ResourceId": "ScheduleId",
            "ResourceType": "Schedule",
            "ResourceTable": dynamodbUtil.SCHEDULES_TARGET_MAPPING_TABLE,
            "ResourceNameKey": "JobName",
            "ResourceTypeKey": "JobType",
        },
        "models": {
            "ResourceId": "ModelId",
            "ResourceType": "MLModel",
            "ResourceTable": dynamodbUtil.MODELS_TABLE,
            "ResourceNameKey": "ModelName",
            "ResourceNameIndexGroupsResourceTable": ML_MODELS_NAME_GSI,
        },
        "jobslibs": {
            "ResourceId": "LibraryId",
            "ResourceType": "JobLib",
            "ResourceTable": dynamodbUtil.SHARED_LIBS_TABLE,
            "ResourceNameKey": "LibraryName",
            "ResourceNameIndexGroupsResourceTable": JOB_SHARED_LIB_TABLE_GSI,
        },
        # "data-quality-checks": {
        #     "ResourceId": "DataQualityCheckId",
        #     "ResourceType": "DataQualityCheck",
        #     "ResourceTable": dynamodbUtil.DATA_QUALITY_CHECKS_TABLE,
        #     "ResourceNameKey": "DataQualityCheckName",
        #     "ResourceNameIndexGroupsResourceTable": DATA_QUALITY_CHECKS_INDEX,
        # },
        "data-pipelines": {
            "ResourceId": "DataPipelineId",
            "ResourceType": "DataPipeline",
            "ResourceTable": dynamodbUtil.DATA_PIPELINES_TABLE,
            "ResourceNameKey": "DataPipelineName",
            "ResourceNameIndexGroupsResourceTable": DATA_PIPELINES_TABLE_DATA_PIPELINE_NAME_INDEX,
        },
        "datasources": {
            "ResourceId": "DatasourceId",
            "ResourceType": "Datasource",
            "ResourceTable": dynamodbUtil.DATASOURCES_TABLE,
            "ResourceNameKey": "DatasourceName",
            "ResourceNameIndexGroupsResourceTable": DATASOURCES_INDEX_NAME,
        },
        "domains": {
            "ResourceId": "DomainName",
            "ResourceType": "Domain",
            "ResourceTable": dynamodbUtil.DOMAIN_TABLE,
            "ResourceNameKey": "DomainName",
        },
        "tenants": {
            "ResourceId": "TenantName",
            "ResourceType": "Tenant",
            "ResourceTable": dynamodbUtil.TENANT_TABLE,
            "ResourceNameKey": "TenantName",
        },
        "verticals": {
            "ResourceId": "VerticalId",
            "ResourceType": "Vertical",
            "ResourceTable": dynamodbUtil.VERTICALS_TABLE,
            "ResourceNameKey": "VerticalName",
        },
        "code-repositories": {
            "ResourceId": "RepositoryName",
            "ResourceType": "CodeRepository",
            "ResourceTable": dynamodbUtil.CODE_REPOSITORIES_TABLE,
            "ResourceNameKey": "RepositoryName",
        },
        "tags": {
            "ResourceId": "Tag",
            "ResourceType": "Tag",
            "ResourceTable": dynamodbUtil.ACL_TAGS_TABLE,
            "ResourceNameKey": "Tag",
        },
        "templates": {
            "ResourceId": "TemplateId",
            "ResourceType": "Template",
            "ResourceTable": dynamodbUtil.TEMPLATES_TABLE,
            "ResourceNameKey": "TemplateName",
        },
        "code-templates": {
            "ResourceId": "TemplateId",
            "ResourceType": "CodeTemplate",
            "ResourceTable": dynamodbUtil.CODE_TEMPLATES_TABLE,
            "ResourceNameKey": "TemplateName",
        },
        "datalabs": {
            "ResourceId": "DatalabId",
            "ResourceType": "Datalab",
            "ResourceTable": dynamodbUtil.DATALABS_TABLE,
            "ResourceNameKey": "DatalabName",
        },
        "datalabs-lifecycle-configurations": {
            "ResourceId": "LifecycleId",
            "ResourceType": "LifecycleConfiguration",
            "ResourceTable": dynamodbUtil.DATALAB_LIFECYCLE_CONFIG_TABLE,
            "ResourceNameKey": "LifecycleName",
            "ResourceNameIndexGroupsResourceTable": DATALAB_LIFECYCLE_CONFIGURATION_NAME_INDEX,
        },
        "glossaries": {
            "ResourceId": "GlossaryId",
            "ResourceType": "Glossary",
            "ResourceTable": dynamodbUtil.GLOSSARIES_TABLE,
            "ResourceNameKey": "GlossaryName",
        },
        "query-workbooks": {
            "ResourceId": "WorkbookId",
            "ResourceType": "NL2SQLWorkbook",
            "ResourceTable": dynamodbUtil.QUERY_WORKBOOKS_TABLE,
            "ResourceNameKey": "Title",
        },
        "service-users": {
            "ResourceId": "UserId",
            "ResourceType": "ServiceUser",
            "ResourceTable": dynamodbUtil.USER_TABLE,
            "ResourceNameKey": "Name",
        }
    }
    if ENABLE_HCLS == "yes":
        RESOURCE_DETAILS_MAP.update(
            {
                "hcls": {
                    "ResourceId": "StoreId",
                    "ResourceType": "HclsStore",
                    "ResourceTable": dynamodbUtil.HCLS_STORES_TABLE,
                    "ResourceNameKey": "StoreName",
                }
            }
        )
        if "aws_omics" in ENABLED_HCLS_LIST:
            RESOURCE_DETAILS_MAP.update(
                {
                    "hcls-omics-workflows": {
                        "ResourceId": "HclsWorkflowId",
                        "ResourceType": "HclsWorkflow",
                        "ResourceTable": dynamodbUtil.HCLS_WORKFLOWS_TABLE,
                        "ResourceNameKey": "WorkflowName",
                    }
                }
            )

    if ENABLE_AI_SERVICES == "yes":
        RESOURCE_DETAILS_MAP.update({
            "knowledgebases": {
                "ResourceId": "KnowledgebaseId",
                "ResourceType": "knowledgebases",
                "ResourceTable": dynamodbUtil.KNOWLEDGE_BASE_TABLE,
                "ResourceNameKey": "KnowledgebaseName",
            },
            "agents": {
                "ResourceId": "AgentId",
                "ResourceType": "Agent",
                "ResourceTable": dynamodbUtil.AGENTS_TABLE,
                "ResourceNameKey": "AgentName",
            },
            "guard-rails": {
                "ResourceId": "GuardRailId",
                "ResourceType": "guard-rails",
                "ResourceTable": dynamodbUtil.GUARD_RAILS_TABLE,
                "ResourceNameKey": "GuardRailName",
            },
            "ai-chats": {
                "ResourceId": "ChatId",
                "ResourceType": "AIChat",
                "ResourceTable": dynamodbUtil.AI_CHATS_TABLE,
                "ResourceNameKey": "Title",
            },
            "ai-notes": {
                "ResourceId": "NoteId",
                "ResourceType": "AINote",
                "ResourceTable": dynamodbUtil.AI_NOTES_TABLE,
                "ResourceNameKey": "Title",
            },
            "projects": {
                "ResourceId": "ProjectId",
                "ResourceType": "Project",
                "ResourceTable": dynamodbUtil.AI_PROJECTS_TABLE,
                "ResourceNameKey": "ProjectName",
            }
        })
    SCHEDULE_JOB_TYPE_ACL_RESOURCE_MAP = {
        'etl': 'jobs',
        'jdbc-cdc': 'datasources',
        'jdbc-full-load': 'datasources',
        'arcgis-full-load': 'datasources',
        'arcgis-incremental': 'datasources',
        'ingestion': 'datasets',
        'data-quality-checks': 'datasets',
        'hcls-fhir-data-conversion': 'datasets',
        'export-to-s3': 'datasets',
        'data-pipelines': 'data-pipelines',
        'hcls-store': 'hcls'
    }

except Exception as exc:
    LOGGER.error("Failed to load env-variables in authUtil with exception %s", exc)
    sys.exit()


class AccessType(Enum):
    """
    Enum representing different access types.
    """

    OWNER = "owner", 3
    EDITOR = "editor", 2
    READONLY = "read-only", 1
    NONE = None, 0  # for revoking access

    def __init__(self, label, priority):
        self.label = label
        self.priority = priority

    # Changed 'str | None' to 'Optional[str] = None' as some of the Amorphic backend glue jobs have 3.9 and 3.7
    # where as this | convention is supported from Python 3.10 onwards
    @classmethod
    def from_label(cls, label: Optional[str] = None):
        """Maps a label to the corresponding AccessType. Returns AccessType.NONE for invalid or None labels."""
        if label is None:
            return cls.NONE
        return next((access_type for access_type in cls if access_type.label == label), cls.NONE)


def validate_resource_type(func):
    """Decorator for validating the 'resource_type' argument of the function against RESOURCE_DETAILS_MAP."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get the argument names and their positions in the function signature
        signature = inspect.signature(func)
        bound_args = signature.bind_partial(*args, **kwargs)
        bound_args.apply_defaults()  # Apply default values where applicable

        # Retrieve the 'resource_type' argument from either args or kwargs
        resource_type = bound_args.arguments.get("resource_type")

        if resource_type is None:
            raise ValueError(f"'resource_type' argument is missing from the function '{func.__name__}'.")

        if resource_type not in RESOURCE_DETAILS_MAP:
            raise ValueError(f"Invalid resource_type: '{resource_type}'. Must be one of {list(RESOURCE_DETAILS_MAP.keys())}.")

        # Proceed with the original function if validation passed
        return func(*args, **kwargs)

    return wrapper


def get_resource_type_from_resource_table_name(resource_table_name):
    """
    Returns the resource type for a given resource table name
    Args:
        resource_table_name (str): The name of the resource table
    Returns:
        str: The resource type corresponding to the resource table name
    """

    for resource_type, details in RESOURCE_DETAILS_MAP.items():
        if details.get("ResourceTable") == resource_table_name:
            return resource_type
    return None  # If no matching ResourceTable is found


def validate_access_label(access_label: Optional[str] = None) -> AccessType:
    """
    Validates the access label and returns the corresponding AccessType enum value.
    Raises ValueError if the access label is invalid.

    Args:
        access_label (Optional[str] = None): The access label to validate. It should be None when revoking access.
    Returns:
        AccessType: The corresponding AccessType enum value.
    Raises:
        ValueError: If the access label is invalid.
    """
    access_type = AccessType.from_label(access_label)
    if access_type is AccessType.NONE and access_label is not None:
        raise ValueError(f"Invalid access label: {access_label}")
    return access_type


def get_access_priority(input_string: str) -> int:
    """
    Helper function to get the access priority for sorting.
    Args:
        input_string (str): The input string in the format: <resource_type>#<tag_key>#<tag_value>#<access_type>

    Returns:
        int: The priority level of the access type.
    """
    access_type_label = input_string.split("#")[-1] if input_string else None
    return AccessType.from_label(access_type_label).priority


def can_modify_access(current_access: AccessType, requested_access: AccessType) -> bool:
    """
    Helper function to check if the user's current access level is enough to grant/revoke the requested access level.
    Args:
        current_access (AccessType): The current access type.
        requested_access (AccessType): The requested access type.

    Returns:
        bool: True if the user can modify the access, False otherwise.
    """
    return (current_access.priority > AccessType.READONLY.priority) and (requested_access.priority <= current_access.priority)

def get_access_type_on_vertical(qs_new_user, audit_log_config):
    """
    This method fethces access type of a user on bi vertical
    :param qs_new_user  --> string (User-id) for whom access type is to be fetched
    :param audit_log_config  --> dict
    :return user_access  --> string (access type)
    """
    LOGGER.info("In authUtil.get_access_type_on_vertical, fetching access type on vertical for user - %s", qs_new_user)
    # Check if new user chosen for resource transfer has owner/editor acces
    verticals_with_access_type = retrieve_user_accessible_resources(DYNAMODB_RES, "verticals", qs_new_user, audit_log_config)
    qs_vertical_id = dynamodbUtil.scan_with_pagination(DYNAMODB_RES.Table(RESOURCE_DETAILS_MAP.get("verticals", {}).get("ResourceTable", "")), audit_log_config, Attr("VerticalType").eq(QS_VERTICAL_NAME),"VerticalId")[0].get("VerticalId")
    LOGGER.info("In authUtil.get_access_type_on_vertical, quicksight vertical id - %s", qs_vertical_id)
    user_access = verticals_with_access_type.get(qs_vertical_id)
    LOGGER.info("In authUtil.get_access_type_on_vertical, user access on quicksight vertical - %s", user_access)
    return user_access

def check_access_level(user_id: str, user_permission: str, required_access: AccessType) -> None:
    """
    Helper function to check if the user has the required access level.
    Args:
        user_id (str): The user's ID.
        user_permission (str): The user's access level.
        required_access (AccessType): The minimum required access level for this action

    Returns:
        None
    """
    # Check if Super Admin mode is active - skip access level validation
    is_super_admin = commonUtil.get_super_admin_context()
    if is_super_admin:
        LOGGER.info("In authUtil.check_access_level, Super Admin mode active for user %s, skipping access level validation", user_id)
        return

    user_permission_object = AccessType.from_label(user_permission)

    if user_permission_object.priority < required_access.priority:
        LOGGER.error("User: %s requires at least %s access to perform this action", user_id, required_access.label)
        errorUtil.raise_exception(
            EVENT_INFO,
            "UU",
            "AUTH-1012",
            f"User: {user_id} requires at least {required_access.label} access on the resource to perform this action.",
        )
    LOGGER.info("In authUtil.check_access_level, User: %s has required access level", user_id)


@validate_resource_type
def retrieve_users_attached_to_resource(dynamodb_resource, resource_type: str, resource_id: str, requestor_user_id: str, audit_log_config: dict, ignore_dla: bool = True) -> list:
    """
    Returns a list of all users attached to a resource (directly attached + indirectly attached through tags)
    Args:
        dynamodb_resource: boto3 dynamodb resource
        resource_type (str): Type of resource(eg: dataset, job, etc)
        resource_id (str): UUID of the resource
        requestor_user_id (str): User Id
        audit_log_config (dict): Configuration for audit logging

    Returns:
        List
    """

    LOGGER.info("In authUtil.retrieve_users_attached_to_resource, Retrieving users who have access to resource %s : %s by - %s", resource_type, resource_id, requestor_user_id)
    acl_response = dynamodbUtil.get_items_by_query(
        dynamodb_resource.Table(ACL_RESOURCES_TABLE),
        Key("ResourceId").eq(resource_id) & Key("TagAccessKey").begins_with(f"{resource_type}#"),
        "TagAccessKey",
        audit_log_config,
    )
    users_list_with_access_type = {"Owner": set(), "Editor": set(), "Read-only": set(), "UsersAttached": set()}
    # requested_by_system = requestor_user_id == commonUtil.SYSTEM_RUNNER_ID
    # requestor_access_type = None
    is_super_admin = commonUtil.get_super_admin_context()
    for item in acl_response:
        users = []
        if is_super_admin:
            users = [requestor_user_id]
        _, tag_key, tag_value, access_type = item["TagAccessKey"].split("#")
        if tag_key == "user":
            users = [tag_value]
            # if not requested_by_system and tag_value == requestor_user_id:
            #     requestor_access_type = access_type
        # Tags has access to this resource, so fetching users from the tag also
        else:
            tags_response = dynamodbUtil.get_items_by_query(
                dynamodb_resource.Table(ACL_RESOURCES_TABLE),
                Key("ResourceId").eq(f"{tag_key}#{tag_value}") & Key("TagAccessKey").begins_with("tags#user"),
                "TagAccessKey",
                audit_log_config,
            )
            for tag_users in tags_response:
                user_id = tag_users["TagAccessKey"].split("#")[-2]
                users.append(user_id)
        users_list_with_access_type[access_type.capitalize()].update(users)
        users_list_with_access_type["UsersAttached"].update(users)

    if resource_type == "datasets" and not ignore_dla:
        # fetch dataset domain
        dataset_detail = dynamodbUtil.get_item_with_key(dynamodb_resource.Table(DATASET_TABLE),
            {'DatasetId': resource_id}, audit_log_config)
        dataset_domain = dataset_detail['Domain']
        # check tags and users attached to that domain
        tags_with_domain_access = list_authorized_entities_for_resource(
            dynamodb_resource, "domains", dataset_domain, commonUtil.SYSTEM_RUNNER_ID, audit_log_config, True
        )
        for access_type, tags_list in tags_with_domain_access.items():
            for tag_item in tags_list:
                users = []
                if is_super_admin:
                    users = [requestor_user_id]
                if tag_item.get('IsDatasetLevelAccessProvided', False):
                    if tag_item['TagKey'] == 'user':
                        users = [tag_item['TagValue']]
                    else:
                        users = retrieve_users_attached_to_resource(dynamodb_resource, "tags", f"{tag_item['TagKey']}#{tag_item['TagValue']}", requestor_user_id, audit_log_config).get("UsersAttached", [])
                    users_list_with_access_type[access_type].update(users)
                    users_list_with_access_type["UsersAttached"].update(users)

    # if not requested_by_system and AccessType.from_label(requestor_access_type).priority < AccessType.EDITOR.priority:
    #     LOGGER.error("User: %s requires at least %s access on the tag to perform this action", requestor_user_id, AccessType.EDITOR.label)
    #     errorUtil.raise_exception(
    #         EVENT_INFO,
    #         "UU",
    #         "AUTH-1012",
    #         f"User: {requestor_user_id} requires at least {AccessType.EDITOR.label} access on the tag to perform this action.",
    #     )

    # Convert sets back to lists
    users_list_with_access_type = {k: list(v) for k, v in users_list_with_access_type.items()}
    LOGGER.info("In authUtil.retrieve_users_attached_to_resource, Users list with access type %s", users_list_with_access_type)
    return users_list_with_access_type


def check_user_access_on_tag(tag_key: str, tag_value: str, user_id: str, dynamodb_resource, audit_log_config: dict, user_share=False) -> dict:
    """
    This method checks if the user has access to a tag or the pseudo tag representing individual user access
    and returns the tag details.
    Args:
        tag_key (str): tag key
        tag_value (str): tag value
        user_id (str): user Id
        dynamodb_resource: boto3 dynamodb resource
        audit_log_config (dict): Configuration for audit logging
        user_share (bool): Flag to indicate if the user is granting/revoking access on a resource to another user

    Returns:
        dict: Tag details
    """
    LOGGER.info(
        "In authUtil.check_user_access_on_tag, user_id is %s, tag_key is %s, tag_value is %s",
        user_id,
        tag_key,
        tag_value,
    )
    super_admin = commonUtil.get_super_admin_context()
    if tag_key == "user":
        if (tag_value == user_id) or user_share or super_admin:
            # Generating a pseudo tag to represent user's default tag
            pseudo_tag_item = {
                "Tag": f"user#{tag_value}",
                "UsersAttached": [tag_value],
            }
            return pseudo_tag_item
        else:
            LOGGER.error(
                "In authUtil.user_has_access_to_tags, User %s cannot have access on another user's default tag - %s : %s",
                user_id,
                tag_key,
                tag_value,
            )
            errorUtil.raise_exception(EVENT_INFO, "II", "TAG-1004", None, tag_key, tag_value)

    tags_item = dynamodbUtil.get_item_with_key(dynamodb_resource.Table(ACL_TAGS_TABLE), {"Tag": f"{tag_key}#{tag_value}"}, audit_log_config)

    if not tags_item:
        LOGGER.error("In authUtil.user_has_access_to_tags, Tag %s : %s does not exist", tag_key, tag_value)
        errorUtil.raise_exception(EVENT_INFO, "II", "IPV-1002", None, "Tag", f"{tag_key} : {tag_value}")

    resource_id = f"{tag_key}#{tag_value}"
    users_attached = retrieve_users_attached_to_resource(dynamodb_resource, "tags", resource_id, user_id, audit_log_config)
    tags_item["UsersAttached"] = users_attached.get("UsersAttached")
    return tags_item


@validate_resource_type
def retrieve_resources_attached_to_tag(resource_type: str, tag_key: str, tag_value: str, dynamodb_resource, audit_log_config: dict, addl_info=False) -> list:
    """
    Returns a list of resources of a particular resource type attached to a tag
    Args:
        resource_type (str): resource type
        tag_key (str): tag name
        tag_value (str): tag value
        dynamodb_resource: boto3 dynamodb resource
        audit_log_config (dict): Configuration for audit logging

    Returns:
        List: List of resources attached to the tag along with their access types
    """
    LOGGER.info("In authUtil.retrieve_resources_attached_to_tag, Retrieving %s resources attached to tag %s : %s", resource_type, tag_key, tag_value)
    starting_sort_key = f"{resource_type}#{tag_key}#{tag_value}#{AccessType.EDITOR.label}"
    ending_sort_key = f"{resource_type}#{tag_key}#{tag_value}#{AccessType.READONLY.label}"
    key_condition_expression = Key("ResourceType").eq(resource_type) & Key("TagAccessKey").between(starting_sort_key, ending_sort_key)
    acl_response = dynamodbUtil.get_items_by_query_index(
        dynamodb_resource.Table(ACL_RESOURCES_TABLE),
        ACL_RESOURCES_TABLE_RESOURCETYPE_INDEX,
        audit_log_config,
        key_condition_expression,
    )
    if not addl_info:
        resource_ids_response = [{item["ResourceId"]: item["TagAccessKey"].split("#")[-1]} for item in acl_response]
    else:
        resource_ids_response = defaultdict(lambda: defaultdict(list))
        for each_resource in acl_response:
            resource_type = each_resource["ResourceType"]
            access_type = each_resource["TagAccessKey"].split("#")[-1]
            resource_id = each_resource["ResourceId"]
            resource_name = each_resource["ResourceName"]

            # Get the corresponding ResourceId and ResourceNameKey from RESOURCE_DETAILS_MAP
            if resource_type in RESOURCE_DETAILS_MAP:
                resource_details = RESOURCE_DETAILS_MAP[resource_type]
                # Format the result
                resource_ids_response[resource_type][access_type].append(
                    {resource_details["ResourceId"]: resource_id, resource_details["ResourceNameKey"]: resource_name}
                )
        resource_ids_response = dict(resource_ids_response)

    return resource_ids_response


def retrieve_user_accessible_tags(dynamodb_resource, user_id: str, audit_log_config: dict) -> list:
    """
    Returns a list of all user accessible tags

    Args:
        dynamodb_resource: boto3 dynamodb resource
        user_id (str): user Id
        audit_log_config (dict): Configuration for audit logging

    Returns:
        List
    """
    LOGGER.info("In authUtil.retrieve_user_accessible_tags, Retrieving tags accessible to user %s", user_id)
    user_table = dynamodb_resource.Table(USER_TABLE)
    user_item = dynamodbUtil.get_item_with_key(user_table, {"UserId": user_id}, audit_log_config)
    if not user_item:
        errorUtil.raise_exception(EVENT_INFO, "II", "GE-1064", None, user_id)


    tags_list = []
    starting_sort_key = f"tags#user#{user_id}#{AccessType.EDITOR.label}"
    ending_sort_key = f"tags#user#{user_id}#{AccessType.READONLY.label}"

    key_condition_expression = Key("ResourceType").eq("tags") & Key("TagAccessKey").between(starting_sort_key, ending_sort_key)

    acl_response = dynamodbUtil.get_items_by_query_index(
        dynamodb_resource.Table(ACL_RESOURCES_TABLE),
        ACL_RESOURCES_TABLE_RESOURCETYPE_INDEX,
        audit_log_config,
        key_condition_expression,
    )
    if acl_response:
        tags_list = [each_resource["ResourceId"] for each_resource in acl_response]
    # Add the pseudo tag which represents individual user access
    tags_list.append(f"user#{user_id}")
    # Sort it to make this list suitable for DDB queries
    tags_list.sort()
    LOGGER.info("In authUtil.retrieve_user_accessible_tags, User: %s has following tags: %s", user_id, tags_list)
    return tags_list


def validate_fileleveltags(read_only_files, user_id, audit_log_config):
    """
     Validates that all file-level tags in the datasets are accessible to the user
    """
    tags_list = retrieve_user_accessible_tags(DYNAMODB_RES, user_id, audit_log_config)
    accessible_tags_set = set(tags_list)
    filelevel_tags_set = set()
    missing_fileleveltags_datasets = []
    for dataset in read_only_files:
        dataset_id = dataset["DatasetId"]
        file_level_tags = dataset.get("FileLevelTags", [])
        if not file_level_tags:
            missing_fileleveltags_datasets.append(dataset_id)
        for tag in file_level_tags:
            tag_key = tag.get("TagKey")
            tag_value = tag.get("TagValue")
            tag_combined = f"{tag_key}#{tag_value}"
            filelevel_tags_set.add(tag_combined)

    if missing_fileleveltags_datasets:
        ec_auth_1032 = errorUtil.get_error_object("AUTH-1031")
        ec_auth_1032["Message"] = (f"Missing FileLevelTags for the following datasets under ReadOnlyFileLevel access: {', '.join(missing_fileleveltags_datasets)}.")
        LOGGER.error("In authUtil.validate_fileleveltags, Datasets missing FileLevelTags: %s",missing_fileleveltags_datasets)
        raise errorUtil.InvalidInputException(EVENT_INFO, ec_auth_1032)

    missing_tags = filelevel_tags_set - accessible_tags_set

    if missing_tags:
        ec_auth_1031 = errorUtil.get_error_object("AUTH-1031")
        ec_auth_1031["Message"] = f"User {user_id} does not have access to the following tags: {', '.join(missing_tags)}"
        LOGGER.error("In authUtil.validate_fileleveltags, missing accessible tags for user %s: %s", user_id, missing_tags)
        raise errorUtil.InvalidInputException(EVENT_INFO, ec_auth_1031)

def _handle_schedule_resource_mapping(dynamodb_resource, schedule_id, user_id, audit_log_config):
    """
    Helper function to handle schedule resource mapping logic.
    Modifies resource_type and resource_id in place and may return early for datasets.

    Returns:
        tuple: (should_return, return_value, resource_type, resource_id)
        - should_return: True if function should return early
        - return_value: The value to return if should_return is True, None otherwise
        - resource_type: Updated resource type
        - resource_id: Updated resource id
    """
    LOGGER.info("In authUtil._handle_schedule_resource_mapping, entering the method with args schedule_id: %s, user_id: %s", schedule_id, user_id)
    schedule_item = dynamodbUtil.get_item_with_key(dynamodb_resource.Table(dynamodbUtil.SCHEDULES_TARGET_MAPPING_TABLE), {"ScheduleId": schedule_id}, audit_log_config)
    if not schedule_item:
        LOGGER.error("In authUtil._handle_schedule_resource_mapping, no %s found with id %s", "schedules", schedule_id)
        ec_ipv_1002 = errorUtil.get_error_object("IPV-1002")
        ec_ipv_1002['Message'] = ec_ipv_1002['Message'].format("schedulesId", schedule_id)
        raise errorUtil.InvalidInputException(EVENT_INFO, ec_ipv_1002)
    # fetch resource type and resource id
    resource_type = SCHEDULE_JOB_TYPE_ACL_RESOURCE_MAP.get(schedule_item.get('JobType', ''), '')
    LOGGER.info("In authUtil._handle_schedule_resource_mapping, resource_type is : %s", resource_type)
    resource_id = schedule_id
    if schedule_item.get('ScheduleType') == 'external-trigger':
        resource_id = schedule_item['Resource']
        resource_type = schedule_item['ResourceType']
        if resource_type == 'jobs':
            job_items = dynamodbUtil.get_items_by_query_index(
                table=dynamodb_resource.Table(dynamodbUtil.JOBS_TABLE),
                index_name=dynamodbUtil.JOB_NAME_INDEX,
                audit_log_config=audit_log_config,
                key_condition_expression=Key("JobName").eq(resource_id)
            )
            if job_items:
                job_id = job_items[0]['Id']
                resource_id = job_id
        elif resource_type == 'data-pipelines':
            data_pipeline_item = dynamodbUtil.get_item_with_key(
                dynamodb_resource.Table(dynamodbUtil.DATA_PIPELINES_TABLE),
                {'DataPipelineId': resource_id},
                audit_log_config
            )
            if not data_pipeline_item:
                LOGGER.error("In authUtil._handle_schedule_resource_mapping, Data pipeline not found with ID %s for external trigger schedule", resource_id)
                return (True, None, None, None)
            # resource_id is already the DataPipelineId, no need to change it
        else:
            LOGGER.error("In authUtil._handle_schedule_resource_mapping, Invalid resource type %s for external trigger schedule", resource_type)
            return (True, None, None, None)
    if resource_type == 'datasets':
        if schedule_item['JobType'] == 'data-quality-checks':
            # fetch dq check item and retrieve datasetId
            dq_check_id = schedule_item['Resource']
            dq_check_item = dynamodbUtil.get_item_with_key(
                DYNAMODB_RES.Table(DATA_QUALITY_CHECKS_TABLE),
                {'DataQualityCheckId': dq_check_id},
                audit_log_config
            )
            resource_id = dq_check_item['DatasetId']
        else:
            resource_id = schedule_item['Resource']
        return (True, _get_user_dataset_permission(dynamodb_resource, resource_id, user_id, audit_log_config), resource_type, resource_id)
    elif resource_type == 'jobs':
        # fetch job id
        job_items = dynamodbUtil.get_items_by_query_index(
            table=dynamodb_resource.Table(dynamodbUtil.JOBS_TABLE),
            index_name=dynamodbUtil.JOB_NAME_INDEX,
            audit_log_config=audit_log_config,
            key_condition_expression=Key("JobName").eq(schedule_item['Resource'])
        )
        if job_items:
            job_id = job_items[0]['Id']
            resource_id = job_id
    elif resource_type == 'datasources':
        if schedule_item['JobType'] in ['jdbc-cdc', 'jdbc-full-load', 'arcgis-full-load', 'arcgis-incremental']:
            dataflow_id = schedule_item['Resource']
            dataflow_item = dynamodbUtil.get_item_with_key(
                DYNAMODB_RES.Table(DATASOURCE_FLOWS_TABLE),
                {'DataflowId': dataflow_id},
                audit_log_config
            )
            resource_id = dataflow_item['DatasourceId']
    elif schedule_item['ScheduleType'] == 'event-trigger':
        resource_id = schedule_item['Resource']
        resource_type = schedule_item['ResourceType']
        if resource_type == 'datasets':
            return (True, _get_user_dataset_permission(dynamodb_resource, resource_id, user_id, audit_log_config), resource_type, resource_id)
    else:
        resource_id = schedule_item['Resource']

    return (False, None, resource_type, resource_id)

@validate_resource_type
def get_user_resource_tags_with_tagawsres_true(
    dynamodb_resource,
    resource_type: str,
    resource_id: str,
    user_id: str,
    audit_log_config: dict,
) -> str:
    """
    This method returns the tags on a resource if it has additional config of TagAwsResource=True
    Args:
        dynamodb_resource: boto3 dynamodb resource
        resource_type (str): Type of resource(eg: dataset, job, etc)
        resource_id (str): UUID of the resource
        user_id (str): user Id
        audit_log_config (dict): Configuration for audit logging
    Returns:
        str: Highest access type for the user on the resource
    """
    LOGGER.info("In authUtil.get_user_resource_tags_with_tagawsres_true, Retrieving tags with TagAwsResource=True for user %s on resource %s", user_id, resource_id)
    response_tags_list = []
    tags_list = retrieve_user_accessible_tags(dynamodb_resource, user_id, audit_log_config)

    starting_sort_key = f"{resource_type}#{tags_list[0]}#{AccessType.EDITOR.label}"
    ending_sort_key = f"{resource_type}#{tags_list[-1]}#{AccessType.READONLY.label}"

    acl_response = dynamodbUtil.get_items_by_query(
        dynamodb_resource.Table(ACL_RESOURCES_TABLE),
        Key("ResourceId").eq(resource_id) & Key("TagAccessKey").between(starting_sort_key, ending_sort_key),
        "TagAccessKey,AdditionalMetadata",
        audit_log_config,
    )

    if acl_response:
        # Filter out the items that do not belong to tags_list
        response_tags_list = [
            "#".join(item["TagAccessKey"].split("#")[1:4])
            for item in acl_response
            if "#".join(item["TagAccessKey"].split("#")[1:3]) in tags_list and item.get("AdditionalMetadata", {}).get("TagAwsResources", False) is True
        ]
        # Return the tags list in the format of tagkey#tagvalue#accesstype
        return response_tags_list


@validate_resource_type
def get_user_resource_permission(
    dynamodb_resource,
    resource_type: str,
    resource_id: str,
    user_id: str,
    audit_log_config: dict,
    dla_flag = True,
    domain_name = "",
) -> str:
    """
    This method returns the user's highest level of access given the resource id
    Args:
        dynamodb_resource: boto3 dynamodb resource
        resource_type (str): Type of resource(eg: dataset, job, etc)
        resource_id (str): UUID of the resource
        user_id (str): user Id
        audit_log_config (dict): Configuration for audit logging
    Returns:
        str: Highest access type for the user on the resource
    """
    LOGGER.info("In authUtil.get_user_resource_permission, Retrieving highest access for user %s on resource %s", user_id, resource_id)

    # Check if Super Admin mode is active - return owner access
    is_super_admin = commonUtil.get_super_admin_context()
    if is_super_admin:
        LOGGER.info("In authUtil.get_user_resource_permission, Super Admin mode active for user %s, returning owner access", user_id)
        return "owner"

    # Validate multi tenancy flag and add default tenant if applicable
    if MULTI_TENANCY == "yes" and resource_type == "tenants" and resource_id.lower() == PROJECT_SHORT_NAME.lower():
        highest_access = "owner"
        return highest_access

    # Handle composite asset IDs for tenants and domains (used in catalog AssetsTable)
    # AssetsTable uses composite IDs like "tenant::TenantName" or "domain::DomainName" to avoid overwriting
    # but ACL tables use the actual resource IDs, so we need to resolve them here
    if resource_type == "tenants" and resource_id.startswith("tenant::"):
        resource_id = resource_id.replace("tenant::", "", 1)
        LOGGER.info("In authUtil.get_user_resource_permission, Resolved tenant ID from composite: %s", resource_id)

    if resource_type == "domains" and resource_id.startswith("domain::"):
        resource_id = resource_id.replace("domain::", "", 1)
        LOGGER.info("In authUtil.get_user_resource_permission, Resolved domain ID from composite: %s", resource_id)

    if resource_type == 'schedules':
        should_return, return_value, resource_type, resource_id = _handle_schedule_resource_mapping(dynamodb_resource, resource_id, user_id, audit_log_config)
        if should_return:
            return return_value

    # Handle datasets separately using the dedicated dataset permission function (when DLA flag is enabled)
    if resource_type == "datasets" and dla_flag:
        LOGGER.info("In authUtil.get_user_resource_permission, the resource type is a dataset and needs to check dla")
        return _get_user_dataset_permission(dynamodb_resource, resource_id, user_id, audit_log_config, domain_name)

    # Handle other resource types (and datasets with dla_flag=False) with general ACL logic
    tags_list = retrieve_user_accessible_tags(dynamodb_resource, user_id, audit_log_config)
    highest_access = None

    starting_sort_key = f"{resource_type}#{tags_list[0]}#{AccessType.EDITOR.label}"
    ending_sort_key = f"{resource_type}#{tags_list[-1]}#{AccessType.READONLY.label}"

    acl_response = dynamodbUtil.get_items_by_query(
        dynamodb_resource.Table(ACL_RESOURCES_TABLE),
        Key("ResourceId").eq(resource_id) & Key("TagAccessKey").between(starting_sort_key, ending_sort_key),
        "TagAccessKey",
        audit_log_config,
    )

    if acl_response:
        # Filter out the items that do not belong to tags_list
        filtered_items = [item["TagAccessKey"].split("#")[-1] for item in acl_response if "#".join(item["TagAccessKey"].split("#")[1:3]) in tags_list]
        if filtered_items:
            # Get the highest access type
            highest_access = max(filtered_items, key=get_access_priority)

    else:
        LOGGER.error("In authUtil.get_user_resource_permission, no access found for user %s on resource %s", user_id, resource_id)

    # For non-dataset resources, return the calculated access
    LOGGER.info(
        "In authUtil.get_user_resource_permission, highest access for user %s on resource %s is %s",
        user_id,
        resource_id,
        resource_type,
        highest_access,
    )

    return highest_access

def authorize_user_datasets(dynamodb_resource, user_id: str, dataset_ids_dict: dict, audit_log_config: dict, **os_env_var_dict: dict) -> list:
    """
    Check whether the user has required access on the dataset
    Args:
        dynamodb_resource: boto3 dynamodb resource
        user_id (str): User Id
        dataset_ids_dict (dict): Dictionary of datasets with their access types
        Example:     {"Owner": [dataset_id1, dataset_id2, ....],
                    "Editor": [dataset_id1, dataset_id2, ....],
                    "Read-Only": [dataset_id1, dataset_id2, ....]}
        audit_log_config (dict): Configuration for audit logging

    Returns:
        list: List of dictionaries containing the dataset id, access type and status
    """
    LOGGER.info("In authUtil.authorize_user_datasets, starting the method")
    dataset_access_list = []
    dataset_access_dict = {}
    read_only_lf_ds = []
    read_only_datasets = set()
    read_only_filelevel = set()
    read_only_lf_ds = []
    # for user_access_type, user_dataset_list in dataset_ids_dict.items():
    #     for user_dataset_item in user_dataset_list:
    #         dataset_access_dict = {
    #             'DatasetId': user_dataset_item,
    #             'AccessType': user_access_type,
    #             'Status': 'failed'
    #         }
    #         dataset_access_list.append(dataset_access_dict)

    user_dataset_access_dict = retrieve_user_accessible_resources(dynamodb_resource, "datasets", user_id, audit_log_config, read_only_file_level=True)
    for dataset_id in dataset_ids_dict.get("Owner", []):
        #user_permission = get_user_resource_permission(dynamodb_resource, "datasets", dataset_id, user_id, audit_log_config)
        #user_permission = get_user_dataset_permission(dynamodb_resource, dataset_id, user_id, audit_log_config)
        user_permission = user_dataset_access_dict.get(dataset_id, {})
        access_type = user_permission.get("access_type") if isinstance(user_permission, dict) else user_permission
        LOGGER.info("In authUtil.authorize_user_datasets, user_permission - %s on dataset - %s", access_type, dataset_id)
        if access_type in ["owner", "editor"]:
            dataset_access_dict = {"DatasetId": dataset_id, "AccessType": access_type, "Status": "success"}
            dataset_access_list.append(dataset_access_dict)
        else:
            dataset_access_dict = {"DatasetId": dataset_id, "AccessType": access_type, "Status": "failed"}
            dataset_access_list.append(dataset_access_dict)

    for dataset_id in dataset_ids_dict.get("ReadOnly", []):
        #user_permission = get_user_resource_permission(dynamodb_resource, "datasets", dataset_id, user_id, audit_log_config)
        #user_permission = get_user_dataset_permission(dynamodb_resource, dataset_id, user_id, audit_log_config)
        user_permission = user_dataset_access_dict.get(dataset_id, {})
        access_type = user_permission.get("access_type") if isinstance(user_permission, dict) else user_permission
        readonly_filelevel = user_permission.get("readonly_filelevel", False) if isinstance(user_permission, dict) else False
        LOGGER.info("In authUtil.authorize_user_datasets, user_permission - %s on dataset - %s", access_type, dataset_id)
        if (access_type == "read-only" and not readonly_filelevel) or access_type in ["owner", "editor"]:
            dataset_access_dict = {"DatasetId": dataset_id, "AccessType": "read-only", "Status": "success"}
            read_only_datasets.add(dataset_id)
            dataset_access_list.append(dataset_access_dict)
        else:
            dataset_access_dict = {"DatasetId": dataset_id, "AccessType": "read-only", "Status": "failed"}
            dataset_access_list.append(dataset_access_dict)

    for dataset_id in dataset_ids_dict.get("ReadOnlyFileLevel", []):
        user_permission = user_dataset_access_dict.get(dataset_id, {})
        access_type = user_permission.get("access_type") if isinstance(user_permission, dict) else user_permission
        LOGGER.info("In authUtil.authorize_user_datasets, user_permission - %s on dataset - %s", access_type, dataset_id)
        if access_type in ["owner", "editor", "read-only"]:
            dataset_access_dict = {"DatasetId": dataset_id, "AccessType": "read-only", "Status": "success"}
            read_only_filelevel.add(dataset_id)
            dataset_access_list.append(dataset_access_dict)
        else:
            dataset_access_dict = {"DatasetId": dataset_id, "AccessType": "read-only", "Status": "failed"}
            dataset_access_list.append(dataset_access_dict)
    # Validate if user has attached any read-only type datasets in jobs
    # Note : As lakeformation doesnot support column filtering we are restricting users from plugging-in read-only type lf datasets
    # Resource : https://docs.aws.amazon.com/lake-formation/latest/dg/limitations.html
    # This block can be removed once lakeformation starts supporting it.
    if os_env_var_dict.get("requestType", "N/A") == "Jobs" and read_only_datasets:
        consolidated_dataset_detail = dynamodbUtil.batch_get_items(
            os_env_var_dict["dynamoDBResource"],
            os_env_var_dict["datasetTableName"],
            [{"DatasetId": item} for item in read_only_datasets],
            audit_log_config,
            "DatasetId,DatasetName,TargetLocation",
        )
        read_only_lf_ds = commonUtil.check_lf_datasets(consolidated_dataset_detail, user_id, audit_log_config)
    # Raise exception if user has readonly permissions on the dataset
    if read_only_lf_ds:
        ec_ds_1059 = errorUtil.get_error_object("DS-1059")
        ec_ds_1059["Message"] = ec_ds_1059["Message"].format(", ".join(set(read_only_lf_ds)), "job")
        raise errorUtil.InvalidInputException(EVENT_INFO, ec_ds_1059)

    LOGGER.info("In authUtil.authorize_user_datasets, dataset access list - %s", dataset_access_dict)
    return dataset_access_list


def validate_user_access_on_resources(user_id: str, dynamodb_resource, resources_dict: dict, tables_dict: dict, audit_log_config: dict) -> tuple:
    """
    This method validates if the user has access on the resources passed in the input
    Args:
        user_id (str): User Id
        dynamodb_resource: boto3 dynamodb resource
        resources_dict (dict): resources dict required for resources to validate
        Example:     {"DatasetOwner": [{DatasetId: <dataset_id>, DatasetName: <dataset_name>}, {DatasetId: <dataset_id>, DatasetName: <dataset_name>}, ....],
                    "DatasetRead": [{DatasetId: <dataset_id>, DatasetName: <dataset_name>}, {DatasetId: <dataset_id>, DatasetName: <dataset_name>}, ....],
                    "Parameters": [parameters list],
                    "Libraries": [libraries list] }
        tables_dict (dict): tables dict required for resources to validate
        Example:     {"DatasetTableName": <table_name>, "UserTableName": <table_name>.........}

    Returns:
        bool: True if user has access on all the resources, False otherwise
        str: Message indicating the status of the user's access on the resources
    """
    # ******************************************************************************
    # For sample input on how to pass input to this method, refer above doc string
    # ******************************************************************************

    LOGGER.info("In authUtil.validate_user_access_on_resources, starting the method")
    overall_access = True
    success_message = "User {} have access to all resources".format(user_id)
    failed_message = "User {} does not have access on the resources,".format(user_id)
    if commonUtil.get_super_admin_context():
        return True, "Super Admin mode active for user {}, skipping access validation".format(user_id)
    if resources_dict.get("DatasetOwner", []) or resources_dict.get("DatasetRead", []) or resources_dict.get("DatasetFileLevel", []):
        # Validate if all the required tables are passed in the input
        LOGGER.info(
            "In authUtil.validate_user_access_on_resources, DatasetOwner or DatasetRead list is provided, check if the user has required permisions on these datasets"
        )

        # Create dict in the format of {'Owner': [], 'Editor': [], 'Viewer': []}, which is input for the method authorize_user_datasets
        dataset_ids_dict = {}
        dataset_ids_dict["Owner"] = [each_dataset_item["DatasetId"] for each_dataset_item in resources_dict.get("DatasetOwner", [])]
        dataset_ids_dict["ReadOnly"] = [each_dataset_item["DatasetId"] for each_dataset_item in resources_dict.get("DatasetRead", [])]
        dataset_ids_dict["ReadOnlyFileLevel"] = [each_dataset_item["DatasetId"] for each_dataset_item in resources_dict.get("DatasetFileLevel", [])]

        dataset_access_result = authorize_user_datasets(dynamodb_resource, user_id, dataset_ids_dict, audit_log_config)
        # Above method returns the results in the format of [{"DatasetId": <dataset_id>, "AccessType": <access_type>, "Status": <failed/success>}.....]
        not_accessible_datasets = []
        # Append dataset names to the list so that it can be passed as return message to the user
        for each_dataset in dataset_access_result:
            if each_dataset["Status"] == "failed":
                overall_access = False
                not_accessible_datasets = not_accessible_datasets + [
                    each_dataset_item["DatasetName"]
                    for each_dataset_item in resources_dict.get("DatasetOwner", [])
                    if each_dataset_item["DatasetId"] == each_dataset["DatasetId"]
                ]

                not_accessible_datasets = not_accessible_datasets + [
                    each_dataset_item["DatasetName"]
                    for each_dataset_item in resources_dict.get("DatasetRead", [])
                    if each_dataset_item["DatasetId"] == each_dataset["DatasetId"]
                ]

                not_accessible_datasets = not_accessible_datasets + [
                    each_dataset_item["DatasetName"]
                    for each_dataset_item in resources_dict.get("DatasetFileLevel", [])
                    if each_dataset_item["DatasetId"] == each_dataset["DatasetId"]
                ]

        LOGGER.info(
            "In authUtil.validate_user_access_on_resources, user does not have access on the datasets %s",
            str(list(set(not_accessible_datasets))),
        )
        failed_message = failed_message + " datasets - " + str(list(set(not_accessible_datasets)))

    if resources_dict.get("Parameters", []) != []:
        LOGGER.info("In authUtil.validate_user_access_on_resources, parameter list is provided, check if all the tables are provided for this resource")
        parameters_tables = ["ParametersTableName", "ParametersIndexName"]
        if set(parameters_tables) - set(tables_dict):
            ec_ipv_1037 = errorUtil.get_error_object("IPV-1037")
            ec_ipv_1037["Message"] = ec_ipv_1037["Message"].format(set(parameters_tables) - set(tables_dict), "parameter")
            raise errorUtil.InvalidInputException(EVENT_INFO, ec_ipv_1037)

        parameters_access = commonUtil.check_parameter_access(
            dynamo_resource=dynamodb_resource,
            user_id=user_id,
            parameter_keys=resources_dict["Parameters"],
            audit_log_config=audit_log_config,
        )
        if parameters_access["NoAccess"]:
            LOGGER.info(
                "In authUtil.validate_user_access_on_resources, user does not have access on the parmeters %s",
                str(parameters_access["NoAccess"]),
            )
            overall_access = False
            failed_message = failed_message + " parameters - " + str(list(parameters_access["NoAccess"]))

    if resources_dict.get("Libraries", []) != []:
        LOGGER.info("In authUtil.validate_user_access_on_resources, parameter list is provided, check if all the tables are provided for this resource")

        libraries_tables = ["UserTableName", "JobLibrariesTableName"]
        if set(libraries_tables) - set(tables_dict):
            ec_ipv_1037 = errorUtil.get_error_object("IPV-1037")
            ec_ipv_1037["Message"] = ec_ipv_1037["Message"].format(set(libraries_tables) - set(tables_dict), "parameter")
            raise errorUtil.InvalidInputException(EVENT_INFO, ec_ipv_1037)

        user_access_libs_list = retrieve_user_accessible_resources(
            dynamodb_resource,
            "jobslibs",
            user_id,
            audit_log_config,
        )
        no_access_lib_list = list(set(resources_dict["Libraries"]) - set(user_access_libs_list))

        if no_access_lib_list:
            # Get names of libraries, because above results in list of UUID's
            LOGGER.info(
                "In authUtil.validate_user_access_on_resources, get names of libraries for corresponding library id's %s",
                str(no_access_lib_list),
            )
            library_ids = [{"LibraryId": library_id} for library_id in no_access_lib_list]
            library_items = dynamodbUtil.batch_get_items(dynamodb_resource, tables_dict["JobLibrariesTableName"], library_ids, audit_log_config)
            if len(library_items) != len(library_ids):
                LOGGER.error(
                    "In authUtil.validate_user_access_on_resources, ids passed %s, libraries retrieved %s",
                    library_ids,
                    library_items,
                )
                ec_ge_1026 = errorUtil.get_error_object("GE-1026")
                raise errorUtil.GenericFailureException(EVENT_INFO, ec_ge_1026)
            libraries_item_names = [each_library.get("LibraryName", "N/A") for each_library in library_items]
            LOGGER.info(
                "In authUtil.validate_user_access_on_resources, User does not have access to the libraries - %s",
                libraries_item_names,
            )
            overall_access = False
            failed_message = failed_message + " libraries - " + str(libraries_item_names)

    message = failed_message if overall_access is False else success_message
    LOGGER.info(
        "In authUtil.validate_user_access_on_resources, overall access status of the user %s is %s and details are %s",
        str(user_id),
        str(overall_access),
        str(message),
    )

    return overall_access, message


@validate_resource_type
def list_authorized_entities_for_resource(
    dynamodb_resource,
    resource_type: str,
    resource_id: str,
    requestor_user_id: str,
    audit_log_config: dict,
    dla_info: bool = False,
    tag_aws_resource: bool = False
) -> dict:
    """
    Retrieves authorized entities(users/tags) for a resource segregated by their access type

    Args:
        dynamodb_resource:
        resource_type (str): Type of resource(eg: dataset, job, etc)
        resource_id (str): UUID of the resource
        requestor_user_id (str): User Id
        audit_log_config (dict): Configuration for audit logging

    Returns:
        dict
    """
    LOGGER.info("In authUtil.list_authorized_entities_for_resource, Retrieving users and tags who have access to the resource of type %s with id %s", resource_type, resource_id)
    if requestor_user_id != commonUtil.SYSTEM_RUNNER_ID:
        user_permission = get_user_resource_permission(dynamodb_resource, resource_type, resource_id, requestor_user_id, audit_log_config)
        check_access_level(requestor_user_id, user_permission, AccessType.READONLY)

    acl_response = dynamodbUtil.get_items_by_query(
        dynamodb_resource.Table(ACL_RESOURCES_TABLE),
        Key("ResourceId").eq(resource_id) & Key("TagAccessKey").begins_with(f"{resource_type}#"),
        "TagAccessKey,AdditionalMetadata",
        audit_log_config,
    )

    # Adding DLA information for domains
    if resource_type == "domains" and dla_info:
        result = {access_type.label.capitalize(): [] for access_type in AccessType if access_type != AccessType.NONE}
        for domain_access_item in acl_response:
            tag_access_key = domain_access_item["TagAccessKey"]
            tag_key = tag_access_key.split("#")[1]
            tag_value = tag_access_key.split("#")[2]
            access_type = tag_access_key.split("#")[-1]
            dla_access = domain_access_item.get("AdditionalMetadata", {}).get("IsDatasetLevelAccessProvided", False)
            result[access_type.capitalize()].append({"TagKey": tag_key, "TagValue": tag_value, "IsDatasetLevelAccessProvided": dla_access})
        return result

    # Adding TagAwsResource information for datasets
    if resource_type == "datasets" and tag_aws_resource:
        result = {access_type.label.capitalize(): [] for access_type in AccessType if access_type != AccessType.NONE}
        for dataset_access_item in acl_response:
            tag_access_key = dataset_access_item["TagAccessKey"]
            tag_key = tag_access_key.split("#")[1]
            tag_value = tag_access_key.split("#")[2]
            access_type = tag_access_key.split("#")[-1]
            tag_aws_resource_flag = dataset_access_item.get("AdditionalMetadata", {}).get("TagAwsResources", False)
            result[access_type.capitalize()].append({
                "TagKey": tag_key,
                "TagValue": tag_value,
                "TagAwsResources": tag_aws_resource_flag
            })
        return result
    tag_access_keys_list = [item["TagAccessKey"] for item in acl_response]
    authorized_entities = segregate_access_details(tag_access_keys_list)
    if commonUtil.get_super_admin_context():
        authorized_entities["Owner"].append({"TagKey": "user", "TagValue": requestor_user_id})
    return authorized_entities

def time_it(func):
    """Decorator to measure execution time of a function."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"Function {func.__name__} took {elapsed_time:.6f} seconds")
        return result
    return wrapper

#The following code is commented out due to the beta implementation of cache logic.
# def remove_context_if_datasets(func):
#     """Decorator to remove context from audit_log_config"""
#     @functools.wraps(func)
#     def wrapper(dynamodb_resource, resource_type, user_id, audit_log_config, *args, **kwargs):
#         if resource_type == "datasets" and isinstance(audit_log_config, dict):
#             audit_log_config.pop('context', None)
#             audit_log_config = json.dumps(audit_log_config)
#         return func(dynamodb_resource, resource_type, user_id, audit_log_config, *args, **kwargs)
#     # Expose cache methods from the wrapped function
#     # The @lru_cache decorator gets overridden by the @remove_context_if_datasets decorator.
#     # Since @remove_context_if_datasets wraps retrieve_user_accessible_resources, the function returned
#     # by this decorator does not retain lru_cache attributes like cache_info().
#     # To ensure cache_info and cache_clear are accessible, they need to be explicitly exposed in remove_context_if_datasets.
#     wrapper.cache_info = func.cache_info
#     wrapper.cache_clear = func.cache_clear
#     return wrapper

# def conditional_lru_cache(maxsize=128):
#     """A decorator that applies lru_cache only if resource_type is 'datasets'."""
#     def decorator(func):
#         cache = lru_cache(maxsize=maxsize)(func)  # Apply LRU caching

#         @wraps(func)
#         def wrapper(dynamodb_resource, resource_type, user_id, audit_log_config, *args, **kwargs):
#             if resource_type == "datasets":
#                 return cache(dynamodb_resource, resource_type, user_id, audit_log_config, *args, **kwargs)
#             return func(dynamodb_resource, resource_type, user_id, audit_log_config, *args, **kwargs)

#         # Expose cache_info() and cache_clear() for external access
#         wrapper.cache_info = cache.cache_info
#         wrapper.cache_clear = cache.cache_clear

#         return wrapper
#     return decorator

# This lru_cache on retrieve_user_accessible_resources is the python inbuilt cache provided by functools
@validate_resource_type
# @remove_context_if_datasets
@time_it
# @conditional_lru_cache(maxsize=MAX_CACHE_SIZE)
def retrieve_user_accessible_resources(dynamodb_resource, resource_type: str, user_id: str, audit_log_config: dict, ignore_dla: bool = False, dla_domains: bool = False, read_only_file_level: bool = False) -> dict:
    """
    Returns a dictionary of user accessible resources under a particular resource type along with their access types

    Args:
        dynamodb_resource: boto3 dynamodb resource
        resource_type (str): Type of resource(eg: datasets, jobs, etc)
        user_id (str): User Id
        audit_log_config (dict): Configuration for audit logging

    Returns:
        dict: Dictionary of user accessible resources along with their access types
    """
    LOGGER.info("In authUtil.retrieve_user_accessible_resources, Retrieving accessible resources of type - %s for user %s", resource_type, user_id)

    # Check if Super Admin mode is active - return all resources with owner access
    is_super_admin = commonUtil.get_super_admin_context()
    if is_super_admin:
        LOGGER.info("In authUtil.retrieve_user_accessible_resources, Super Admin mode active for user %s, returning all resources with owner access", user_id)
        # Query all resources of the given type from ACL_RESOURCES_TABLE using GSI
        resources_with_access_types = {}

        # Query ACL_RESOURCES_TABLE using GSI on ResourceType
        key_condition_expression = Key("ResourceType").eq(resource_type)
        acl_resources = dynamodbUtil.get_items_by_query_index(
            dynamodb_resource.Table(ACL_RESOURCES_TABLE),
            ACL_RESOURCES_TABLE_RESOURCETYPE_INDEX,
            audit_log_config,
            key_condition_expression,
        )

        # Extract unique resource IDs from ACL resources
        seen_resource_ids = set()
        for acl_resource in acl_resources:
            resource_id = acl_resource.get("ResourceId")
            if resource_id and resource_id not in seen_resource_ids:
                seen_resource_ids.add(resource_id)
                if read_only_file_level:
                    resources_with_access_types[resource_id] = {
                        "access_type": "owner",
                        "readonly_filelevel": False
                    }
                else:
                    resources_with_access_types[resource_id] = "owner"

        # Validate multi tenancy flag and add default tenant if applicable
        if MULTI_TENANCY == "yes" and resource_type == "tenants":
            resources_with_access_types[PROJECT_SHORT_NAME] = "owner"

        LOGGER.info("In authUtil.retrieve_user_accessible_resources, Super Admin mode: returning %d resources with owner access", len(resources_with_access_types))
        return resources_with_access_types

    #The following code is commented out due to the beta implementation of cache logic.
    # Converting audit_log_config back to a dictionary to avoid unhashable type issues when caching
    # if resource_type == "datasets":
    # audit_log_config = json.loads(audit_log_config)
    tags_list = retrieve_user_accessible_tags(dynamodb_resource, user_id, audit_log_config)
    resources_with_access_types = {}
    starting_sort_key = f"{resource_type}#{tags_list[0]}#{AccessType.EDITOR.label}"
    ending_sort_key = f"{resource_type}#{tags_list[-1]}#{AccessType.READONLY.label}"

    key_condition_expression = Key("ResourceType").eq(resource_type) & Key("TagAccessKey").between(starting_sort_key, ending_sort_key)

    acl_response = dynamodbUtil.get_items_by_query_index(
        dynamodb_resource.Table(ACL_RESOURCES_TABLE),
        ACL_RESOURCES_TABLE_RESOURCETYPE_INDEX,
        audit_log_config,
        key_condition_expression,
    )

    # for datasets checking DLA access via domains
    if resource_type == "datasets" and not ignore_dla:
        starting_sort_key = f"domains#{tags_list[0]}#{AccessType.EDITOR.label}"
        ending_sort_key = f"domains#{tags_list[-1]}#{AccessType.READONLY.label}"
        key_condition_expression = Key("ResourceType").eq("domains") & Key("TagAccessKey").between(starting_sort_key, ending_sort_key)
        acl_domains_response = dynamodbUtil.get_items_by_query_index(
            dynamodb_resource.Table(ACL_RESOURCES_TABLE),
            ACL_RESOURCES_TABLE_RESOURCETYPE_INDEX,
            audit_log_config,
            key_condition_expression,
        )
        if acl_domains_response:
            for domain_item in acl_domains_response:
                if domain_item.get("AdditionalMetadata", {}).get("IsDatasetLevelAccessProvided", False):
                    tag_access_key = domain_item["TagAccessKey"]
                    tag_name = "#".join(tag_access_key.split("#")[1:3])
                    current_access_type = tag_access_key.split("#")[-1]
                    # fetch datasets under the domain
                    dataset_items = dynamodbUtil.get_items_by_query_index(
                        dynamodb_resource.Table(dynamodbUtil.DATASET_TABLE),
                        dynamodbUtil.DATASET_TABLE_DOMAIN_INDEX_NAME,
                        audit_log_config,
                        Key("Domain").eq(domain_item["ResourceId"]),
                        "DatasetId",
                        None,
                    )
                    for dataset_item in dataset_items:
                        dataset_acl_item = {"ResourceId": dataset_item["DatasetId"], "TagAccessKey": f"datasets#{tag_name}#{current_access_type}"}
                        acl_response.append(dataset_acl_item)

    if acl_response:
        for item in acl_response:
            # If the dla_domain flag is True, the condition below will evaluate to True only if the user has dataset-level access for a domain. This ensures that the result includes only domains with dataset-level access.
            # However, if the dla_domain flag is False, the condition is always True, and the result will include all domains to which the user has access.
            if not dla_domains or item.get("AdditionalMetadata", {}).get("IsDatasetLevelAccessProvided", False):
                resource_id = item["ResourceId"]
                tag_access_key = item["TagAccessKey"]
                current_access_type = tag_access_key.split("#")[-1]
                current_priority = get_access_priority(tag_access_key)
                tag = "#".join(tag_access_key.split("#")[1:3])
                # Filter out tags which user does not have access to and capture only the highest access the user has on resource
                if tag in tags_list:
                    if read_only_file_level:
                        file_level_access = item.get("AdditionalMetadata", {}).get("TagAwsResources", False)
                        readonly_filelevel_flag = False
                        if current_access_type.lower() == "read-only" and file_level_access:
                            readonly_filelevel_flag = True
                        if (resource_id not in resources_with_access_types) or (
                            AccessType.from_label(resources_with_access_types[resource_id]["access_type"]).priority < current_priority
                        ):
                            resources_with_access_types[resource_id] = {
                                "access_type": current_access_type,
                                "readonly_filelevel": readonly_filelevel_flag
                            }
                    else:
                        if (
                            resource_id not in resources_with_access_types
                            or AccessType.from_label(resources_with_access_types[resource_id]).priority < current_priority
                        ):
                            resources_with_access_types[resource_id] = current_access_type

    # Validate multi tenancy flag and add default tenant if applicable
    if MULTI_TENANCY == "yes" and resource_type == "tenants":
        resources_with_access_types[PROJECT_SHORT_NAME] = "owner"

    LOGGER.info("In authUtil.retrieve_user_accessible_resources, exiting with resources_with_access_types - %s", resources_with_access_types)
    return resources_with_access_types


# pylint: disable=too-many-arguments
# pylint: disable=too-many-function-args
def manage_access_on_resource_sharing(
    dynamodb_resource,
    resource_type: str,
    resources_dict: dict,
    access_tags: list,
    desired_access_type: AccessType,
    user_id: str,
    audit_log_config: dict,
    tag_aws_resources: bool = False,
    is_dla_provided: bool = False,
    bypass_kb_source_acl: bool = False,
    revert_revoke_operation: bool = False,
    event: dict = None,
    **kwargs: dict,
) -> None:
    """
    Grant or revoke a user/tag with access to resource(s)
    Args:
        resource_type (str): Type of resource(eg: dataset, job, etc)
        resources_dict (dict): List of resources Ids with their names
        access_tags(list): A list of dictionaries, each containing a 'TagKey' and 'TagValue'
        desired_access_type (AccessType): Desired Access type (owner, editor, READONLY) for the resource. None if it is to remove access.
        user_id (str): User Id
        audit_log_config (dict): Configuration for audit logging
        tag_aws_resources(bool): Flag to indicate if backend AWS resources are tagged
        is_dla_provided(bool): Flag to indicate if Dataset Level Access is provided for domain
        bypass_kb_source_acl(bool): Flag to indicate if Knowledge Base Source ACL should be bypassed
    Returns:
        None
    """
    LOGGER.info("In authUtil.manage_access_on_resource_sharing, managing access on resource of type -  %s with resources_dict - %s for tags %s ", resource_type, resources_dict, access_tags)

    if event is None:
        event = dict()
    acl_table = dynamodb_resource.Table(ACL_RESOURCES_TABLE)
    batch_write_keys = []
    batch_delete_keys = []
    for resource_id in resources_dict:
        for tags in access_tags:
            tag_key = tags.get("TagKey", None)
            tag_value = tags.get("TagValue", None)
            # Granting Access
            # desired_access_type should be there in case of granting access.
            # if we are trying to grant access as result of some failed revoke operation
            if revert_revoke_operation:
                if tag_key == 'user':
                    access_type = get_user_resource_permission(DYNAMODB_RES, resource_type, resource_id, tag_value, audit_log_config)
                else:
                    access_type = retrieve_tag_resource_access(dynamodb_resource, resource_type, resource_id, tag_key, tag_value, audit_log_config)
                desired_access_type = validate_access_label(access_type)
            if desired_access_type.priority > 0:
                sort_key = f"{resource_type}#{tag_key}#{tag_value}#{desired_access_type.label}"
                put_item = {
                    "ResourceId": resource_id,
                    "ResourceName": resources_dict[resource_id],
                    "TagAccessKey": sort_key,
                    "ResourceType": resource_type,
                    "CreatedBy": user_id,
                    "CreatedTime": commonUtil.get_current_time(),
                    "AdditionalMetadata": {"TagAwsResources": tag_aws_resources},
                }
                if resource_type == "domains" and is_dla_provided:
                    put_item["AdditionalMetadata"]["IsDatasetLevelAccessProvided"] = is_dla_provided
                if resource_type == "knowledgebases" and bypass_kb_source_acl:
                    put_item["AdditionalMetadata"]["BypassKBSourceACL"] = bypass_kb_source_acl
                batch_write_keys.append(put_item)
            # Revoking Access
            # if desired_access_type is None then action is revoke and the access will be revoked from those tags irresepective of the permission they have on that resource.
            else:
                sort_key_prefix = f"{resource_type}#{tag_key}#{tag_value}#"
                response = acl_table.query(
                    KeyConditionExpression=Key('ResourceId').eq(resource_id) & Key('TagAccessKey').begins_with(sort_key_prefix)
                )
                items_to_delete = response.get('Items', [])
                for item in items_to_delete:
                    delete_item = {
                        "ResourceId": item["ResourceId"],
                        "TagAccessKey": item["TagAccessKey"]
                    }
                    batch_delete_keys.append(delete_item)
    if batch_delete_keys:
        tag_values = []
        if resource_type == "tags":
            for tag in access_tags:
                tag_key = tag.get("TagKey", None)
                tag_value = tag.get("TagValue", None)
                if tag_key == "user" and kwargs:
                    tag_values.append(tag_value)

                # revoke permissions
                # action = "revoke-auth-group-user-access"
                # pylint: disable=undefined-loop-variable
        if tag_values:
            revoke_access_to_user_on_tag_resources(
                resource_id.split("#")[0], resource_id.split("#")[-1], tag_values, user_id, audit_log_config, dynamodb_resource, event, **kwargs
            )
        if resource_type != "tags" or event.get('PermissionAction', '') == 'updated_qs_dashboards':
            dynamodbUtil.batch_delete_items(acl_table, batch_delete_keys, audit_log_config)
        else:
            event.update({"batch_delete_keys": batch_delete_keys})
    if batch_write_keys:
        tag_values = []
        for tag in access_tags:
            tag_key = tag.get("TagKey", None)
            tag_value = tag.get("TagValue", None)
            if tag_key == "user" and resource_type == "tags" and kwargs:
                tag_values.append(tag_value)
                # grant permissions
                # in case of tags there will be only 1 item in resources_dict
                resource_id = list(resources_dict.keys())[0]

        if tag_values:
            # action = "grant-auth-group-user-access"
            grant_access_to_user_on_tag_resources(
                user_id, dynamodb_resource, resource_id.split("#")[0], resource_id.split("#")[-1], tag_values, audit_log_config, event, **kwargs
            )
        if resource_type != "tags" or event.get('PermissionAction', '') == 'updated_qs_dashboards':
            dynamodbUtil.batch_write_items(acl_table, batch_write_keys, audit_log_config)
        else:
            event.update({"batch_write_keys": batch_write_keys})

@validate_resource_type
def manage_access_on_resource(
    dynamodb_resource,
    resource_type: str,
    resources_dict: dict,
    tag_key: str,
    tag_value: str,
    desired_access_type: AccessType,
    user_id: str,
    audit_log_config: dict,
    existing_access: AccessType = AccessType.NONE,
    tag_aws_resources: bool = False,
    is_dla_provided: bool = False,
    **kwargs: dict,
) -> None:
    """
    Grant or revoke a user/tag with access to resource(s)

    Args:
        resource_type (str): Type of resource(eg: dataset, job, etc)
        resources_dict (dict): List of resources Ids with their names
        tag_key (str): Key of the tag
        tag_value (str): Value of the tag
        desired_access_type (AccessType): Desired Access type (owner, editor, READONLY) for the resource. None if it is to remove access.
        user_id (str): User Id
        audit_log_config (dict): Configuration for audit logging
        existing_access (str): Existing access type for the resource. Required if desired_access_type is None.
        tag_aws_resources(bool): Flag to indicate if backend AWS resources are tagged
        is_dla_provided(bool): Flag to indicate if Dataset Level Access is provided for domain

    Returns:
        None
    """
    LOGGER.info("In authUtil.manage_access_on_resource, managing access on resource of type -  %s with id and name - %s for tag %s : %s", resource_type, resources_dict, tag_key, tag_value)
    acl_table = dynamodb_resource.Table(ACL_RESOURCES_TABLE)
    batch_write_keys = []
    batch_delete_keys = []
    for resource_id in resources_dict:

        # Granting Access
        if desired_access_type.priority > 0:
            sort_key = f"{resource_type}#{tag_key}#{tag_value}#{desired_access_type.label}"
            put_item = {
                "ResourceId": resource_id,
                "ResourceName": resources_dict[resource_id],
                "TagAccessKey": sort_key,
                "ResourceType": resource_type,
                "CreatedBy": user_id,
                "CreatedTime": commonUtil.get_current_time(),
                "AdditionalMetadata": {"TagAwsResources": tag_aws_resources},
            }

            if resource_type == "domains" and is_dla_provided:
                put_item["AdditionalMetadata"]["IsDatasetLevelAccessProvided"] = is_dla_provided
            batch_write_keys.append(put_item)

        # Revoking Access
        else:
            sort_key = f"{resource_type}#{tag_key}#{tag_value}#{existing_access.label}"
            delete_item = {"ResourceId": resource_id, "TagAccessKey": sort_key}
            batch_delete_keys.append(delete_item)

    if batch_delete_keys:
        if tag_key == "user" and resource_type == "tags" and kwargs:
            # revoke permissions
            # action = "revoke-auth-group-user-access"
            # pylint: disable=undefined-loop-variable
            revoke_access_to_user_on_tag_resources(
                resource_id.split("#")[0], resource_id.split("#")[-1], tag_value, user_id, audit_log_config, dynamodb_resource, **kwargs
            )
        dynamodbUtil.batch_delete_items(acl_table, batch_delete_keys, audit_log_config)

    if batch_write_keys:
        if tag_key == "user" and resource_type == "tags" and kwargs:
            # grant permissions
            resource_id = list(resources_dict.keys())[0]
            # action = "grant-auth-group-user-access"
            grant_access_to_user_on_tag_resources(
                user_id, dynamodb_resource, resource_id.split("#")[0], resource_id.split("#")[-1], tag_value, audit_log_config, **kwargs
            )
        dynamodbUtil.batch_write_items(acl_table, batch_write_keys, audit_log_config)


def retrieve_valid_users(dynamodb_resource, user_list, audit_log_config):
    """
    This method adds users to a group
    :param user_list: List of users
    :type user_list: list
    :param audit_log_config: Audit log configuration information
    :type audit_log_config: dict
    :return: valid users list
    :rtype: list
    """
    LOGGER.info("In authUtil.retrieve_valid_users, validating users - %s", user_list)
    # To handle edge case when no user input is passed
    if not user_list:
        return []
    user_list = commonUtil.valid_user_list(list(user_list), dynamodb_resource.Table(USER_TABLE), audit_log_config)
    if user_list["valid_users"]:
        valid_members = user_list["valid_users"]
        invalid_members = user_list["invalid_users"]
    else:
        ec_ipv_1001 = errorUtil.get_error_object("IPV-1001")
        ec_ipv_1001["Message"] = "Input does not contain valid users to update the group"
        raise errorUtil.InvalidInputException(EVENT_INFO, ec_ipv_1001)
    LOGGER.info("In authUtil.retrieve_valid_users, valid users are - %s, skipping invalid users - %s", valid_members, invalid_members)
    return valid_members


def lf_permissions(user_details, user_id, dataset_item, action, tag_key, tag_value, access_type, audit_log_config, success_list, **kwargs):
    """
    This method retieves user details and updates lf permissions
    :param user_details(dict): user details
    :param user_id(str): user id
    :param dataset_item(dict): dataset item
    :param action(str): action
    :param tag_key(str): tag key
    :param tag_value(str): tag value
    :param access_type(str): access to be provided or revoked
    :param audit_log_config(dict): audit log config
    :param success_list(list): list containing dataset ids which are successfully shared
    :param kwargs(dict): keyword arguments
    :return: None
    :rtype: None
    """
    LOGGER.info("In authUtil.lf_permissions, updating lakeformation permissions for dataset - %s , user - %s", dataset_item["DatasetId"], user_id)
    catalog_id = dataset_item.get("CatalogId", ACCOUNT_ID)
    commonUtil.apply_effective_user_lf_permission(
        user_details,
        dataset_item,
        kwargs["LF_CLIENT"],
        catalog_id,
        kwargs["LF_TABLES"],
        action,
        audit_log_config,
        access_type,
        f"{tag_key}#{tag_value}",
    )
    success_list.append(dataset_item["DatasetId"])
    LOGGER.info("In authUtil.lf_permissions, exiting method")

def update_lf_permission(tag_key, tag_value, user_id, action, dynamodb_resource, audit_log_config, event, **kwargs):
    """
    This method assigns/revokes user lakeformation permissions related to a dataset
    Args:
        tag_key (str): Tag key
        tag_value (str): Tag value
        user_id (str): User ID
        action (str): Action to be performed
        dynamodb_resource: boto3 dynamodb resource
        audit_log_config: audit log configuration
        event: event information
        kwargs: keyword arguments
    Returns:
        None
    """
    LOGGER.info(
        "In authUtil.update_lf_permission, updating lakeformation permissions for tag_key - %s, tag_key - %s, operation - %s",
        tag_key,
        tag_value,
        action
    )
    if event.get('lf_dataset_ids_dict'):
        datasets_batch_start_index = event.get('lf_datasets_current_index', 0)
        lf_dataset_ids_list = list(event.get('lf_dataset_ids_dict').keys())
        datasets_batch = lf_dataset_ids_list[datasets_batch_start_index: datasets_batch_start_index + DATASET_BATCH_SIZE]
        LOGGER.info("In authUtil.update_lf_permission, datasets_batch - %s", datasets_batch)
        consolidated_dataset_detail = dynamodbUtil.batch_get_items(
            DYNAMODB_RES, DATASET_TABLE, [{"DatasetId": item} for item in datasets_batch], audit_log_config, None
        )
        LOGGER.info("In authUtil.update_lf_permission, consolidated_dataset_detail - %s", consolidated_dataset_detail)
        if commonUtil.is_valid_user(user_id, dynamodb_resource.Table(USER_TABLE), audit_log_config):
            success_list = event.get('success_list', [])
            user_details = commonUtil.get_userdetails(user_id, USER_TABLE, dynamodb_resource, audit_log_config)
            if "IAMRole" not in user_details:
                LOGGER.info("In authUtil.update_lf_permission, creating the missing IAM role for user - %s", user_details["UserId"])
                user_details = commonUtil.create_iam_roles_for_users(
                    "lakeformation", [user_details], dynamodb_resource, USER_TABLE, kwargs["IAMUTIL_OS_ENV_VAR_DICT"], audit_log_config
                )[0]
            try:
                with ThreadPoolExecutor(max_workers=10) as executor:
                    futures = [executor.submit(
                        lf_permissions,
                        user_details, user_id, dataset_item, action, tag_key, tag_value,
                        event.get('lf_dataset_ids_dict', {}).get(dataset_item['DatasetId']),
                        audit_log_config, success_list, **kwargs) for dataset_item in consolidated_dataset_detail]
                    for future in as_completed(futures):
                        future.result()# to raise exceptions if any
            except Exception as ex:
                LOGGER.error("In authUtil.update_lf_permission, failed to provide lakeformation permission due to ex - %s", str(ex))
                event.update({'success_list': success_list})
                raise

            event.update({
                'success_list': success_list,
                'lf_datasets_current_index': datasets_batch_start_index + DATASET_BATCH_SIZE,
                'lf_dataset_permissions_process': 'in_progress' if (datasets_batch_start_index + DATASET_BATCH_SIZE) < len(lf_dataset_ids_list) else 'completed'
            })
    else:
        LOGGER.info("In authUtil.update_lf_permission, no datasets found attached to tag")
    LOGGER.info("In authUtil.update_lf_permission, exiting method.")


# pylint: disable=too-many-function-args
def grant_access_to_user_on_tag_resources(requestor_id, dynamodb_resource, tag_key, tag_value, user_to_be_added, audit_log_config, event=None, **kwargs):
    """
    This method is used to grant access to user on resources belonging to a tag
    Args:
        requestor_id (str): Requestor's User Id
        dynamodb_resource: boto3 dynamodb resource
        tag_key (str): Tag key
        tag_value (str): Tag value
        user_to_be_added (list): list[User Id]
        audit_log_config (dict): Configuration for audit logging
        event (dict): event info
        kwargs (dict): keyword arguments
    Returns:
        None
    """
    if event is None:
        event = dict()
    response = dict()
    if isinstance(user_to_be_added, str):
        user_to_be_added = [user_to_be_added]
    if "lf_dataset_permissions_process" not in event:
        LOGGER.info("In authUtil.grant_access_to_user_on_tag_resources, granting access to user %s on resources accessible to tag %s : %s", user_to_be_added, tag_key, tag_value)
        conn = redshiftUtil.get_redshift_connection(kwargs["DWH_HOST"], kwargs["DWH_PORT"], kwargs["DWH_USER"], kwargs["DWH_PASSWORD"], kwargs["DWH_DATABASE"])
        response = add_users_to_group(user_to_be_added, dynamodb_resource, conn, tag_key, tag_value, audit_log_config, **kwargs)
    event.update({"PermissionAction": "user_added_to_redshift_group"})
    if "lf_dataset_permissions_process" in event or response["statusCode"] == 200:
        action = "grant-auth-group-user-access"
        if event.get('lf_dataset_permissions_process', '') != 'completed':
            update_lf_permission(tag_key, tag_value, user_to_be_added[0], action, dynamodb_resource, audit_log_config, event, **kwargs)

        if 'lf_dataset_permissions_process' in event and event.get('lf_dataset_permissions_process', '') != 'completed':
            return
        else:
            event.update({"PermissionAction": "user_granted_lf_permissions"})

        # Update user profile information if any tenants exist in the group
        tenant_resources = [
            list(tenant_item)[0] for tenant_item in retrieve_resources_attached_to_tag("tenants", tag_key, tag_value, dynamodb_resource, audit_log_config)
        ]
        if tenant_resources:
            update_tenant_user_profile(user_to_be_added, tenant_resources, dynamodb_resource, USER_TABLE, kwargs["ADD_FUNC_ARGS_DICT"], "Attach", requestor_id)
        event.update({"PermissionAction": "updated_tenant_profile"})

        # update dashboards permissions
        for user_id in user_to_be_added:
            update_dashboard_permissions("grant", dynamodb_resource, tag_key, tag_value, user_id, event, audit_log_config)

        event.update({"PermissionAction": "updated_qs_dashboards"})
    elif response.get("statusCode") != 200:
        raise Exception("Failed to update redshift group")
    LOGGER.info("In authUtil.grant_access_to_user_on_tag_resources, exiting method.")


def manage_data_lake_permission_to_user_role(user_role_arn, tag_key, tag_value, user_id, lf_client, action="grant"):
    """
    Manage lake formation permissions for a tag value to a list IAM roles
    :param user_roles_arn: IAM role of the user
    :param tag_name: Tag key Name
    :param tag_value: Tag value
    :param user_id: User name
    :param action: Grant or revoke permission to the user role arn
    :return: None
    """
    LOGGER.info(
        "In tagManagement.manage_data_lake_permission_to_user_role, action: %s, tag_name: %s, tag_value: %s, user_id: %s", action, tag_key, tag_value, user_id
    )
    permission_object = {
        "Entries": [
            {
                "Id": f"{user_id}-{tag_key}-{tag_value}-owner-{action}",
                "Principal": {"DataLakePrincipalIdentifier": f"arn:{AWS_PARTITION}:iam::{ACCOUNT_ID}:role/{user_role_arn}"},
                "Resource": {"LFTagPolicy": {"ResourceType": "TABLE", "Expression": [{"TagKey": f"{tag_key}={tag_value}", "TagValues": ["owner"]}]}},
                "Permissions": commonUtil.LF_DS_PERMISSIONS["owner"],
            },
            {
                "Id": f"{user_id}-{tag_key}-{tag_value}-editor-{action}",
                "Principal": {"DataLakePrincipalIdentifier": f"arn:{AWS_PARTITION}:iam::{ACCOUNT_ID}:role/{user_role_arn}"},
                "Resource": {"LFTagPolicy": {"ResourceType": "TABLE", "Expression": [{"TagKey": f"{tag_key}={tag_value}", "TagValues": ["editor"]}]}},
                "Permissions": commonUtil.LF_DS_PERMISSIONS["editor"],
            },
            {
                "Id": f"{user_id}-{tag_key}-{tag_value}-read-only-{action}",
                "Principal": {"DataLakePrincipalIdentifier": f"arn:{AWS_PARTITION}:iam::{ACCOUNT_ID}:role/{user_role_arn}"},
                "Resource": {"LFTagPolicy": {"ResourceType": "TABLE", "Expression": [{"TagKey": f"{tag_key}={tag_value}", "TagValues": ["read-only"]}]}},
                "Permissions": ["SELECT", "ALTER"],  # for creating glue partition when columns are explicitly tagged we need 'ALTER' permission
            },
            {
                "Id": f"{user_id}-{tag_key}-{tag_value}-restrict-{action}",
                "Principal": {"DataLakePrincipalIdentifier": f"arn:{AWS_PARTITION}:iam::{ACCOUNT_ID}:role/{user_role_arn}"},
                "Resource": {"LFTagPolicy": {"ResourceType": "TABLE", "Expression": [{"TagKey": f"{tag_key}={tag_value}", "TagValues": ["restrict"]}]}},
                "Permissions": ["ALTER"],
            },
        ]
    }
    try:
        if action == "grant":
            lf_client.batch_grant_permissions(**permission_object)
        elif action == "revoke":
            lf_client.batch_revoke_permissions(**permission_object)
    except Exception as ex:
        LOGGER.error("In tagManagement.manage_data_lake_permission_to_user_role, failed to grant/revoke batch permissions %s", str(ex))
        ec_ge_1034 = errorUtil.get_error_object("GE-1034")
        ec_ge_1034["Message"] = f"Failed to grant/revoke batch permissions due to error: {str(ex)}"
        raise errorUtil.GenericFailureException(EVENT_INFO, ec_ge_1034)


def add_users_to_group(members, dynamodb_resource, conn, tag_key, tag_value, audit_log_config, **kwargs):
    """
    This is main function to add users to group
    :param members_info json body from API
    :param user_id requested
    :dynamo_resp refer below
    """
    # validating tenant access for new members
    validate_user_tenant_access(members, tag_key, tag_value, dynamodb_resource, audit_log_config)
    # validating domain access for new members
    validate_user_domain_access(members, tag_key, tag_value, dynamodb_resource, audit_log_config)

    # Adding members to DWH
    LOGGER.info("Adding members in DWH group")
    # dwh_members_new = []
    # for i in new_members:
    if kwargs["DATALAKE_DWH"] == "redshift":
        usernames = []
        for member in members:
            user_details = commonUtil.get_userdetails(member, USER_TABLE, dynamodb_resource, audit_log_config)
            usernames.append(user_details["UserName"])
        redshiftUtil.add_users_to_redshift_group(f"{tag_key}${tag_value}", ",".join(usernames), conn)
        try:
            role_name = redshiftUtil.get_tag_redshift_role_name(tag_key, tag_value)
            redshiftUtil.grant_redshift_role_to_users(role_name, usernames, conn)
        except redshiftUtil.RedshiftTableException as rs_ex:
            ec_rs_1017 = errorUtil.get_error_object("RS-1017")
            ec_rs_1017["Message"] = rs_ex
            raise errorUtil.InvalidInputException(EVENT_INFO, ec_rs_1017)
        try:
            tag_domains = [
                    list(domain_item)[0] for domain_item in retrieve_resources_attached_to_tag("domains", tag_key, tag_value, dynamodb_resource, audit_log_config)
                ]

            if tag_domains:
                for domain_name in tag_domains:
                    # user_permission = get_user_resource_permission(dynamodb_resource, "tags", f"{tag_key}#{tag_value}", user_id, audit_log_config)
                    user_permission = retrieve_tag_resource_access(dynamodb_resource, "domains", domain_name, tag_key, tag_value, audit_log_config)
                    rs_access = "owner" if user_permission in ["owner", "editor"] else "read-only"
                    if "_" in domain_name:
                        database_name = commonUtil.retrieve_tenant_db(
                            {"Domain": domain_name}, kwargs["DWH_DATABASE"], dynamodb_resource.Table(dynamodbUtil.TENANT_TABLE), audit_log_config
                        )
                        redshift_conn = redshiftUtil.get_redshift_connection(
                            kwargs["DWH_HOST"], kwargs["DWH_PORT"], kwargs["DWH_USER"], kwargs["DWH_PASSWORD"], database_name
                        )
                        redshiftUtil.schema_access("GRANT", domain_name, ",".join(usernames), redshift_conn, rs_access, f"{tag_key}${tag_value}")

                    else:
                        redshiftUtil.schema_access("GRANT", domain_name, ",".join(usernames), conn, rs_access, f"{tag_key}${tag_value}")

        except redshiftUtil.RedshiftTableException as rs_ex:
            ec_rs_1017 = errorUtil.get_error_object("RS-1017")
            ec_rs_1017["Message"] = rs_ex
            raise errorUtil.InvalidInputException(EVENT_INFO, ec_rs_1017)

    success_message = {"Message": "Adding members completed successfully.", "TagId": f"{tag_key}${tag_value}"}

    return commonUtil.build_post_response(200, success_message)


def validate_user_tenant_access(new_member, tag_key, tag_value, dynamodb_resource, audit_log_config):
    """
    When a user is being added to a tag, this method validates if the user has access to tenants of domains already present in the group
    Args:
        new_member (str): New member to be added to the tag
        tag_key (str): Tag key
        tag_value (str): Tag value
        dynamodb_resource: boto3 dynamodb resource
        audit_log_config: audit log configuration
    """
    LOGGER.info("In authUtil.validate_user_tenant_access, validating users %s", new_member)
    # featch domains list
    domains_list = []
    domains_list = [
        list(domain_item)[0] for domain_item in retrieve_resources_attached_to_tag("domains", tag_key, tag_value, dynamodb_resource, audit_log_config)
    ]
    tenants_list = [
        list(tenants_item)[0] for tenants_item in retrieve_resources_attached_to_tag("tenants", tag_key, tag_value, dynamodb_resource, audit_log_config)
    ]

    for domain_name in domains_list:
        if MULTI_TENANCY == "yes" and "_" in domain_name:
            domain_item = dynamodbUtil.get_item_with_key(dynamodb_resource.Table(DOMAINS_TABLE), {"DomainName": domain_name}, audit_log_config)
            tenant_name = domain_item["TenantName"]
            LOGGER.info("In authUtil.validate_user_tenant_access, found tenant domain %s", domain_name)
            if tenant_name not in tenants_list:
                # for user in new_members:
                check_user_tenant_access(domain_name, [new_member], audit_log_config, dynamodb_resource)


def validate_user_domain_access(new_members, tag_key, tag_value, dynamodb_resource, audit_log_config):
    """
    When a user is being added to a tag, this method validates if the user has access to domians of datasets/views already present in the group
    Args:
        new_members (list): List of new members to be added to the tag
        tag_key (str): Tag key
        tag_value (str): Tag value
        dynamodb_resource: boto3 dynamodb resource
        audit_log_config: audit log configuration
    """
    LOGGER.info("In authUtil.validate_user_domain_access, validating users %s", new_members)
    # fetch datasets in tag
    datasets_in_tag = [
        list(dataset_item)[0] for dataset_item in retrieve_resources_attached_to_tag("datasets", tag_key, tag_value, dynamodb_resource, audit_log_config)
    ]
    domains_in_tag = [list(dom_item)[0] for dom_item in retrieve_resources_attached_to_tag("domains", tag_key, tag_value, dynamodb_resource, audit_log_config)]
    domains_of_datasets_in_tag = []
    if datasets_in_tag:
        datasets_in_tag_details = dynamodbUtil.batch_get_items(
            dynamodb_resource, dynamodbUtil.DATASET_TABLE, [{"DatasetId": dataset_id} for dataset_id in datasets_in_tag], audit_log_config
        )
        for dataset_details in datasets_in_tag_details:
            if dataset_details.get("Domain", "") != "":
                domains_of_datasets_in_tag.append(dataset_details.get("Domain", ""))
    required_domain_access = domains_of_datasets_in_tag
    if required_domain_access:
        required_domain_access = set(required_domain_access).difference(set(domains_in_tag))
    LOGGER.info("In authUtil.validate_user_domain_access, required domain access are  %s", required_domain_access)
    for new_member in new_members:
        user_accessible_domains = retrieve_user_accessible_resources(dynamodb_resource, "domains", new_member, audit_log_config)
        user_accessible_domains = list(user_accessible_domains.keys())
        for domain_id in required_domain_access:
            if domain_id not in user_accessible_domains:
                ec_grp_1022 = errorUtil.get_error_object("TAG-1022")
                ec_grp_1022["Message"] = ec_grp_1022["Message"].format(new_member, domain_id)
                raise errorUtil.GenericFailureException(EVENT_INFO, ec_grp_1022)


def revoke_access_to_user_on_tag_resources(tag_key, tag_value, remove_users, requestor_user_id, audit_log_config, dynamodb_resource, event=None, **kwargs):
    """
    Method to revoke permissions related to tag from user
    Args:
        tag_key (str): Tag key
        tag_value (str): Tag value
        remove_user (list): list[User Id]
        requestor_user_id (str): Requestor's User Id
        audit_log_config (dict): Configuration for audit logging
        dynamodb_resource: boto3 dynamodb resource
        event (dict): event info
        kwargs: Additional arguments
    Returns:
        None
    """
    if event is None:
        event = dict()
    if isinstance(remove_users, str):
        remove_users = [remove_users]
    response = dict()
    LOGGER.info("In authUtil.revoke_access_to_user_on_tag_resources, revoking access to user %s on resources accessible to tag %s : %s", remove_users, tag_key, tag_value)
    if "lf_dataset_permissions_process" not in event:
        conn = redshiftUtil.get_redshift_connection(kwargs["DWH_HOST"], kwargs["DWH_PORT"], kwargs["DWH_USER"], kwargs["DWH_PASSWORD"], kwargs["DWH_DATABASE"])
        # Check tenant dependency
        tenant_name_set = [
            list(tenant_item)[0] for tenant_item in retrieve_resources_attached_to_tag("tenants", tag_key, tag_value, dynamodb_resource, audit_log_config)
        ]
        tag_details = {
            'TagId': f"{tag_key}#{tag_value}",
            'TenantNameList': tenant_name_set
        }
        check_tenant_dependency_on_users(tag_details, remove_users, requestor_user_id, audit_log_config, dynamodb_resource, action="update_user")
        # Check domain dependency
        tag_domain_list = [
            list(domain_item)[0] for domain_item in retrieve_resources_attached_to_tag("domains", tag_key, tag_value, dynamodb_resource, audit_log_config)
        ]
        tag_details = {"DomainNameList": tag_domain_list, "TagId": f"{tag_key}#{tag_value}"}
        user_other_means_domain_access = check_domain_dependency_on_users(
            [tag_details], remove_users, requestor_user_id, audit_log_config, dynamodb_resource, action="update_user"
        )
        # Check users have atleast one tenant before being removed from the group
        tenant_name_set = [
            list(tenant_item)[0] for tenant_item in retrieve_resources_attached_to_tag("tenants", tag_key, tag_value, dynamodb_resource, audit_log_config)
        ]
        tag_details.update({"TenantNameList": tenant_name_set})
        if tag_details.get("TenantNameList", []):
            for remove_user in remove_users:
                tenants_with_access_type = retrieve_user_accessible_resources(dynamodb_resource, "tenants", remove_user, audit_log_config)
                # user_accessible_views = set(views_with_access_type.keys())
                LOGGER.info("In authUtil.revoke_access_to_user_on_tag_resources, user tenants with access types - %s", tenants_with_access_type)
                user_tenants = list(tenants_with_access_type.keys())
                if not user_tenants:
                    # Raise an error if all the tenants are removed from the user
                    ec_dwh_1029 = errorUtil.get_error_object("DWH-1029")
                    error_message = "{}. All active tenants are removed from users profile, please re-try after repairing user metadata".format(remove_user)
                    ec_dwh_1029["Message"] = ec_dwh_1029["Message"].format(error_message)
                    raise errorUtil.GenericFailureException(EVENT_INFO, ec_dwh_1029)
                access_list = []
                LOGGER.info("In authUtil.revoke_access_to_user_on_tag_resources, user tenants with access type - %s", tenants_with_access_type)
                if len(user_tenants) == 1 and user_tenants[0] in tag_details["TenantNameList"]:
                    user_accessible_tenants = retrieve_user_accessible_resources(dynamodb_resource, "tenants", remove_user, audit_log_config)
                    for tag_id, access in user_accessible_tenants.items():
                        if tag_id != f"{tag_key}#{tag_value}":
                            access_list.append(access)
                    if not access_list:
                        LOGGER.error("In authUtil.revoke_access_to_user_on_tag_resources, revoking tenant access failed, user should atleast have one tenant attached")
                        ec_dwh_1031 = errorUtil.get_error_object("DWH-1031")
                        ec_dwh_1031["Message"] = "Cannot remove user {} access to tenant {}.".format(remove_user, user_tenants[0]) + ec_dwh_1031["Message"]
                        raise errorUtil.GenericFailureException(EVENT_INFO, ec_dwh_1031)

        response = delete_users_from_tag(
            remove_users, dynamodb_resource, USER_TABLE, conn, tag_key, tag_value, audit_log_config, user_other_means_domain_access, **kwargs
        )
        event.update({"PermissionAction": "user_removed_from_redshift_group"})
        LOGGER.info("In authUtil.revoke_access_to_user_on_tag_resources, removing group users response - %s", response)
    if "lf_dataset_permissions_process" in event or response["statusCode"] == 200:
        if event.get('lf_dataset_permissions_process', '') != 'completed':
            action = "revoke-auth-group-user-access"
            update_lf_permission(tag_key, tag_value, remove_users[0], action, dynamodb_resource, audit_log_config, event, **kwargs)

        if 'lf_dataset_permissions_process' in event and event.get('lf_dataset_permissions_process', '') != 'completed':
            return
        else:
            event.update({"PermissionAction": "user_revoked_lf_permissions"})

        # Update user profile information if any tenants exist in the group
        tenant_resources = [
            list(tenant_item)[0] for tenant_item in retrieve_resources_attached_to_tag("tenants", tag_key, tag_value, dynamodb_resource, audit_log_config)
        ]
        if tenant_resources:
            update_tenant_user_profile(
                remove_users, tenant_resources, dynamodb_resource, USER_TABLE, kwargs["ADD_FUNC_ARGS_DICT"], "Detach", requestor_user_id
            )
        event.update({"PermissionAction": "updated_tenant_profile"})

        for user_id in remove_users:
            update_dashboard_permissions("revoke", dynamodb_resource, tag_key, tag_value, user_id, event, audit_log_config)
        event.update({"PermissionAction": "updated_qs_dashboards"})
    elif response.get("statusCode") != 200:
        raise Exception("Failed to update redshift group")
    LOGGER.info("In authUtil.revoke_access_to_user_on_tag_resources, exiting method.")


def delete_users_from_tag(members_info, dynamodb_resource, user_table, conn, tag_key, tag_value, audit_log_config, user_other_means_domain_access, **kwargs):
    """
    This is the main function to delete users from tag
    Args:
        members_info: list of users
        dynamodb_resource: boto3 dynamodb resource
        user_table: user table name
        conn: redshift connection
        tag_key: tag key
        tag_value: tag value
        audit_log_config: audit log configuration
        user_other_means_domain_access: user other means domain access
        kwargs: additional arguments
    Returns:
        None
    """
    LOGGER.info("In authUtil.delete_users_from_tag, Deleting users from tag")

    user_list = commonUtil.valid_user_list(members_info, dynamodb_resource.Table(user_table), audit_log_config)
    if not user_list["valid_users"]:
        success_message = {
            "Message": "No valid users to remove, skipping the process.",
            "GroupId": f"{tag_key}${tag_value}",
            "Invalid_Users": user_list["invalid_users"],
        }
        return commonUtil.build_put_response(200, success_message)
    else:
        remove_members = user_list["valid_users"]


    # Remove users from DWH group
    LOGGER.info("In authUtil.delete_users_from_tag, Removing members in DWH group")
    dwh_members_remove = []
    for i in remove_members:
        user_details = commonUtil.get_userdetails(i, user_table, dynamodb_resource, audit_log_config)
        dwh_members_remove.append(user_details["UserName"])

    if kwargs["DATALAKE_DWH"] == "redshift":
        redshiftUtil.remove_users_in_redshift_group(f"{tag_key}${tag_value}", ",".join(dwh_members_remove), conn)
        try:
            role_name = redshiftUtil.get_tag_redshift_role_name(tag_key, tag_value)
            redshiftUtil.revoke_redshift_role_from_users(role_name, dwh_members_remove, conn)
        except redshiftUtil.RedshiftTableException as rs_ex:
            ec_rs_1017 = errorUtil.get_error_object("RS-1017")
            ec_rs_1017["Message"] = rs_ex
            raise errorUtil.InvalidInputException(EVENT_INFO, ec_rs_1017)
        tag_domains = [
            list(domain_item)[0] for domain_item in retrieve_resources_attached_to_tag("domains", tag_key, tag_value, dynamodb_resource, audit_log_config)
        ]
        if tag_domains:
            for domain_name in tag_domains:
                # Make sure that users having access to domains only through this group are revoked access
                current_domain_user_removal_list = dwh_members_remove
                if user_other_means_domain_access.get(domain_name, []):
                    users_rs_names = []
                    for user_id in user_other_means_domain_access[domain_name]:
                        users_item = commonUtil.get_userdetails(user_id, user_table, dynamodb_resource, audit_log_config)
                        users_rs_names.append(users_item["UserName"])
                        LOGGER.info("users_rs_names == %s", users_rs_names)
                    current_domain_user_removal_list = set(dwh_members_remove) - set(users_rs_names)
                try:
                    user_permission = retrieve_tag_resource_access(dynamodb_resource, "domains", domain_name, tag_key, tag_value, audit_log_config)
                    rs_access = "owner" if user_permission in ["owner", "editor"] else "read-only"
                    if current_domain_user_removal_list:
                        if "_" in domain_name:
                            database_name = commonUtil.retrieve_tenant_db(
                                {"Domain": domain_name}, kwargs["DWH_DATABASE"], dynamodb_resource.Table(dynamodbUtil.TENANT_TABLE), audit_log_config
                            )
                            redshift_conn = redshiftUtil.get_redshift_connection(
                                kwargs["DWH_HOST"], kwargs["DWH_PORT"], kwargs["DWH_USER"], kwargs["DWH_PASSWORD"], database_name
                            )
                            redshiftUtil.schema_access(
                                "REVOKE", domain_name, ",".join(current_domain_user_removal_list), redshift_conn, rs_access, f"{tag_key}${tag_value}"
                            )
                        else:
                            redshiftUtil.schema_access(
                                "REVOKE", domain_name, ",".join(current_domain_user_removal_list), conn, rs_access, f"{tag_key}${tag_value}"
                            )
                except redshiftUtil.RedshiftTableException as rs_ex:
                    ec_rs_1017 = errorUtil.get_error_object("RS-1017")
                    ec_rs_1017["Message"] = rs_ex
                    raise errorUtil.InvalidInputException(EVENT_INFO, ec_rs_1017)

    success_message = {"Message": "Removing members completed successfully.", "GroupId": f"{tag_key}${tag_value}", "MembersRemoved": remove_members}
    # if invalid_remove_members:
    #     success_message["message"] = "Removing members completed successfully with valid users & filtered invalid users"
    #     success_message["Invalid_Users"] = invalid_remove_members
    # # send notifications to subscribed users. only if a user got removed.
    # if remove_members:
    #     alert_obj = {
    #         "GroupName": dynamo_resp["GroupName"],
    #         "ProviderUserId": user_id,
    #         "ToUserIdList": remove_members,
    #         "AccessType": dynamo_resp["GroupType"].lower(),
    #         "Operation": "revoke",
    #         "USER_TABLE": dynamo_resp["USER_TABLE"],
    #         "NOTIFICATIONS_INDEX_NAME": dynamo_resp["NOTIFICATIONS_INDEX_NAME"],
    #         "NOTIFICATIONS_TABLE": dynamo_resp["NOTIFICATIONS_TABLE"],
    #         "ENVIRONMENT": dynamo_resp["ENVIRONMENT"],
    #         "PROJECT_SHORTNAME": dynamo_resp["PROJECT_SHORTNAME"],
    #         "EMAIL_FROM": dynamo_resp["EMAIL_FROM"]
    #     }
    #     for dataset_id in dynamo_resp.get("DatasetList", []):
    #         dataset_detail = dynamodbUtil.get_item_with_key(dynamodb.Table(dynamo_resp["DATASET_TABLE"]), {
    #             'DatasetId': dataset_id}, audit_log_config)
    #         alert_obj.update({
    #             "ResourceId": dataset_id,
    #             "ResourceName": "{} ({})".format(dataset_detail["DatasetName"], dataset_detail["Domain"]),
    #             "ResourceType": "Dataset"
    #         })
    #         send_alert(dynamodb, alert_obj, audit_log_config)
    #     for job_id in dynamo_resp.get("JobIdList", []):
    #         alert_obj.update({
    #             "ResourceId": job_id,
    #             "ResourceName": dynamodbUtil.get_item_with_key(dynamodb.Table(dynamo_resp["JOBS_TABLE"]), {'Id': job_id}, audit_log_config)["JobName"],
    #             "ResourceType": "Job"
    #         })
    #         send_alert(dynamodb, alert_obj, audit_log_config)
    #     for dashboard_id in dynamo_resp.get("DashboardList", []):
    #         alert_obj.update({
    #             "ResourceId": dashboard_id,
    #             "ResourceName": dynamodbUtil.get_item_with_key(dynamodb.Table(dynamo_resp["DASHBOARD_TABLE"]), {'DashboardId': dashboard_id}, audit_log_config)["DashboardName"],
    #             "ResourceType": "Dashboard"
    #         })
    #         send_alert(dynamodb, alert_obj, audit_log_config)
    #     for schedule_id in dynamo_resp.get("ScheduleIdList", []):
    #         alert_obj.update({
    #             "ResourceId": schedule_id,
    #             "ResourceName": dynamodbUtil.get_item_with_key(dynamodb.Table(dynamo_resp["SCHEDULES_TABLE_NAME"]), {'ScheduleId': schedule_id}, audit_log_config)["JobName"],
    #             "ResourceType": "Schedule"
    #         })
    #         send_alert(dynamodb, alert_obj, audit_log_config)

    return commonUtil.build_put_response(200, success_message)

def check_tenant_dependency_on_users(tag_details, users_list, requestor_user_id, audit_log_config, dynamodb_resource, action=""):
    """
    This method validates if a user has access to domain under a tenant, then the user has the access to tenant
    """
    LOGGER.info("In authUtil.check_tenant_dependency_on_users method, with tag details %s", tag_details)
    tenant_name_set = list(tag_details.get("TenantNameList", []))
    tag_key = tag_details.get('TagId', '').split('#')[0]
    tag_value = tag_details.get('TagId', '').split('#')[-1]

    LOGGER.info("In authUtil.check_tenant_dependency_on_users method, tenant names list is %s", tenant_name_set)
    for tenant_name in tenant_name_set:
        tags_with_tenant_access = list_authorized_entities_for_resource(
            dynamodb_resource, "tenants", tenant_name, commonUtil.SYSTEM_RUNNER_ID, audit_log_config
        )
        tags_or_users_with_tenant_access = [f"{tag_item['TagKey']}#{tag_item['TagValue']}" for _ , tags_list  in tags_with_tenant_access.items() for tag_item in tags_list]
        for a_user in users_list:

            if f"{tag_key}#{tag_value}" in tags_or_users_with_tenant_access:
                tags_or_users_with_tenant_access.remove(f"{tag_key}#{tag_value}")
            users_with_access = []
            for tag_name in tags_or_users_with_tenant_access:
                # fetch tag users
                tag_item_key = tag_name.split('#')[0]
                if tag_item_key != "user":
                    users_attached_to_tag = retrieve_users_attached_to_resource(dynamodb_resource, "tags", tag_name, requestor_user_id, audit_log_config).get("UsersAttached", [])
                    users_with_access.extend(users_attached_to_tag)
                else:
                    users_with_access.append(tag_name.split("#")[-1])

            user_has_access = False
            if a_user in users_with_access:
                user_has_access = True


            if user_has_access:
                LOGGER.info("In authUtil.check_tenant_dependency_on_users method, %s has access to tenant through other tags", a_user)
            else:
                # Retrieve domains in each tenant, validate if there are any user resources under the domain
                tenant_domains = retrieve_tenant_domains(tenant_name, dynamodb_resource, audit_log_config)
                LOGGER.info("In authUtil.check_tenant_dependency_on_users method, tenant domains are - %s", tenant_domains)
                if tenant_domains:
                    if action in ["update_user", "delete_group"]:
                        for domain_details in tenant_domains:
                            authorized_users_and_tags = list_authorized_entities_for_resource(
                                dynamodb_resource, "domains", domain_details.get("DomainName"), requestor_user_id, audit_log_config
                            )
                            authorised_users = [
                                tag_item["TagValue"]
                                for _, tag_list in authorized_users_and_tags.items()
                                for tag_item in tag_list
                                if tag_item["TagKey"] == "user"
                            ]
                            for authorised_user in authorised_users:
                                # check if user is has individual access to a domain under the tenant
                                if authorised_user == a_user:
                                    ec_grp_1021 = errorUtil.get_error_object("TAG-1021")
                                    ec_grp_1021["Message"] = "Failed to remove user {}'s access to tenant {}, user has access to domain in tenant".format(
                                        a_user, tenant_name
                                    )
                                    raise errorUtil.GenericFailureException(EVENT_INFO, ec_grp_1021)
                            authorised_tags = [
                                tag_item["TagKey"] + "#" + tag_item["TagValue"]
                                for _, tag_list in authorized_users_and_tags.items()
                                for tag_item in tag_list
                                if tag_item["TagKey"] != "user"
                            ]
                            # authorised_groups = authorized_users_and_groups.get("groups",{}).get("owners",[]) + authorized_users_and_groups.get("groups",{}).get("read-only",[])
                            for authorised_tag in authorised_tags:
                                # check if user has access to the domain via any other groups
                                tag_users = list_authorized_entities_for_resource(
                                    dynamodb_resource, "tags", authorised_tag, requestor_user_id, audit_log_config
                                )
                                tag_users_list = [
                                    tag_item["TagValue"] for _, tag_list in tag_users.items() for tag_item in tag_list if tag_item["TagKey"] == "user"
                                ]
                                if authorised_tag != f"{tag_key}#{tag_value}" and a_user in tag_users_list:
                                    ec_grp_1021 = errorUtil.get_error_object("TAG-1021")
                                    ec_grp_1021["Message"] = "Failed to remove user {}'s access to tenant {}, user has access to domain in tenant".format(
                                        a_user, tenant_name
                                    )
                                    raise errorUtil.GenericFailureException(EVENT_INFO, ec_grp_1021)
                    else:
                        tag_details = {
                            "DomainNameList": [item["DomainName"] for item in tenant_domains if "DomainName" in item and item["DomainName"]],
                            "TagId": f"{tag_key}#{tag_value}",
                        }
                        try:
                            check_domain_dependency_on_users([tag_details], [a_user], requestor_user_id, audit_log_config, dynamodb_resource)
                            # check user accessible domains under the tenant. This is to validate if user has any
                            # domains attached but doesnot have any resources underneath it
                            LOGGER.info("In authUtil.check_tenant_dependency_on_users method, no resources found under domains")
                            for tenant_domain in tag_details["DomainNameList"]:
                                user_permission = get_user_resource_permission(dynamodb_resource, "domains", tenant_domain, a_user, audit_log_config)
                                LOGGER.info(
                                    "In authUtil.check_tenant_dependency_on_users method, user - %s has - %s permission on tenant domain - %s",
                                    a_user,
                                    user_permission,
                                    tenant_domain,
                                )
                                # If user permission exist we throw an error because the tenant access is about to be removed
                                if user_permission:
                                    ec_grp_1021 = errorUtil.get_error_object("TAG-1021")
                                    ec_grp_1021["Message"] = "Failed to remove user {}'s access to tenant {}, user has access to domain in tenant".format(
                                        a_user, tenant_name
                                    )
                                    raise errorUtil.GenericFailureException(EVENT_INFO, ec_grp_1021)
                                else:
                                    LOGGER.info("In authUtil.check_tenant_dependency_on_users method, no resources found under tenant")
                        except Exception as ex:
                            if re.match("(.*) user has access to (.*) in domain", str(ex)):
                                # Add additional response to the error message for the user
                                raise Exception(
                                    "{}. Please revoke all dependent resources and domain access first to revoke tenant access".format(str(ex))
                                ) from ex
                            raise ex


def get_datasets_list(user_id, dynamodb_res, audit_log_config, remove_external_datasets=False, action=""):
    """
    Return list of user dataset details
    :param dataset_table_name:
    :param audit_log config:
    :param remove_external_dataset: flag to remove external datasets from response
    :return: list(dictionary_object)
    """

    LOGGER.info("In authUtil.get_datasets_list, Retrieving list of authorized datasets for the user %s", user_id)
    dataset_list = {"Owner": [], "Editor": [], "ReadOnly": []}
    datasets_dict = retrieve_user_accessible_resources(dynamodb_res, "datasets", user_id, audit_log_config, action != "domain_access")
    user_dataset_ids = set(datasets_dict.keys())
    # Adding dataset details to the result
    projection_expression = "DatasetName,DatasetId,IsActive,#d,DatasetType"
    expression_att_names = {"#d": "Domain"}
    response_items = dynamodbUtil.batch_get_items(
        dynamodb_res,
        dynamodbUtil.DATASET_TABLE,
        [{"DatasetId": dataset_id} for dataset_id in user_dataset_ids],
        audit_log_config,
        projection_expression,
        expression_att_names,
    )
    dataset_details = {}
    for item in response_items:
        if item:
            dataset_details[item["DatasetId"]] = item
    # Preparing dataset list with access and dataset metadata
    invalid_datasets = []
    for dataset_id, dataset_item in dataset_details.items():
        uad_item = {}
        if remove_external_datasets and dataset_item and dataset_item.get("DatasetType", "internal") == "external":
            continue
        if dataset_item and dataset_item.get("IsActive", "no") == "yes":
            LOGGER.info("In authUtil.get_datasets_list, UserDataset item: %s", dataset_item)
            uad_item["DatasetName"] = dataset_item["DatasetName"]
            uad_item["DatasetId"] = dataset_item["DatasetId"]
            uad_item["Domain"] = dataset_item["Domain"]
            if datasets_dict[dataset_id].lower() == "owner" and uad_item["DatasetId"] not in [d_item["DatasetId"] for d_item in dataset_list["Owner"]]:
                dataset_list["Owner"].append(uad_item)
            elif datasets_dict[dataset_id].lower() == "read-only" and uad_item["DatasetId"] not in [d_item["DatasetId"] for d_item in dataset_list["ReadOnly"]]:
                dataset_list["ReadOnly"].append(uad_item)
            elif datasets_dict[dataset_id].lower() == "editor" and uad_item["DatasetId"] not in [d_item["DatasetId"] for d_item in dataset_list["Editor"]]:
                dataset_list["Editor"].append(uad_item)
        else:
            invalid_datasets.append({"DatasetId": dataset_id, "AccessType": datasets_dict[dataset_id]})
    LOGGER.info("In authUtil.get_datasets_list, Retrieved the list of dataset access. InActive/Invalid datasets: %s", invalid_datasets)
    return dataset_list, invalid_datasets


# pylint: disable=too-many-locals, import-outside-toplevel
def check_domain_dependency_on_users(tags_details, users_list, requestor_user_id, audit_log_config, dynamodb_resource, action=""):
    """
    This method is used to test whether the user has domain datasets and views associated
    """
    LOGGER.info("In authUtil.check_domain_dependency_on_users method")
    domain_names_set = set()
    tag_ids = []
    tag_details_list = tags_details.copy()
    for tag_details in tags_details:
        domain_names_set = domain_names_set.union(tag_details.get("DomainNameList", set()))
        tag_ids.append(tag_details.get("TagId"))
    LOGGER.info("In authUtil.check_domain_dependency_on_users method, domain names list is %s", domain_names_set)
    # consists of user list for which users have access to domain from other groups
    user_other_means_domain_access = {}
    # check if the user has to resources in this domain through other means
    # get the dataset, view access to see if the user has access to it
    # if he has access to it and it is also through other means
    # then let the operation complete gracefully else throw exception
    # pylint: disable=too-many-nested-blocks
    for domain_name in domain_names_set:
        # CLOUD-2549 - Checking if the DLA provided for group and ignoring the domain dependency check in the next steps
        for tag_item in tag_details_list:
            tag_id = tag_item["TagId"]
            sort_key_prefix = f"domains#{tag_id}#"
            key_condition_expression = Key("ResourceId").eq(domain_name) & Key("TagAccessKey").begins_with(sort_key_prefix)
            acl_response = dynamodbUtil.get_items_by_query(dynamodb_resource.Table(ACL_RESOURCES_TABLE), key_condition_expression, None, audit_log_config)
            tag_domain_item = acl_response[0] if acl_response else {}
            is_dla_provided = tag_domain_item.get("AdditionalMetadata", {}).get("IsDatasetLevelAccessProvided", False)
            # Only check domain_dependency_on_users if it domain access is not from DLA
            LOGGER.info("In authUtil.check_domain_dependency_on_users, Checking whether group domain access is from Dataset Level Access or not")

            if not is_dla_provided or action in ["domain_access", "update_user"]:
                LOGGER.info(
                    "In authUtil.check_domain_dependency_on_users, Group domain doesn't have Dataset Level Access, So proceeding with dependency checks"
                )
                tags_with_domain_access = list_authorized_entities_for_resource(
                    dynamodb_resource, "domains", domain_name, commonUtil.SYSTEM_RUNNER_ID, audit_log_config
                )
                tags_or_users_with_domain_access = [f"{tag_item['TagKey']}#{tag_item['TagValue']}" for _ , tags_list  in tags_with_domain_access.items() for tag_item in tags_list]
                for a_user in users_list:

                    if tag_id in tags_or_users_with_domain_access:
                        tags_or_users_with_domain_access.remove(tag_id)
                    users_with_access = []
                    for tag_name in tags_or_users_with_domain_access:
                        # fetch tag users
                        tag_item_key = tag_name.split('#')[0]
                        if tag_item_key != "user":
                            users_attached_to_tag = retrieve_users_attached_to_resource(dynamodb_resource, "tags", tag_name, requestor_user_id, audit_log_config).get("UsersAttached", [])
                            users_with_access.extend(users_attached_to_tag)
                        else:
                            users_with_access.append(tag_name.split("#")[-1])

                    user_has_access = False
                    if a_user in users_with_access:
                        user_has_access = True

                    if user_has_access:
                        LOGGER.info(
                            "In authUtil.check_domain_dependency_on_users method,\
                            user %s has access to domain through other means",
                            a_user,
                        )
                        current_domain_users_list = user_other_means_domain_access.get(domain_name, [])
                        LOGGER.info("In authUtil.check_domain_dependency_on_users method, current domain users list - %s", current_domain_users_list)
                        current_domain_users_list.append(a_user)
                        user_other_means_domain_access.update({domain_name: current_domain_users_list})
                    else:
                        # Check if the user has any datasets or views in domain.
                        user_dataset_details, _ = get_datasets_list(a_user, dynamodb_resource, audit_log_config, False)
                        LOGGER.info("In authUtil.check_domain_dependency_on_users method, user dataset details %s", user_dataset_details)
                        # Get the domains of datasets that are accessible by users
                        user_dataset_domains = set(
                            [dataset_details["Domain"] for dataset_details in user_dataset_details.get("Owner", [])]
                            + [dataset_details["Domain"] for dataset_details in user_dataset_details.get("Editor", [])]
                            + [dataset_details["Domain"] for dataset_details in user_dataset_details.get("ReadOnly", [])]
                        )
                        if domain_name not in user_dataset_domains:
                            LOGGER.info("In authUtil.check_domain_dependency_on_users method, user has no access on datasets in domain")
                        else:
                            # when user action is update_user or delete_group and user has access to datasets in domain, we need to check where the access is from.
                            # when a_user does not have other means of access to a domain, he can have access to a dataset/view in the domain from 3 places
                            # 1) access to domain from group and individual access to a dataset/view (Throw exception in this case)
                            # 2) access to domain from one group and access to domain/view from another group (Throw exception in this case
                            # 3) access to both domian and dataset/view from the same group (Pass this condition)
                            if action in ["update_user", "delete_group"]:
                                users_datasets_in_domain = [
                                    dataset_details
                                    for dataset_details in user_dataset_details.get("Owner", [])
                                    if dataset_details.get("Domain", "") == domain_name
                                ]
                                users_datasets_in_domain += [
                                    dataset_details
                                    for dataset_details in user_dataset_details.get("Editor", [])
                                    if dataset_details.get("Domain", "") == domain_name
                                ]
                                users_datasets_in_domain += [
                                    dataset_details
                                    for dataset_details in user_dataset_details.get("ReadOnly", [])
                                    if dataset_details.get("Domain", "") == domain_name
                                ]
                                for dataset_details in users_datasets_in_domain:
                                    # authorized_users_and_groups = get_authorized_users_on_dataset(dataset_details.get("DatasetId"), audit_log_config, dynamodb_resource)
                                    authorized_users_and_tags = list_authorized_entities_for_resource(
                                        dynamodb_resource, "datasets", dataset_details.get("DatasetId"), commonUtil.SYSTEM_RUNNER_ID, audit_log_config
                                    )
                                    if authorized_users_and_tags:
                                        # authorised_users = authorized_users_and_groups.get("users", {}).get("owners", []) + authorized_users_and_groups.get("users", {}).get("read-only", [])
                                        authorised_users = [
                                            tag_item["TagValue"]
                                            for access in authorized_users_and_tags
                                            for tag_item in authorized_users_and_tags[access]
                                            if tag_item["TagKey"] == "user"
                                        ]
                                        for authorised_user in authorised_users:
                                            # check if user is has individual access to a dataset in the domain
                                            if authorised_user == a_user:
                                                ec_grp_1020 = errorUtil.get_error_object("TAG-1020")
                                                ec_grp_1020["Message"] = (
                                                    "Failed to remove user {}'s access to domain {}, user has access to dataset in domain".format(
                                                        a_user, domain_name
                                                    )
                                                )
                                                raise errorUtil.GenericFailureException(EVENT_INFO, ec_grp_1020)
                                        # authorised_groups = authorized_users_and_tags.get("groups",{}).get("owners",[]) + authorized_users_and_tags.get("groups",{}).get("read-only",[])
                                        authorised_tags = [
                                            tag_item["TagKey"] + "#" + tag_item["TagValue"]
                                            for access in authorized_users_and_tags
                                            for tag_item in authorized_users_and_tags[access]
                                            if tag_item["TagKey"] != "user"
                                        ]
                                        for authorised_tag in authorised_tags:
                                            # check if user has access to this dataset via any other groups
                                            users_attached = retrieve_users_attached_to_resource(
                                                dynamodb_resource, "tags", authorised_tag, commonUtil.SYSTEM_RUNNER_ID, audit_log_config
                                            ).get("UsersAttached", [])
                                            if authorised_tag not in tag_ids and a_user in users_attached:
                                                ec_grp_1020 = errorUtil.get_error_object("TAG-1020")
                                                ec_grp_1020["Message"] = (
                                                    "Failed to remove user {}'s access to domain {}, user has access to dataset in domain".format(
                                                        a_user, domain_name
                                                    )
                                                )
                                                raise errorUtil.GenericFailureException(EVENT_INFO, ec_grp_1020)
                            else:
                                # when user action is other than update user or delete a group (like update resources),
                                # we raise an exception if user has access to any dataset under a domain
                                # the access can be from anywhere like individual access to dataset/ access to dataset and domain
                                # from same group/ access to dataset and domain from different group
                                ec_grp_1020 = errorUtil.get_error_object("TAG-1020")
                                ec_grp_1020["Message"] = "Failed to remove user {}'s access to domain {}, user has access to dataset in domain".format(
                                    a_user, domain_name
                                )
                                raise errorUtil.GenericFailureException(EVENT_INFO, ec_grp_1020)

    LOGGER.info("In authUtil.check_domain_dependency_on_users method, exiting, with %s", user_other_means_domain_access)
    return user_other_means_domain_access


def delete_resource(dynamodb_resource, resource_id: str, audit_log_config: dict) -> None:
    """
    This method is used to remove resource details from access controls table
    Args:
        dynamodb_resource: boto3 dynamodb resource
        resource_id (str): UUID of the resource
        audit_log_config (dict): Configuration for audit logging
    Returns:
        None
    """
    acl_items = dynamodbUtil.get_items_by_query(dynamodb_resource.Table(ACL_RESOURCES_TABLE), Key("ResourceId").eq(resource_id), "ResourceId, TagAccessKey", audit_log_config)
    LOGGER.info("In accessUtil.delete_resource, deleting %s items from access control table", len(acl_items))
    dynamodbUtil.batch_delete_items(dynamodb_resource.Table(ACL_RESOURCES_TABLE), acl_items, audit_log_config)


def last_auth_check(dynamodb_resource, resource_type: str, resource_id: str, tag_key: str, tag_value: str,  audit_log_config: dict) -> bool:
    """
    This method ensures that during any access update there is
    always at least one authorized entity(user/tag) with owner access on a resource

    Args:
        dynamodb_resource: boto3 dynamodb resource
        resource_type(str): type of the resource
        resource_id (str): UUID of the resource
        tag_key (str): Tag key that is being updated
        tag_value (str): Tag value that is being updated
        audit_log_config (dict): Configuration for audit logging

    Returns:
        bool: True if tag_key:tag_value is the last owner, False otherwise
    """
    LOGGER.info("In accessUtil.last_auth_check, checking if resource %s has only one owner", resource_id)
    acl_response = dynamodbUtil.get_items_by_query(
        dynamodb_resource.Table(ACL_RESOURCES_TABLE),
        Key("ResourceId").eq(resource_id),
        "TagAccessKey",
        audit_log_config,
    )
    owner_access_key = f"{resource_type}#{tag_key}#{tag_value}#{AccessType.OWNER.label}"
    tag_access_keys_list = [item["TagAccessKey"] for item in acl_response]
    number_of_owners = sum(1 for tag in tag_access_keys_list if tag.endswith(f"{AccessType.OWNER.label}"))
    if (number_of_owners == 1) and owner_access_key in tag_access_keys_list:
        return True

    return False


def segregate_access_details(tag_access_keys_list: list) -> dict:
    """
    Processes a list of tag access keys to segregate users and tags as per the access type.

    Each input string is expected to be in the format:
    <resource_type>#<tag_key>#<tag_value>#<access_type>

    Args:
        dynamodb_resource: boto3 dynamodb resource
        tag_access_keys_list: List of tag access keys
        audit_log_config: DynamoDB audit log configuration

    Returns:
        dict: A dictionary containing user and tag details organized by access type.
              The structure is as follows:
              {
                "Owner": [
                    {
                        "TagKey": "string",
                        "TagValue": "string"
                    }
                ],
                "Editor": [],
                "Read-only": []
              }
    """
    result = {access_type.label.capitalize(): [] for access_type in AccessType if access_type != AccessType.NONE}

    # Extract and map tag key-value pairs to their access types
    for tag_access_key in tag_access_keys_list:
        parts = tag_access_key.split("#")
        tag_key = parts[1]
        tag_value = parts[2]
        access_type_str = parts[3]

        access_type = AccessType.from_label(access_type_str)
        if access_type == AccessType.NONE:
            continue  # Skip if access type is invalid

        result[access_type.label.capitalize()].append({"TagKey": tag_key, "TagValue": tag_value})

    return result


def check_user_tenant_access(domain_name, users_list, audit_log_config, dynamodb_resource, return_permission=False):
    """
    This method is used to check if the user has access to tenant of domain
    Note : domain name passed to this method should always be of the format <tenant_name>_<domain_name>
    Args:
        domain_name (str): Domain name
        requestor_id (str): User Id
        audit_log_config (dict): Configuration for audit logging
        dynamodb_resource: boto3 dynamodb resource

    Returns:
        None
    """
    domain_item = dynamodbUtil.get_item_with_key(dynamodb_resource.Table(dynamodbUtil.DOMAIN_TABLE), {"DomainName": domain_name}, audit_log_config)
    database_name = domain_item["TenantName"]
    key = {"TenantName": database_name}
    tenant_item = dynamodbUtil.get_item_with_key(dynamodb_resource.Table(dynamodbUtil.TENANT_TABLE), key, audit_log_config)
    if not tenant_item:
        ec_rs_1020 = errorUtil.get_error_object("RS-1020")
        ec_rs_1020["Message"] = ec_rs_1020["Message"].format(database_name)
        raise errorUtil.InvalidInputException(EVENT_INFO, ec_rs_1020)
    # Check user's tenant permission
    for user_id in users_list:
        LOGGER.info("In authUtil.check_user_tenant_access method, with requestor id %s", user_id)
        user_tenant_permission = get_user_resource_permission(dynamodb_resource, "tenants", database_name, user_id, audit_log_config)
        if return_permission:
            return user_tenant_permission, database_name
        if not user_tenant_permission:
            LOGGER.error("In authUtil.check_user_tenant_access method, permission retrieved for tenant is %s", user_tenant_permission)
            ec_auth_1010 = errorUtil.get_error_object("AUTH-1010")
            ec_auth_1010["Message"] = "User {} doesn't have access to tenant {}. Please provide tenant access before sharing the domain {}".format(
                user_id, database_name, domain_name
            )
            raise errorUtil.InvalidInputException(EVENT_INFO, ec_auth_1010)
    LOGGER.info("In authUtil.check_user_tenant_access method, exiting")


@validate_resource_type
def check_user_domain_access(
    domain_name: str, resource_name: str, users_list: str, resource_type: str, audit_log_config: dict, dynamodb_resource, is_domain_access_requested=False
) -> None:
    """
    This method is used to check if the user has access to resource domain
    Args:
        domain_name (str): Domain name
        resource_name (str): Resource name
        users_list (str): List of users
        resource_type (str): Type of resource
        audit_log_config (dict): Configuration for audit logging
        dynamodb_resource: boto3 dynamodb resource
        is_domain_access_requested: boolean
    Returns:
        None
    """
    for user_id in users_list:
        LOGGER.info("In authUtil.check_user_domain_access method, with user id %s", user_id)
        if MULTI_TENANCY == "yes" and "_" in domain_name:
            user_tenant_permission, database_name = check_user_tenant_access(domain_name, [user_id], audit_log_config, dynamodb_resource, True)
            if not user_tenant_permission and not is_domain_access_requested:
                LOGGER.error("In authUtil.check_user_domain_access method, permission retrieved for tenant is %s", user_tenant_permission)
                ec_auth_1010 = errorUtil.get_error_object("AUTH-1010")
                ec_auth_1010["Message"] = "User {} doesn't have access to tenant {}. Please provide tenant access before sharing the domain {}".format(
                    user_id, database_name, domain_name
                )
                raise errorUtil.InvalidInputException(EVENT_INFO, ec_auth_1010)

        user_permission = get_user_resource_permission(dynamodb_resource, "domains", domain_name, user_id, audit_log_config)
        if not user_permission:
            LOGGER.error("In authUtil.check_user_domain_access method, permission retrieved is %s", user_permission)
            ec_auth_1010 = errorUtil.get_error_object("AUTH-1010")
            ec_auth_1010["Message"] = "User {} doesn't have access to domain {} of {} {}".format(user_id, domain_name, resource_type, resource_name)
            raise errorUtil.InvalidInputException(EVENT_INFO, ec_auth_1010)
    LOGGER.info("In authUtil.check_user_domain_access method, exiting")
    return True


# def validate_user_tenant_access(users_list, domains_list, dynamodb_resource, audit_log_config):
#     """
#     When a user/tag is being added to a domain, this method validates if the user has access to tenant of domain
#     :dynamodb_resource
#     :audit_log_config
#     """
#     LOGGER.info("In authUtil.validate_user_tenant_access, validating user %s", users_list)
#     for domain_name in domains_list:
#         if MULTI_TENANCY == "yes" and "_" in domain_name:
#             domain_item = dynamodbUtil.get_item_with_key(dynamodb_resource.Table(dynamodbUtil.DOMAIN_TABLE), {"DomainName": domain_name}, audit_log_config)
#             tenant_name = domain_item["TenantName"]
#             LOGGER.info(
#                 "In authUtil.validate_user_tenant_access, found tenant domain %s with tenant %s",
#                 domain_name,
#                 tenant_name,
#             )
#             for user_id in users_list:
#                 check_user_tenant_access(domain_name, [user_id], audit_log_config, dynamodb_resource)
#     LOGGER.info("In authUtil.validate_user_tenant_access method, exiting")


@validate_resource_type
def validate_users_domain_access(users_list: list, resource_type: str, resource_ids_list: list, dynamodb_resource, audit_log_config: dict) -> None:
    """
    When a user is being added to a tag, this method validates if the user has access to domians of datasets/views already present in the tag
    Args:
        users_list (list): List of users
        resource_type (str): Type of resource
        resource_ids_list (list): List of resource ids
        dynamodb_resource: boto3 dynamodb resource
        audit_log_config (dict): Configuration for audit logging

    Returns:
        None
    """
    LOGGER.info("In authUtil.validate_user_domain_access, validating users %s", users_list)
    required_domain_access = []
    if resource_type == "datasets":
        datasets_in_group_details = dynamodbUtil.batch_get_items(
            dynamodb_resource,
            dynamodbUtil.DATASET_TABLE,
            [{"DatasetId": dataset_id} for dataset_id in resource_ids_list],
            audit_log_config,
        )
        for dataset_details in datasets_in_group_details:
            if dataset_details.get("Domain", "") != "":
                required_domain_access.append(dataset_details.get("Domain", ""))

    LOGGER.info("In authUtil.validate_user_domain_access, required domain access are  %s", required_domain_access)
    # when adding a user to a group, we need to check if user will be getting access to required_domain_access domains from the group
    # if not then the user should have access to these domains by any other means
    for user_id in users_list:
        user_accessible_domains = retrieve_user_accessible_resources(dynamodb_resource, "domains", user_id, audit_log_config)
        user_accessible_domains = list(user_accessible_domains.keys())
        for domain_id in required_domain_access:
            if domain_id not in user_accessible_domains:
                ec_grp_1022 = errorUtil.get_error_object("TAG-1022")
                ec_grp_1022["Message"] = ec_grp_1022["Message"].format(user_id, domain_id)
                raise errorUtil.GenericFailureException(EVENT_INFO, ec_grp_1022)


def extract_underlying_datasets(sql_statement: str, dynamodb_resource, dataset_table: str, audit_log_config: dict) -> dict:
    """
    Extract underlying datasets inside a sql statement
    Args:
        sql_statement (str): SQL statement
        dynamodb_resource: boto3 dynamodb resource
        dataset_table (str): Dataset table name
        audit_log_config (dict): Configuration for audit logging

    Returns:
        dict: Dictionary of dataset ids and names
    """
    filter_expression = Attr("TargetLocation").eq(commonUtil.TARGET_LOCATION_MAP["lf"]) & Attr("RegistrationStatus").eq("completed")
    list_of_datasets = dynamodbUtil.scan_with_pagination(
        dynamodb_resource.Table(dataset_table), audit_log_config, filter_expression, "DatasetName, DatasetId", None
    )
    LOGGER.info("In authUtil.extract_underlying_datasets, list of datasets read - %s", list_of_datasets)
    datasets_original_and_lower_case_dict, dataset_id_dict = {}, {}
    # Create a dict of dataset names original and lower case
    for dataset_item in list_of_datasets:
        datasets_original_and_lower_case_dict[dataset_item["DatasetName"].lower()] = (
            dataset_item["DatasetName"],
            dataset_item["DatasetId"],
        )
    list_of_strings_after_splitting_sql_by_white_spaces = sql_statement.split()
    # Check if dataset from query matches with lower case existing datasets if yes
    # get the name of the original dataset to perform further access checks
    # using rstrip to remove trailing ; ( ) in the dataset names
    # removal of parenthesis is needed in case of queries containing sub-selects

    for domain_dataset_str in list_of_strings_after_splitting_sql_by_white_spaces:
        if "." in domain_dataset_str:
            query_str = domain_dataset_str.lower().split(".", 1)[1].rstrip(";()")
            if query_str in datasets_original_and_lower_case_dict:
                dataset_name, dataset_id = datasets_original_and_lower_case_dict[domain_dataset_str.lower().split(".", 1)[1].rstrip(";()")]
                dataset_id_dict[dataset_id] = dataset_name
    return dataset_id_dict


def manage_view_resource_access(
    access_type,
    resource_ids,
    tag_user_map,
    approver_id,
    dynamodb_resource,
    db_tables,
    dwh_details,
    audit_log_config,
):
    """
    This method manages access for views (both DWH & S3Athena)
    :param access_type: None if the call is to revoke, else owner or read-only
    :param resource_id: List of Resources that owner will provide access to
    :param tag_user_map: Mapping of tags (tag_key, tag_value) to lists of users
    :param approver_id: One who triggers this API call, owner
    :param dynamodb_resource: DynamoDB object
    :param db_tables: ViewsTable in DynamoDB
    :param dwh_details: jdbc datasource details to dwh
    :param audit_log_config: Configuration for audit logging
    """
    LOGGER.info("In authUtil.manage_view_resource_access method, updating access for multiple resources by user - %s", approver_id)
    # Check whether access type matches resource access types or none
    if access_type not in commonUtil.ACCESS_TYPES + [None]:
        LOGGER.error("In authUtil.manage_view_resource_access method, encountered access type %s", access_type)
        ec_ipv_1005 = errorUtil.get_error_object("IPV-1005")
        ec_ipv_1005["Message"] = ec_ipv_1005["Message"].format(access_type)
        raise errorUtil.InvalidInputException(EVENT_INFO, ec_ipv_1005)

    # Check whether approver is authorized or not(has owner access or not)
    # user_permission = get_user_resource_permission(dynamodb_resource, "views", resource_id, approver_id, audit_log_config)
    # if user_permission not in ["owner", "editor"]:
    #     LOGGER.info(
    #         "In authUtil.manage_view_resource_access method, user %s has %s permission on resource %s",
    #         approver_id,
    #         user_permission,
    #         resource_id,
    #     )
    #     ec_auth_1005 = errorUtil.get_error_object("AUTH-1005")
    #     ec_auth_1005["Message"] = ec_auth_1005["Message"].format(approver_id)
    #     raise errorUtil.InvalidInputException(EVENT_INFO, ec_auth_1005)

    # fetching view details
    view_details_list = dynamodbUtil.batch_get_items(dynamodb_resource, db_tables["dataset_table"],
        [{"DatasetId": resource_id} for resource_id in resource_ids],
        audit_log_config,
    )
    view_details_map = {item["DatasetId"]: item for item in view_details_list}
    for resource_id in resource_ids:
        view_details = view_details_map.get(resource_id)
        resource_name = view_details["DatasetName"]

        # Users should not able to share non-active views
        if view_details.get("IsActive", "yes") == "no":
            ec_grp_1003 = errorUtil.get_error_object("TAG-1013")
            raise errorUtil.InvalidInputException(EVENT_INFO, ec_grp_1003)

        if view_details["TargetLocation"] == commonUtil.TARGET_LOCATION_MAP["redshift"]:
            # checking if redshift cluster is available
            redshiftUtil.is_redshift_cluster_available(dwh_details["dwh_host"])
            # If view is created inside a custom tenant and domain
            dwh_details["dwh_database"] = commonUtil.retrieve_tenant_db(
                {"Domain": view_details["Domain"]},
                dwh_details["dwh_database"],
                dynamodb_resource.Table(db_tables["tenant_table"]),
                audit_log_config,
            )

        for (tag_key, tag_value), users_list in tag_user_map.items():
            LOGGER.info(
                "In authUtil.manage_view_resource_access,Processing resource ID: %s, Tag: %s:%s, Users: %s",
                resource_id,
                tag_key,
                tag_value,
                users_list,
            )

            for user_to_be_granted in users_list:
                LOGGER.info(
                    "In authUtil.manage_view_resource_access method, with resource id %s and access type %s for user %s",
                    resource_id,
                    access_type,
                    user_to_be_granted,
                )

                # Check if user is valid
                commonUtil.is_valid_user(user_to_be_granted, dynamodb_resource.Table(db_tables["user_table"]), audit_log_config)


                if access_type:
                    # Provide access to the user
                    LOGGER.info("In authUtil.manage_view_resource_access, to grant access to %s on %s", user_to_be_granted, resource_id)
                    # Check whether user has access to view domain
                    domain_name = view_details.get("Domain", "N/A")
                    check_user_domain_access(domain_name, resource_name, [user_to_be_granted], "datasets", audit_log_config, dynamodb_resource)
                    # Lake formation views
                    if view_details["TargetLocation"] in [
                        commonUtil.TARGET_LOCATION_MAP["lf"],
                        commonUtil.TARGET_LOCATION_MAP["s3athena"],
                    ]:
                        # Validate if user has underlying dataset access
                        dataset_id_dict = extract_underlying_datasets(view_details["SqlStatement"], dynamodb_resource, db_tables["dataset_table"], audit_log_config)
                        for dataset_id, value in dataset_id_dict.items():
                            # check if user has access to this dataset
                            user_permission = get_user_resource_permission(dynamodb_resource, "datasets", dataset_id, user_to_be_granted, audit_log_config)
                            if not user_permission:
                                LOGGER.error(
                                    "In authUtil.manage_view_resource_access, user %s  has no access on lakeformation dataset %s, grant dataset permission prior to authorizing the view",
                                    user_to_be_granted,
                                    dataset_id,
                                )
                                ec_ds_1060 = errorUtil.get_error_object("DS-1060")
                                ec_ds_1060["Message"] = ec_ds_1060["Message"].format(user_to_be_granted, value)
                                raise errorUtil.InvalidInputException(EVENT_INFO, ec_ds_1060)

            if view_details["TargetLocation"] == commonUtil.TARGET_LOCATION_MAP["redshift"]:
                conn = dwhQueryUtil.get_dwh_connection(
                    dwh_details["data_warehouse_type"],
                    dwh_details["dwh_host"],
                    dwh_details["dwh_port"],
                    dwh_details["dwh_user"],
                    dwh_details["dwh_password"],
                    dwh_details["dwh_database"],
                )
                if not access_type:
                    dwhQueryUtil.revoke_permissions_to_view(
                        view_details["DatasetName"],
                        f"{tag_key}${tag_value}" if tag_key !='user' else f"u_{tag_value}", # redshift group or user name
                        view_details["Domain"],
                        conn,
                        dwh_details["data_warehouse_type"],
                        tag_key !='user' # boolean value indicating wether its a single user or group operation
                    )
                else:
                    dwhQueryUtil.assign_permissions_to_view(
                        view_details["DatasetName"],
                        f"{tag_key}${tag_value}" if tag_key !='user' else f"u_{tag_value}", # redshift group or user name
                        view_details["Domain"],
                        conn,
                        dwh_details["data_warehouse_type"],
                        dynamodb_resource,
                        db_tables["domains_table"],
                        view_details["SqlStatement"],
                        audit_log_config,
                        access_type,
                        tag_key !='user' # boolean value indicating wether its a single user or group operation
                    )

    LOGGER.info("In authUtil.manage_view_resource_access, exiting")
    return commonUtil.build_post_delete_response(200, {"Message": "Successfully updated user access"})


def auth_user_catalog_access(
    user_name_list: list, tenant_name_list: list, action: str, requestor_id: str, add_func_args_dict: dict, audit_log_config: dict
) -> None:
    """
     Method updates the user catalog access within the tenant. This method is called as on when there is an update to the user access
     for a tenant which is from Authorized users or tags.
    Args:
        user_name_list (list): List of users to whom the tenant needs to be attached/detached based on the action.
        tenant_name_list (list): Tenant name list which are attached/detached to the user
        action (str): Attach/Detach tenant to a user.
        requestor_id (str): Requestor user id who is initiating the change.
        add_func_args_dict (dict): Contains function arguments
        audit_log_config (dict): Configuration for audit logging

    Returns:
        None
    """
    try:
        LOGGER.info(
            "In authUtil.auth_user_catalog_access, tenant list - %s user list - %s, action - %s. Started updating redshift access",
            tenant_name_list,
            user_name_list,
            action,
        )
        if not user_name_list or not tenant_name_list:
            LOGGER.info("In authUtil.auth_user_catalog_access, skipped process as one of the key parameters are empty")
            return
        if action == "Attach":
            # Batch get tenant details and apply catalog permissions only when the global user catalog access parameter is enabled
            key_list = [{"TenantName": tenant_name} for tenant_name in tenant_name_list]
            tenant_items = dynamodbUtil.batch_get_items(add_func_args_dict["DynamoDBResource"], dynamodbUtil.TENANT_TABLE, key_list, audit_log_config)
            if len(key_list) != len(tenant_name_list):
                LOGGER.error(
                    "In authUtil.auth_user_catalog_access, Missing tenants in metadata, keys passed %s, tenants retrieved %s",
                    key_list,
                    tenant_items,
                )
            for tenant_item in tenant_items:
                # Take precedence when a global setting from DWH management page is called
                dwh_user_access = add_func_args_dict.get("UserAccess", {}).get(tenant_item["TenantName"], {})
                if not dwh_user_access:
                    dwh_user_access = tenant_item.get("UserCatalogAccess", "enabled")
                if dwh_user_access == "enabled":
                    # This method provides user catalog access by disabling user to select/list databases and users in the cluster
                    redshiftDataUtil.update_user_catalog_access(tenant_item["TenantName"], ",".join(user_name_list), add_func_args_dict, audit_log_config)
                else:
                    LOGGER.info(
                        "In authUtil.auth_user_catalog_access, skipped process as user catalog access is disabled for tenant - %s",
                        tenant_item["TenantName"],
                    )
        else:
            for tenant_name in tenant_name_list:
                max_retries = 6
                retries = 0
                query_statement = "REVOKE USAGE ON SCHEMA pg_catalog FROM {}".format(",".join(user_name_list))
                upd_success = False
                query_details = redshiftDataUtil.submit_query_to_rs(
                    add_func_args_dict["Client"],
                    query_statement,
                    requestor_id,
                    add_func_args_dict["ClusterId"],
                    tenant_name,
                    add_func_args_dict["DWHUser"],
                )
                LOGGER.info(
                    "In authUtil.auth_user_catalog_access, successfully submitted query with response - %s",
                    query_details,
                )
                while retries < max_retries:
                    time.sleep(3**retries)
                    retries = retries + 1
                    qe_response = redshiftDataUtil.get_query_execution(
                        query_details["QueryId"],
                        add_func_args_dict["Client"],
                        add_func_args_dict["DynamoDBResource"],
                        requestor_id,
                        add_func_args_dict["RSQueryTable"],
                        audit_log_config,
                        None,
                    )
                    if qe_response["QueryStatus"] == "FINISHED":
                        LOGGER.info("In authUtil.auth_user_catalog_access, successfully completed user tenant catalog access")
                        upd_success = True
                        break
                    if qe_response["QueryStatus"] == "FAILED":
                        LOGGER.error("In authUtil.auth_user_catalog_access, failed to run update user catalog access query in redshift")
                        raise Exception(qe_response.get("Message", "Unknown failure"))
                    LOGGER.info("In authUtil.auth_user_catalog_access, revoke query pending re-trying attempt - %s", retries)
                if not upd_success:
                    raise Exception("Unable to update user tenant catalog access. Operation timed out as process reached maximum retries")
        LOGGER.info("In authUtil.auth_user_catalog_access, Successfully updated authorized user(s) tenant catalog access in redshift")
    except Exception as ex:
        LOGGER.error("In authUtil.auth_user_catalog_access, error updating user catalog access - %s", ex)
        ec_rs_1017 = errorUtil.get_error_object("RS-1017")
        message = "Failed to update access with error - {}".format(ex)
        ec_rs_1017["Message"] = message
        raise errorUtil.GenericFailureException(EVENT_INFO, ec_rs_1017)


def update_tenant_user_profile(
    user_list: list,
    tenant_name_list: list,
    dynamodb_resource: list,
    user_table: str,
    add_func_args_dict: dict,
    action: str,
    requestor_id: str,
    resource_access_check: bool = True,
) -> None:
    """
    This function updates the user metadata with tenant information
    Args:
        user_list (list): List of users to whom the tenant needs to be attached/detached based on the action.
        tenant_name_list (list): Tenant name list which are attached/detached to the user
        dynamodb_resource: boto3 dynamodb resource
        user_table (str): User table name
        add_func_args_dict (dict): Contains function arguments
        action (str): Attach/Detach tenant to a user.
        requestor_id (str): Requestor user id who is initiating the change.
        resource_access_check (bool): Check for resource access

    Returns:
        None
    """
    LOGGER.info(
        "In authUtil.update_tenant_user_profile, input user list - %s, tenants - %s with action - %s",
        user_list,
        tenant_name_list,
        action,
    )
    audit_log_config = add_func_args_dict.get("AuditLogConfig")
    if user_list:
        # Update tenant catalog access to the user
        users_key_list = [{"UserId": user_id} for user_id in set(user_list)]
        user_items = dynamodbUtil.batch_get_items(dynamodb_resource, user_table, users_key_list, audit_log_config, None)
        dynamodb_condition = "ADD" if action == "Attach" else "DELETE"
        modified_condition = ":val1 SET"
        for user_detail in user_items:
            cons_user_tenant_name_list = deepcopy(tenant_name_list)
            key = {"UserId": user_detail["UserId"]}
            expression_attributes = {
                ":val1": set(cons_user_tenant_name_list),
                ":val2": commonUtil.get_current_time(),
                ":val3": requestor_id,
            }
            if "TenantsAttached" not in user_detail and action == "Attach":
                dynamodb_condition = "SET"
                modified_condition = "=:val1,"
            else:
                if action == "Detach":
                    if resource_access_check:
                        tenants_with_access_type = retrieve_user_accessible_resources(dynamodb_resource, "tenants", user_detail["UserId"], audit_log_config)
                        LOGGER.info(
                            "In authUtil.update_tenant_user_profile, user - %s, tenants with access types - %s",
                            user_detail["UserId"],
                            tenants_with_access_type,
                        )
                        user_tenants = list(tenants_with_access_type.keys())
                        if not user_tenants:
                            # Raise an error if all the tenants are removed from the user
                            ec_dwh_1029 = errorUtil.get_error_object("DWH-1029")
                            error_message = "{}. All active tenants are removed from users profile, please re-try after repairing user metadata".format(
                                user_detail["UserId"]
                            )
                            ec_dwh_1029["Message"] = ec_dwh_1029["Message"].format(error_message)
                            raise errorUtil.GenericFailureException(EVENT_INFO, ec_dwh_1029)
                        remove_user_tenants = []
                        LOGGER.info(
                            "In authUtil.update_tenant_user_profile, input tenant list - %s, consolidated user tenant list - %s",
                            tenant_name_list,
                            user_tenants,
                        )
                        for tenant in tenant_name_list:
                            if tenant not in user_tenants:
                                remove_user_tenants.append(tenant)
                        # Update the tenant list to remove only the tenants which user doesnot have access to
                        cons_user_tenant_name_list = remove_user_tenants
                    if not cons_user_tenant_name_list:
                        LOGGER.info(
                            "In authUtil.update_tenant_user_profile, No Impacted tenants to update for user - %s",
                            user_detail["UserId"],
                        )
                        continue
            update_expression = "{} TenantsAttached {} LastModified = :val2, LastModifiedBy = :val3".format(dynamodb_condition, modified_condition)
            status = dynamodbUtil.update_item_by_key(dynamodb_resource.Table(user_table), key, update_expression, audit_log_config, expression_attributes)
            if status == "error":
                ec_db_1002 = errorUtil.get_error_object("DB-1002")
                raise errorUtil.InconsistentMetadataException(EVENT_INFO, ec_db_1002)
            LOGGER.info(
                "In authUtil.update_tenant_user_profile, successfully updated user %s metadata with tenants %s action %s",
                user_detail["UserId"],
                cons_user_tenant_name_list,
                action,
            )
            # Update redshift access, this is done after updating dynamodb because the logic validates accesses from other entities
            # and updates the tenant name list on which the action needs to be performed. The resource_access_check condition is only false
            # when the user is trying to delete the tenant
            if resource_access_check:
                auth_user_catalog_access(
                    [user_detail["UserName"]],
                    cons_user_tenant_name_list,
                    action,
                    requestor_id,
                    add_func_args_dict,
                    audit_log_config,
                )
        LOGGER.info("In authUtil.update_tenant_user_profile, successfully updated user's tenants both dynamodb and redshift access")
    else:
        LOGGER.info("In authUtil.update_tenant_user_profile, No Impacted users to update")


def retrieve_tenant_domains(tenant: str, dynamodb_resource, audit_log_config: dict) -> list:
    """
    This method is used to retrieve domains in a tenant
    Args:
        tenant: Tenant Name
        dynamodb_resource: Dynamodb table boto3 resource
        audit_log_config: Dynamodb Audit log configuration

    Returns:
        list: List of domains in a tenant
    """
    LOGGER.info("In authUtil.retrieve_tenant_domains method, retrieving domains for tenant - %s", tenant)
    filter_expression = Attr("TenantName").eq(tenant)
    tenant_domain_items = dynamodbUtil.scan_with_pagination(dynamodb_resource.Table(dynamodbUtil.DOMAIN_TABLE), audit_log_config, filter_expression, None, None)
    LOGGER.info("In authUtil.retrieve_tenant_domains method, retrieved domains for tenant - %s", tenant_domain_items)
    return tenant_domain_items


def retrieve_tenant_parameters(tenant_name: str, project_short_name: str, dynamodb_resource, audit_log_config: dict) -> list:
    """
    This method is used to retrieve parameters in a tenant
    Args:
        tenant_name: Tenant Name
        project_short_name: Project Short Name
        dynamodb_resource: Dynamodb table boto3 resource
        audit_log_config: Dynamodb Audit log configuration

    Returns:
        list: List of parameters in
    """
    LOGGER.info(
        "In authUtil.retrieve_tenant_parameters method, retrieving parameters for tenant - %s, project_short_name - %s",
        tenant_name,
        project_short_name,
    )
    # parameters that are created before tenants feature will not have TenantName attribute in dynamodb items.
    # All those parameters are treated as part of default tenant i.e., PROJECT_SHORTNAME
    # below filter conditions will check for default tenant and if it is a default tenant then get all the parameters that have TenantName as PROJECT_SHORTNAME
    # and also the parameters that doesn't has a TenantName attribute and which are global & user scoped variables (doesn't list system variables)
    if tenant_name == project_short_name:
        filter_expression = Attr("TenantName").eq(tenant_name) | (
            Attr("TenantName").not_exists()
            & Attr("Scope").is_in(["global", "user"])
            & (Attr("Owner").ne(commonUtil.SYSTEM_RUNNER_ID) | Attr("Owner").ne(commonUtil.SYSTEM_RUNNER_ID.lower()))
        )
    else:
        filter_expression = Attr("TenantName").eq(tenant_name)
    tenant_parameter_items = dynamodbUtil.scan_with_pagination(
        dynamodb_resource.Table(dynamodbUtil.PARAMETERS_TABLE), audit_log_config, filter_expression, None, None
    )
    LOGGER.info("In authUtil.retrieve_tenant_parameters method, retrieved parameters for tenant - %s", tenant_parameter_items)
    return tenant_parameter_items


def check_last_auth_access_tenant(users_list: list, dynamodb_resource, tenant_name: str, audit_log_config: dict) -> None:
    """
    This function checks whether any user has the current tenant as the only accessible tenant
    Args:
        users_list (list): List of users
        dynamodb_resource: boto3 dynamodb resource
        tenant_name (str): Tenant name
        audit_log_config (dict): Configuration for audit logging

    Returns:
        None

    """
    LOGGER.info("In authUtil.check_last_auth_access_tenant method, Checking users - %s", users_list)
    for user_id in users_list:
        # Check if users have only a single tenant attached
        tenants_with_access_type = retrieve_user_accessible_resources(dynamodb_resource, "tenants", user_id, audit_log_config)
        LOGGER.info("In authUtil.check_last_auth_access_tenant, user tenants with access type - %s", tenants_with_access_type)
        user_tenants = list(tenants_with_access_type.keys())
        if not user_tenants:
            # Raise an error if all the tenants are removed from the user
            ec_dwh_1029 = errorUtil.get_error_object("DWH-1029")
            error_message = "{}. All active tenants are removed from users profile, please re-try after repairing user metadata".format(user_id)
            ec_dwh_1029["Message"] = ec_dwh_1029["Message"].format(error_message)
            raise errorUtil.GenericFailureException(EVENT_INFO, ec_dwh_1029)
        if len(user_tenants) == 1 and user_tenants[0] == tenant_name:
            LOGGER.error("In authUtil.check_last_auth_access_tenant, revoking tenant access failed, user should atleast have one tenant attached")
            ec_dwh_1031 = errorUtil.get_error_object("DWH-1031")
            ec_dwh_1031["Message"] = "Cannot remove user {} access to tenant {}.".format(user_id, user_tenants[0]) + ec_dwh_1031["Message"]
            raise errorUtil.GenericFailureException(EVENT_INFO, ec_dwh_1031)
    LOGGER.info("In authUtil.check_last_auth_access_tenant, exiting")


def provide_dataset_level_access_to_domain(dynamodb_resource, tag_key, tag_value, users_list, domain_name, access_type, audit_log_config, **kwargs):
    """
    This method is to provide dataset level access to a specific domain either user/tag.
    """
    LOGGER.info(
        "In authUtil.provide_dataset_level_access_to_domain, Providing Dataset level access to the %s=%s for domain %s.", tag_key, tag_value, domain_name
    )
    error_message = None
    try:
        # Get the domain item and validate the origin to proceed further
        domain_item = dynamodbUtil.get_item_with_key(dynamodb_resource.Table(DOMAINS_TABLE), {"DomainName": domain_name}, audit_log_config)
        ### Update DWH related permissions
        if kwargs["DATALAKE_DWH"] == "redshift" and domain_item.get("ResourceOrigin", "API") != "AWSConsole":
            try:
                if "_" in domain_name and MULTI_TENANCY == "yes":
                    database_name = domain_item.get("TenantName", kwargs["DWH_DATABASE"])
                    kwargs["CONN"] = redshiftUtil.get_redshift_connection(
                        kwargs["DWH_HOST"], kwargs["DWH_PORT"], kwargs["DWH_USER"], kwargs["DWH_PASSWORD"], database_name
                    )
                if tag_key != "user":
                    redshiftUtil.assign_dataset_level_perms_to_redshift_group(f"{tag_key}${tag_value}", access_type, domain_name, kwargs["CONN"])
                else:
                    # Get the user details
                    user_details = commonUtil.get_userdetails(tag_value, dynamodbUtil.USER_TABLE, dynamodb_resource, audit_log_config)
                    redshiftUtil.assign_dataset_level_perms_to_redshift_user(user_details["UserName"], access_type, domain_name, kwargs["CONN"])
            except redshiftUtil.RedshiftTableException as rs_ex:
                LOGGER.error("In authUtil.provide_dataset_level_access_to_domain, Exception while updating redshift permissions - %s", str(rs_ex))
                ec_rs_1017 = errorUtil.get_error_object("RS-1017")
                ec_rs_1017["Message"] = rs_ex
                raise errorUtil.InvalidInputException(EVENT_INFO, ec_rs_1017)
        else:
            # For other DWHs we don't need to add separate SQL Table permissions
            LOGGER.info("In authUtil.provide_dataset_level_access_to_domain, Skipped adding permissions for Datalake DWH - %s", kwargs["DATALAKE_DWH"])
        ### Update LF related permissions i.e. IAMRoles for all the LF datasets under the domain
        new_lf_users = []
        existing_lf_users = []
        upd_user_items = []
        # Retrieve all the LF datasets under the specific domain
        lf_datasets = dynamodbUtil.get_items_by_query_with_filter(
            dynamodb_resource.Table(dynamodbUtil.DATASET_TABLE),
            Key("Domain").eq(domain_name),
            None,
            Attr("TargetLocation").eq(commonUtil.TARGET_LOCATION_MAP["lf"]) & Attr("RegistrationStatus").eq("completed"),
            dynamodbUtil.DATASET_TABLE_DOMAIN_INDEX_NAME,
            None,
            audit_log_config,
        )
        if lf_datasets:
            LOGGER.info(
                "In authUtil.provide_dataset_level_access_to_domain, Lake formation supported datasets exist so providing creating IAMRole for users if not already present"
            )
            user_items = dynamodbUtil.batch_get_items(dynamodb_resource, USER_TABLE, [{"UserId": user_id} for user_id in users_list], audit_log_config)
            for user_item in user_items:
                if user_item.get("IAMRole"):
                    existing_lf_users.append(user_item)
                else:
                    new_lf_users.append(user_item)
            # Create IAM roles for new lake formation users
            upd_user_items = commonUtil.create_iam_roles_for_users(
                "lakeformation", new_lf_users, dynamodb_resource, USER_TABLE, kwargs["IAMUTIL_OS_ENV_VAR_DICT"], audit_log_config
            )
        # update existing inline policy for user_iam_role, this code is only for updating existing policy permissions.
        # backward compatibility
        for user_item in existing_lf_users + upd_user_items:
            commonUtil.update_custom_inline_policy_with_updated_permissions(
                user_item["UserId"], user_item["IAMRole"], kwargs["IAMUTIL_OS_ENV_VAR_DICT"], kwargs["IAM_CLIENT"]
            )
        for dataset_item in lf_datasets:
            for user_item in existing_lf_users + upd_user_items:
                catalog_id = dataset_item.get("CatalogId", kwargs["ACCOUNT_ID"])
                commonUtil.apply_effective_user_lf_permission(
                    user_item, dataset_item, kwargs["LF_CLIENT"], catalog_id, kwargs["LF_TABLES"], "grant-auth-user-access", audit_log_config, access_type, f"{tag_key}#{tag_value}"
                )
        LOGGER.info(
            "In authUtil.provide_dataset_level_access_to_domain, Updated permissions of all datasets under domain %s to %s=%s", domain_name, tag_key, tag_value
        )
    except Exception as ex:
        error_message = str(ex)
        LOGGER.error(
            "In authUtil.provide_dataset_level_access_to_domain, Error while updating dataset level access for resource %s with exception %s",
            domain_name,
            str(ex),
        )
        # As exception occurred, Revert the input IsDatasetLevelAccessProvided value to original state
        # "retry" will be present in kwargs if reverting to original state fails
        if "retry" not in kwargs:
            kwargs["IsDatasetLevelAccessProvided"] = not kwargs["IsDatasetLevelAccessProvided"]
        LOGGER.info(
            "In authUtil.provide_dataset_level_access_to_domain, As exception occurred, Reverting the Dataset level access value to original state - %s",
            kwargs["IsDatasetLevelAccessProvided"],
        )
        # Reverting back to older state if providing DLA failed
        if not kwargs["IsDatasetLevelAccessProvided"] and "retry" not in kwargs:
            # Adding key "retry" to kwargs to avoid recursive call of functions, ie DLA access failed -> reverting to older state -> reverting failed -> stop the process and send email
            kwargs["retry"] = 1
            revoke_dataset_level_access_from_domain(dynamodb_resource, tag_key, tag_value, users_list, domain_name, access_type, audit_log_config, **kwargs)
    return error_message


def revoke_dataset_level_access_from_domain(dynamodb_resource, tag_key, tag_value, users_list, domain_name, access_type, audit_log_config, **kwargs):
    """
    This method is to revoke dataset level access from a specific group
    """
    LOGGER.info("In authUtil.revoke_dataset_level_access_to_domain, Revoking Dataset level access to the %s=%s for domain %s.", tag_key, tag_value, domain_name)
    error_message = None
    try:
        #### Update DWH related permissions
        conn = kwargs["CONN"]
        # Get the domain item and validate the origin to proceed further
        domain_item = dynamodbUtil.get_item_with_key(dynamodb_resource.Table(DOMAINS_TABLE), {"DomainName": domain_name}, audit_log_config)
        ### Update DWH related permissions
        if kwargs["DATALAKE_DWH"] == "redshift" and domain_item.get("ResourceOrigin", "API") != "AWSConsole":
            try:
                if "_" in domain_name and MULTI_TENANCY == "yes":
                    database_name = domain_item.get("TenantName", kwargs["DWH_DATABASE"])
                    conn = redshiftUtil.get_redshift_connection(
                        kwargs["DWH_HOST"], kwargs["DWH_PORT"], kwargs["DWH_USER"], kwargs["DWH_PASSWORD"], database_name
                    )
                if tag_key != "user":
                    redshiftUtil.revoke_dataset_level_perms_from_redshift_group(f"{tag_key}${tag_value}", access_type, domain_name, conn)
                    ## As we revoked all dataset level permissions in the above step, We'll assign the group datasets again to group
                    LOGGER.info(
                        "In authUtil.revoke_dataset_level_access_to_domain, Retaining old permissions as we revoked all DWH permissions for group %s",
                        f"{tag_key}${tag_value}",
                    )
                    # Check if the user has access on any dataset using this tag
                    dataset_ids = [
                        list(dataset_item)[0]
                        for dataset_item in retrieve_resources_attached_to_tag("datasets", tag_key, tag_value, dynamodb_resource, audit_log_config)
                    ]
                    for dataset_id in dataset_ids:
                        # fetch dataset details
                        dataset_details = dynamodbUtil.get_item_with_key(
                            dynamodb_resource.Table(dynamodbUtil.DATASET_TABLE),
                            {"DatasetId": dataset_id},
                            audit_log_config,
                        )
                        # Re-assign DWH permissions only for the datasets under the specific domain
                        if dataset_details["Domain"].lower() == domain_name.lower():
                            # pylint: disable=line-too-long
                            if (
                                dataset_details["TargetLocation"].lower() == commonUtil.TARGET_LOCATION_MAP["redshift"]
                                and dataset_details["FileType"].lower() in commonUtil.DWH_SUPPORTED_FILEFORMATS[dataset_details["TargetLocation"].lower()]
                            ) or ("RedshiftTableName" in dataset_details.keys()):
                                if "_" in dataset_details["Domain"]:
                                    database_name = commonUtil.retrieve_tenant_db(
                                        {"Domain": dataset_details["Domain"]},
                                        kwargs["DWH_DATABASE"],
                                        dynamodb_resource.Table(dynamodbUtil.TENANT_TABLE),
                                        audit_log_config,
                                    )
                                    conn = redshiftUtil.get_redshift_connection(
                                        kwargs["DWH_HOST"], kwargs["DWH_PORT"], kwargs["DWH_USER"], kwargs["DWH_PASSWORD"], database_name
                                    )
                                redshiftUtil.assign_permissions_redshift(
                                    dataset_details.get("TableUpdate", "none"),
                                    dataset_details["DatasetName"],
                                    f"{tag_key}${tag_value}",
                                    dataset_details["Domain"],
                                    conn,
                                    access_type,
                                )
                else:
                    # Get the user details
                    user_details = commonUtil.get_userdetails(tag_value, dynamodbUtil.USER_TABLE, dynamodb_resource, audit_log_config)
                    redshiftUtil.revoke_dataset_level_perms_from_redshift_user(user_details["UserName"], access_type, domain_name, conn)
                    ## As we revoked all dataset level permissions in the above step, We'll assign the group datasets again to group
                    # Check if the user has any direct access on any dataset under this domain
                    datasets_with_access_type = retrieve_user_accessible_resources(dynamodb_resource, "datasets", tag_value, audit_log_config, True)
                    user_datasets_ids = list(datasets_with_access_type.keys())
                    for dataset_id in user_datasets_ids:
                        # fetch dataset details
                        dataset_details = dynamodbUtil.get_item_with_key(
                            dynamodb_resource.Table(dynamodbUtil.DATASET_TABLE),
                            {"DatasetId": dataset_id},
                            audit_log_config,
                        )
                        # Re-assign DWH permissions only for the datasets under the specific domain
                        if dataset_details["Domain"].lower() == domain_name.lower():
                            # pylint: disable=line-too-long
                            if (
                                dataset_details["TargetLocation"].lower() == commonUtil.TARGET_LOCATION_MAP["redshift"]
                                and dataset_details["FileType"].lower() in commonUtil.DWH_SUPPORTED_FILEFORMATS[dataset_details["TargetLocation"].lower()]
                            ) or ("RedshiftTableName" in dataset_details.keys()):
                                if "_" in dataset_details["Domain"]:
                                    database_name = commonUtil.retrieve_tenant_db(
                                        {"Domain": dataset_details["Domain"]},
                                        kwargs["DWH_DATABASE"],
                                        dynamodb_resource.Table(dynamodbUtil.TENANT_TABLE),
                                        audit_log_config,
                                    )
                                    conn = redshiftUtil.get_redshift_connection(
                                        kwargs["DWH_HOST"], kwargs["DWH_PORT"], kwargs["DWH_USER"], kwargs["DWH_PASSWORD"], database_name
                                    )
                                redshiftUtil.assign_permissions(
                                    dataset_details.get("TableUpdate", "none"),
                                    dataset_details["DatasetName"],
                                    user_details["UserName"],
                                    dataset_details["Domain"],
                                    conn,
                                    access_type,
                                )
            except redshiftUtil.RedshiftTableException as rs_ex:
                LOGGER.error("In authUtil.revoke_dataset_level_access_to_domain, Exception while updating redshift permissions - %s", str(rs_ex))
                ec_rs_1017 = errorUtil.get_error_object("RS-1017")
                ec_rs_1017["Message"] = rs_ex
                raise errorUtil.InvalidInputException(EVENT_INFO, ec_rs_1017)
        else:
            # For other DWHs we don't need to add separate SQL Table permissions
            LOGGER.info("In authUtil.revoke_dataset_level_access_to_domain, Skipped revoking permissions for Datalake DWH - %s", kwargs["DATALAKE_DWH"])
        #### Update LF related permissions i.e. IAMRoles for all the LF datasets under the domain
        existing_lf_users = []
        # Retrieve all the LF datasets under the specific domain
        lf_datasets = dynamodbUtil.get_items_by_query_with_filter(
            dynamodb_resource.Table(dynamodbUtil.DATASET_TABLE),
            Key("Domain").eq(domain_name),
            None,
            Attr("TargetLocation").eq(commonUtil.TARGET_LOCATION_MAP["lf"]) & Attr("RegistrationStatus").eq("completed"),
            dynamodbUtil.DATASET_TABLE_DOMAIN_INDEX_NAME,
            None,
            audit_log_config,
        )
        if lf_datasets:
            LOGGER.info(
                "In authUtil.revoke_dataset_level_access_to_domain, Lake formation supported datasets exist so providing creating IAMRole for users if not already present"
            )
            user_items = dynamodbUtil.batch_get_items(dynamodb_resource, USER_TABLE, [{"UserId": user_id} for user_id in users_list], audit_log_config)
            for user_item in user_items:
                if user_item.get("IAMRole"):
                    existing_lf_users.append(user_item)
            for dataset_item in lf_datasets:
                for user_item in existing_lf_users:
                    catalog_id = dataset_item.get("CatalogId", kwargs["ACCOUNT_ID"])
                    commonUtil.apply_effective_user_lf_permission(
                        user_item, dataset_item, kwargs["LF_CLIENT"], catalog_id, kwargs["LF_TABLES"], "revoke-auth-user-access", audit_log_config, access_type, f"{tag_key}#{tag_value}", dla_revoke = True
                    )
        LOGGER.info(
            "In authUtil.revoke_dataset_level_access_to_domain, Updated permissions of all datasets under domain %s to %s=%s", domain_name, tag_key, tag_value
        )
    except Exception as ex:
        error_message = str(ex)
        LOGGER.error(
            "In authUtil.revoke_dataset_level_access_to_domain, Error while updating dataset level access for resource %s with exception %s",
            domain_name,
            str(ex),
        )
        # As exception occurred, Revert the input IsDatasetLevelAccessProvided value to original state
        # If retain_old_permissions is False then flow is from delete resource implies the value passed is from DDB metadata not input. So reverting accordingly
        if "retry" not in kwargs:
            kwargs["IsDatasetLevelAccessProvided"] = not kwargs["IsDatasetLevelAccessProvided"]
        LOGGER.info(
            "In authUtil.revoke_dataset_level_access_to_domain, As exception occurred, Reverting the Dataset level access value to original state - %s",
            kwargs["IsDatasetLevelAccessProvided"],
        )
        if kwargs["IsDatasetLevelAccessProvided"] and "retry" not in kwargs:
            # Adding key "retry" to kwargs to avoid recursive call of functions, ie DLA access failed -> reverting to older state -> reverting failed -> stop the process and send email
            kwargs["retry"] = 1
            provide_dataset_level_access_to_domain(dynamodb_resource, tag_key, tag_value, users_list, domain_name, access_type, audit_log_config, **kwargs)
    return error_message


def get_access_priority_from_access(input_string):
    """
    This method is used to get highest priority given access string
    """
    priority_dict = {"owner": 3, "editor": 2, "read-only": 1}
    return priority_dict[input_string]


def get_user_segregated_permission(user_id, dataset_id, dynamodb_resource, audit_log_config):
    """
    Returns AccessType of user to a dataset and details related to the origin of it
    :param user_id
    :param dataset_id
    :param dynamodb_resource
    :param audit_log_config
    :return Accesstype - owner/read-only/admin/None
    """
    LOGGER.info("In commonUtil.get_user_segregated_permission with user_id %s, dataset_id %s", user_id, dataset_id)
    segregated_permission = {"OverallPermission": None, "UserPermission": None, "TagPermission": None}
    user_access = None
    tags_list = retrieve_user_accessible_tags(dynamodb_resource, user_id, audit_log_config)
    highest_access = None

    starting_sort_key = f"datasets#{tags_list[0]}#{AccessType.EDITOR.label}"
    ending_sort_key = f"datasets#{tags_list[-1]}#{AccessType.READONLY.label}"

    acl_response = dynamodbUtil.get_items_by_query(
        dynamodb_resource.Table(ACL_RESOURCES_TABLE),
        Key("ResourceId").eq(dataset_id) & Key("TagAccessKey").between(starting_sort_key, ending_sort_key),
        "TagAccessKey",
        audit_log_config,
    )

    if acl_response:
        # fetch user direct access if any
        for item in acl_response:
            if item["TagAccessKey"].split("#")[1] == "user" and item["TagAccessKey"].split("#")[2] == user_id:
                user_access = item["TagAccessKey"].split("#")[-1]
                break

        # Filter out the items that do not belong to tags_list
        filtered_items = [
            item["TagAccessKey"].split("#")[-1]
            for item in acl_response
            if ("#".join(item["TagAccessKey"].split("#")[1:3]) in tags_list) and (item["TagAccessKey"].split("#")[1] != "user")
        ]
        # Get the highest access type
        highest_access = max(filtered_items, key=get_access_priority)

    all_access = []
    if user_access:
        segregated_permission["UserPermission"] = user_access
        all_access.append(user_access)
    if highest_access:
        segregated_permission["TagPermission"] = highest_access
        all_access.append(highest_access)
    if user_access or highest_access:
        segregated_permission["OverallPermission"] = max(highest_access, key=get_access_priority_from_access)
    # LOGGER.info("In commonUtil.get_user_segregated_permission, User metadata user data item - %s, access list - %s", user_dataset_item, access_list)
    # if not user_dataset_item and not access_list:
    #     LOGGER.info("In commonUtil.get_user_segregated_permission, No metadata exists, User segregated permissions are - %s", segregated_permission)
    #     return segregated_permission
    # # Updating permissions from authorized user
    # if user_dataset_item and 'AccessType' in user_dataset_item:
    #     user_access_type = user_dataset_item['AccessType'].lower()
    #     access_list.append(user_access_type)
    #     segregated_permission["UserPermission"] = user_access_type
    # segregated_permission["OverallPermission"] = "owner" if 'owner' in set(access_list) else "read-only"
    # LOGGER.info("In commonUtil.get_user_segregated_permission, User segregated permissions are - %s", segregated_permission)
    return segregated_permission


def retrieve_tag_resource_access(dynamodb_resource, resource_type, resource_id, tag_key, tag_value, audit_log_config):
    """
    Retrieve the access of tag on resource
    """
    LOGGER.info("In authUtil.retrieve_tag_resource_access method, getting tag - %s:%s permission for resource - %s", tag_key, tag_value, resource_id)
    sort_key_prefix = f"{resource_type}#{tag_key}#{tag_value}#"
    key_condition_expression = Key("ResourceId").eq(resource_id) & Key("TagAccessKey").begins_with(sort_key_prefix)
    acl_response = dynamodbUtil.get_items_by_query(dynamodb_resource.Table(ACL_RESOURCES_TABLE), key_condition_expression, None, audit_log_config)
    LOGGER.info("In authUtil.retrieve_tag_resource_access method, acl response - %s", acl_response)

    if resource_type == "datasets":
        highest_access = None
        # For datasets checking if the tag has access through DLA
        dataset_item = dynamodbUtil.get_item_with_key(dynamodb_resource.Table(DATASET_TABLE), {'DatasetId': resource_id}, audit_log_config)
        domain_sort_key_prefix = f"domains#{tag_key}#{tag_value}#"
        domain_key_condition_expression = Key("ResourceId").eq(dataset_item["Domain"]) & Key("TagAccessKey").begins_with(domain_sort_key_prefix)
        acl_domain_response = dynamodbUtil.get_items_by_query(dynamodb_resource.Table(ACL_RESOURCES_TABLE), domain_key_condition_expression, None, audit_log_config)
        LOGGER.info("In authUtil.retrieve_tag_resource_access method, acl domain response - %s", acl_domain_response)
        if acl_domain_response and acl_domain_response[0].get("AdditionalMetadata", {}).get("IsDatasetLevelAccessProvided", False):
            tag_access_key = acl_domain_response[0]["TagAccessKey"]
            tag_name = "#".join(tag_access_key.split("#")[1:3])
            current_access_type = tag_access_key.split("#")[-1]
            dataset_acl_item = {"ResourceId": dataset_item["DatasetId"], "TagAccessKey": f"datasets#{tag_name}#{current_access_type}"}
            acl_response.append(dataset_acl_item)
        LOGGER.info("In authUtil.retrieve_tag_resource_access method, final acl response - %s", acl_response)
        if acl_response:
            filtered_items = [item["TagAccessKey"].split("#")[-1] for item in acl_response]
            LOGGER.info("In authUtil.retrieve_tag_resource_access method, filtered items - %s", filtered_items)
            # Get the highest access type
            if filtered_items:
                highest_access = max(filtered_items, key=get_access_priority)
        LOGGER.info("In authUtil.retrieve_tag_resource_access method, Highest access for tag %s:%s on resource %s is %s", tag_key, tag_value, resource_id, highest_access)
        return highest_access
    else:
        return acl_response[0]["TagAccessKey"].split("#")[-1] if acl_response else None

def get_owners_list_with_tags(dataset_id, dynamodb_resource, audit_log_config):
    """
    The function will give the user_id list for a particular dataset_id who are all the owners along with access from tags.
    """
    users_list = []
    users_list = list(
        retrieve_users_attached_to_resource(dynamodb_resource, "datasets", dataset_id, commonUtil.SYSTEM_RUNNER_ID, audit_log_config).get("Owner", [])
    )
    return users_list


def get_dataset_owner_details(dataset_id, dynamodb_resource, audit_log_config):
    """
    This method returns the details of the owners for a given dataset id
    :param dataset_id: unique id of the dataset
    :return dataset_owners_details: list objects with details of the owner
    """
    LOGGER.info("In authUtil.get_dataset_owner_details method")
    dataset_owners = get_owners_list_with_tags(dataset_id, dynamodb_resource, audit_log_config)
    dataset_owners_details = [commonUtil.get_userdetails(owner, USER_TABLE, dynamodb_resource, audit_log_config) for owner in dataset_owners]
    LOGGER.info(
        "In authUtil.get_dataset_owner_details method, retrieved owners for the dataset id '%s' - %s",
        dataset_id,
        dataset_owners_details,
    )
    return dataset_owners_details


def _get_user_dataset_permission(dynamodb_resource, dataset_id, user_id, audit_log_config, domain_name=""):
    """
    This method returns the user's highest level of access on a dataset given the dataset id.
    It also takes access via DLA into consideration.

    Args:
        dynamodb_resource: boto3 dynamodb resource
        dataset_id (str): UUID of the dataset
        user_id (str): user Id
        audit_log_config (dict): Audit log configuration object for dynamodb
        domain_name (str): Domain name of the dataset
    Returns:
        str: Highest access type for the user on the resource
    """
    LOGGER.info("In authUtil._get_user_dataset_permission method, getting user - %s permission for dataset - %s", user_id, dataset_id)

    # def get_access_priority_string(input_string):
    #     priority_dict = {"owner": 3, "editor": 2, "read-only": 1}
    #     return priority_dict[input_string]
    highest_access = None
    # if Domain of the dataset not given get it from dataset_item
    if not domain_name:
        dataset_item = dynamodbUtil.get_item_with_key(dynamodb_resource.Table(dynamodbUtil.DATASET_TABLE), {'DatasetId': dataset_id}, audit_log_config)
        if dataset_item:
            domain_name = dataset_item["Domain"]
        else:
            return highest_access

    tags_list = retrieve_user_accessible_tags(dynamodb_resource, user_id, audit_log_config)
    starting_sort_key = f"datasets#{tags_list[0]}#editor"
    ending_sort_key = f"datasets#{tags_list[-1]}#read-only"

    acl_response = dynamodbUtil.get_items_by_query_with_filter(
        dynamodb_resource.Table(ACL_RESOURCES_TABLE),
        Key("ResourceId").eq(dataset_id) & Key("TagAccessKey").between(starting_sort_key, ending_sort_key),
        "TagAccessKey",
        None,
        None,
        None,
        audit_log_config
    )
    if acl_response:
        # Filter out the items that do not belong to user accessible tagstags_list
        LOGGER.info("In authUtil._get_user_dataset_permission method, filter out the acl tags response - %s", acl_response)
        filtered_items = [item["TagAccessKey"].split("#")[-1] for item in acl_response if "#".join(item["TagAccessKey"].split("#")[1:3]) in tags_list]
        LOGGER.info("In authUtil._get_user_dataset_permission method, filtered items - %s", filtered_items)
        # Get the highest access type, stopping the checks if user has highest access
        if filtered_items:
            highest_access = max(filtered_items, key=get_access_priority)
            if highest_access == AccessType.OWNER.label:
                return highest_access

    # for datasets checking DLA access via domains
    # if resource_type == "datasets" and not ignore_dla:
    starting_sort_key = f"domains#{tags_list[0]}#{AccessType.EDITOR.label}"
    ending_sort_key = f"domains#{tags_list[-1]}#{AccessType.READONLY.label}"
    key_condition_expression = Key("ResourceType").eq("domains") & Key("TagAccessKey").between(starting_sort_key, ending_sort_key)
    filter_expression = Attr('AdditionalMetadata.IsDatasetLevelAccessProvided').eq(True) & Attr("ResourceName").eq(domain_name)
    acl_domains_response = dynamodbUtil.get_items_by_query_index(
        dynamodb_resource.Table(ACL_RESOURCES_TABLE),
        ACL_RESOURCES_TABLE_RESOURCETYPE_INDEX,
        audit_log_config,
        key_condition_expression,
        None,
        filter_expression
    )
    LOGGER.info("In authUtil._get_user_dataset_permission method, acl domains response - %s", acl_domains_response)
    if acl_domains_response:
        for domain_item in acl_domains_response:
            tag_access_key = domain_item["TagAccessKey"]
            tag_name = "#".join(tag_access_key.split("#")[1:3])
            current_access_type = tag_access_key.split("#")[-1]
            dataset_acl_item = {"ResourceId": dataset_id, "TagAccessKey": f"datasets#{tag_name}#{current_access_type}"}
            acl_response.append(dataset_acl_item)

    if acl_response:
        # Filter out the items that do not belong to tags_list
        LOGGER.info("In authUtil._get_user_dataset_permission method, filter out the acl response - %s", acl_response)
        filtered_items = [item["TagAccessKey"].split("#")[-1] for item in acl_response if "#".join(item["TagAccessKey"].split("#")[1:3]) in tags_list]
        LOGGER.info("In authUtil._get_user_dataset_permission method, filtered items - %s", filtered_items)
        # Get the highest access type
        if filtered_items:
            highest_access = max(filtered_items, key=get_access_priority)
    else:
        LOGGER.error("In authUtil._get_user_dataset_permission method, No access found for user %s on resource %s", user_id, dataset_id)
    LOGGER.info("In authUtil._get_user_dataset_permission method, Highest access for user %s on resource %s is %s", user_id, dataset_id, highest_access)
    return highest_access


def get_user_dataset_access_with_tagawsres_true(user_id, dataset_id, dynamodb_resource, audit_log_config):
    """
    This method returns the the list of tags with TagAwsResources=True for the dataset that user has access to
    Args:
        dynamodb_resource: boto3 dynamodb resource
        dataset_id (str): UUID of the dataset
        user_id (str): user Id
    Returns:
        str: Highest access type for the user on the resource
    """
    LOGGER.info("In authUtil.get_user_dataset_access_with_tagawsres_true method, getting user - %s's permission on dataset - %s", user_id, dataset_id)
    response_tags_list = []
    tags_list = retrieve_user_accessible_tags(dynamodb_resource, user_id, audit_log_config)
    starting_sort_key = f"datasets#{tags_list[0]}#{AccessType.EDITOR.label}"
    ending_sort_key = f"datasets#{tags_list[-1]}#{AccessType.READONLY.label}"
    acl_response = dynamodbUtil.get_items_by_query(
        dynamodb_resource.Table(ACL_RESOURCES_TABLE),
        Key("ResourceId").eq(dataset_id) & Key("TagAccessKey").between(starting_sort_key, ending_sort_key),
        "TagAccessKey,AdditionalMetadata",
        audit_log_config,
    )
    if acl_response:
        # Filter out the items that do not belong to tags_list
        response_tags_list = [
            "#".join(item["TagAccessKey"].split("#")[1:4])
            for item in acl_response
            if "#".join(item["TagAccessKey"].split("#")[1:3]) in tags_list and item.get("AdditionalMetadata", {}).get("TagAwsResources", False) is True
        ]
    # for datasets checking DLA access via domains
    # if resource_type == "datasets" and not ignore_dla:
    starting_sort_key = f"domains#{tags_list[0]}#{AccessType.EDITOR.label}"
    ending_sort_key = f"domains#{tags_list[-1]}#{AccessType.READONLY.label}"
    key_condition_expression = Key("ResourceType").eq("domains") & Key("TagAccessKey").between(starting_sort_key, ending_sort_key)
    acl_domains_response = dynamodbUtil.get_items_by_query_index(
        dynamodb_resource.Table(ACL_RESOURCES_TABLE),
        ACL_RESOURCES_TABLE_RESOURCETYPE_INDEX,
        audit_log_config,
        key_condition_expression,
    )
    if acl_domains_response:
        for domain_item in acl_domains_response:
            if domain_item.get("AdditionalMetadata", {}).get("IsDatasetLevelAccessProvided", False):
                tag_access_key = domain_item["TagAccessKey"]
                # fetch datasets under the domain
                dataset_items = dynamodbUtil.get_items_by_query_index(
                    dynamodb_resource.Table(dynamodbUtil.DATASET_TABLE),
                    dynamodbUtil.DATASET_TABLE_DOMAIN_INDEX_NAME,
                    audit_log_config,
                    Key("Domain").eq(domain_item["ResourceId"]),
                    "DatasetId",
                    None,
                )
                for dataset_item in dataset_items:
                    if dataset_item["DatasetId"] == dataset_id:
                        response_tags_list.append("#".join(tag_access_key.split("#")[1:4]))
    # Return the tags list in the format of tagkey:tagvalue
    return response_tags_list


def retrieve_datasets_attached_to_tag_with_dla(tag_key, tag_value, dynamodb_resource, audit_log_config):
    """
    Returns a dictionary of tag accessible datasets along with their access types
    """
    tag_name = f"{tag_key}#{tag_value}"
    resources_with_access_types = {}
    starting_sort_key = f"datasets#{tag_name}#{AccessType.EDITOR.label}"
    ending_sort_key = f"datasets#{tag_name}#{AccessType.READONLY.label}"

    key_condition_expression = Key("ResourceType").eq("datasets") & Key("TagAccessKey").between(starting_sort_key, ending_sort_key)

    acl_response = dynamodbUtil.get_items_by_query_index(
        dynamodb_resource.Table(ACL_RESOURCES_TABLE),
        ACL_RESOURCES_TABLE_RESOURCETYPE_INDEX,
        audit_log_config,
        key_condition_expression,
    )

    # for datasets checking DLA access via domains
    starting_sort_key = f"domains#{tag_name}#{AccessType.EDITOR.label}"
    ending_sort_key = f"domains#{tag_name}#{AccessType.READONLY.label}"
    key_condition_expression = Key("ResourceType").eq("domains") & Key("TagAccessKey").between(starting_sort_key, ending_sort_key)
    acl_domains_response = dynamodbUtil.get_items_by_query_index(
        dynamodb_resource.Table(ACL_RESOURCES_TABLE),
        ACL_RESOURCES_TABLE_RESOURCETYPE_INDEX,
        audit_log_config,
        key_condition_expression,
    )
    if acl_domains_response:
        for domain_item in acl_domains_response:
            if domain_item.get("AdditionalMetadata", {}).get("IsDatasetLevelAccessProvided", False):
                tag_access_key = domain_item["TagAccessKey"]
                tag_name = "#".join(tag_access_key.split("#")[1:3])
                current_access_type = tag_access_key.split("#")[-1]
                # fetch datasets under the domain
                dataset_items = dynamodbUtil.get_items_by_query_index(
                    dynamodb_resource.Table(dynamodbUtil.DATASET_TABLE),
                    dynamodbUtil.DATASET_TABLE_DOMAIN_INDEX_NAME,
                    audit_log_config,
                    Key("Domain").eq(domain_item["ResourceId"]),
                    "DatasetId",
                    None,
                )
                for dataset_item in dataset_items:
                    dataset_acl_item = {"ResourceId": dataset_item["DatasetId"], "TagAccessKey": f"datasets#{tag_name}#{current_access_type}"}
                    acl_response.append(dataset_acl_item)

    if acl_response:
        for item in acl_response:
            resource_id = item["ResourceId"]
            tag_access_key = item["TagAccessKey"]
            current_access_type = tag_access_key.split("#")[-1]
            current_priority = get_access_priority(tag_access_key)
            # Filter out tags which user does not have access to and capture only the highest access the user has on resource
            if resource_id not in resources_with_access_types or AccessType.from_label(resources_with_access_types[resource_id]).priority < current_priority:
                resources_with_access_types[resource_id] = current_access_type

    return resources_with_access_types


def get_user_registered_datasets(user_id, datasources_table, audit_log_config, **kwargs):
    """
    This function returns the list of datasets registered by the user.
    :param user_id:
    :param datasources_table:
    :param user_table:
    :return: dict
    """
    LOGGER.info("In authUtil.get_user_registered_datasets, Retrieving list of datasets for the user %s", user_id)
    dataset_list = {"datasets": []}
    dataset_id_list = []
    dataset_access = {}
    dynamodb_resource = kwargs["dynamodb_resource"]

    LOGGER.info("In authUtil.get_user_registered_datasets, Getting list of datasets datasources that are of bulkDataload type to filter from results")
    conn_filter_expression = Key("IngestionType").eq("bulkdataload")
    datasources_items = dynamodbUtil.scan_with_pagination(datasources_table, audit_log_config, conn_filter_expression)
    datasource_ids_bulkload = [
        each_datasource["DatasourceId"]
        for each_datasource in datasources_items
        if each_datasource["IngestionType"] == "bulkdataload"
    ]
    datasets_dict = retrieve_user_accessible_resources(dynamodb_resource, "datasets", user_id, audit_log_config)
    ud_items = [{"DatasetId": dataset_id, "AccessType": access} for dataset_id, access in datasets_dict.items()]
    ##### (CLOUD-2549) Adding the user related Dataset level access datasets to the existing datasets #####
    # Exemption case: For Athena temp credentials, No need to provide all DLA datasets list instead
    # domains list will be provided so that domain/* permission can be given in IAM Role respectively
    # Note: Following change is restricted to this method in authUtil and not for the same method in datasetUtil
    # because DLA datasets should be included in the 'datasetUtil' datasets listing page code.
    user_dla_domains_dict = {}
    if kwargs.get("action") == "generate_temp_athena_credentials":
        # Format: user_dla_domains_dict {"airline": "owner", "hotels": "editor", "movies": "read-only"}
        user_dla_domains_dict = commonUtil.get_dataset_level_access_domains_for_user(user_id, dynamodb_resource, audit_log_config)

    unique_ds = set()
    for ud_item in ud_items:
        if not ud_item["DatasetId"] in unique_ds:
            dataset_id_list.append({"DatasetId": ud_item["DatasetId"]})
            unique_ds.add(ud_item["DatasetId"])
        # Add accesstype if not present in the dictionary else if access is already present then check the existing access and update it accordingly
        # Owner permission takes precendence than read-only. Above response will have duplicates because a dataset can be present in multiple groups and the access to that dataset changes accordingly
        if not dataset_access.get(ud_item["DatasetId"]):
            dataset_access[ud_item["DatasetId"]] = ud_item["AccessType"]
        else:
            if dataset_access[ud_item["DatasetId"]] != ud_item["AccessType"] and (ud_item["AccessType"] == "owner" or dataset_access[ud_item["DatasetId"]]):
                dataset_access[ud_item["DatasetId"]] = "owner"

    LOGGER.info("In authUtil.get_user_registered_datasets, get all registered datasets at once")
    # Dedup dataset id keys from the above list of dictionaries
    dataset_batch_items = dynamodbUtil.batch_get_items(kwargs["dynamodb_resource"], kwargs["dataset_table"], dataset_id_list, audit_log_config)

    for dataset_item in dataset_batch_items:
        if dataset_item["IsActive"] == "yes":
            dataset_item["AccessType"] = dataset_access[dataset_item["DatasetId"]]
            # Add DatasourceType if not exists and default it to api
            dataset_item["DatasourceType"] = dataset_item.get("DatasourceType", "api")
            if "projection_keys" in kwargs and kwargs["projection_keys"]:
                key_list = kwargs["projection_keys"].split(",")
                dataset_item_new = {key: dataset_item[key] for key in dataset_item.keys() if key in key_list}
                if kwargs["bulk_jdbc_datasets"] == "false":
                    if "DatasourceId" not in dataset_item or (
                        (dataset_item.get("DatasourceId") not in datasource_ids_bulkload)
                        and dataset_item.get("TableUpdate") not in ["full-refresh", "full-load", "cdc", "full-load-and-cdc"]
                    ):
                        dataset_list["datasets"].append(dataset_item_new)
                    else:
                        LOGGER.info(
                            "In authUtil.get_user_registered_datasets, Dataset %s is loaded as part of JDBC bulk data load, so filtering it from result",
                            str(dataset_item["DatasetName"]),
                        )
                else:
                    dataset_list["datasets"].append(dataset_item_new)
            else:
                if kwargs["bulk_jdbc_datasets"] == "false":
                    if "DatasourceId" not in dataset_item or (
                        (dataset_item.get("DatasourceId") not in datasource_ids_bulkload)
                        and dataset_item.get("TableUpdate") not in ["full-refresh", "full-load", "cdc", "full-load-and-cdc"]
                    ):
                        dataset_list["datasets"].append(dataset_item)
                    else:
                        LOGGER.info(
                            "In authUtil.get_user_registered_datasets, Dataset %s is loaded as part of JDBC bulk data load, so filtering it from result",
                            str(dataset_item["DatasetName"]),
                        )
                else:
                    dataset_list["datasets"].append(dataset_item)
    return dataset_list, user_dla_domains_dict


def get_dataset_user_access(user_id, datasets, dynamodb_resource, audit_log_config):
    """
    Retrieves user access type of the given datasets.
     Note : This method does not take group access into consideration.
    :param user_id : User identification
    :param datasets : List of Dataset Id's
    :return User dataset access categorized based on access type owner/read-only/NoAccess
    """
    LOGGER.info("In authUtil.get_dataset_user_access with user_id %s, datasets %s", user_id, datasets)
    user_dataset_access_dict = {"Owner": [], "Editor": [], "ReadOnly": [], "NoAccess": []}
    datasets_with_access_type = retrieve_user_accessible_resources(dynamodb_resource, "datasets", user_id, audit_log_config)
    for dataset_id in datasets:
        if dataset_id in datasets_with_access_type:
            if datasets_with_access_type[dataset_id] == "owner":
                user_dataset_access_dict["Owner"].append(dataset_id)
            elif datasets_with_access_type[dataset_id] == "editor":
                user_dataset_access_dict["Editor"].append(dataset_id)
            else:
                user_dataset_access_dict["ReadOnly"].append(dataset_id)
        else:
            user_dataset_access_dict["NoAccess"].append(dataset_id)
    LOGGER.info("In authUtil.get_dataset_user_access, Returning datasets access - %s", user_dataset_access_dict)
    return user_dataset_access_dict


# pylint: disable=import-outside-toplevel
def update_dashboard_permissions(action, dynamodb_resource, tag_key, tag_value, user_id, event, audit_log_config):
    """
    This method updates user's permission on dashboards attached to an access tag
    :param action: grant or revoke
    :param dynamodb_resource: dynamodb boto3 resource
    :param tag_key: tag key
    :param tag_value: tag value
    :param user_id: user id of user to be added or removed from tag
    :param event: event info
    :param audit_log_config: dict
    :return: None
    :rtype: None
    """
    LOGGER.info("In authUtil.update_dashboard_permissions, starting method with action - %s, tag_key - %s, tag_value - %s, user_id - %s", action, tag_key, tag_value, user_id)
    # importing dashboardUtil inside the function to avoid circular dependency
    import dashboardUtil
    # retrieve dashboards attached to tag
    tag_dashboards = retrieve_resources_attached_to_tag("dashboards", tag_key, tag_value, dynamodb_resource, audit_log_config)
    LOGGER.info("In authUtil.update_dashboard_permissions, dashboards attached to tag - %s", tag_dashboards)
    # iterating over each dashboard and granting/revoking permissions
    if tag_dashboards:
        if "qs_dashboard_success_list" not in event:
            event['qs_dashboard_success_list'] = []
        # Variable to check if user principal is fetched from quicksight
        is_user_fetched = False
        for dashboard in tag_dashboards:
            dashboard_id = list(dashboard)[0]
            access_type = dashboard[dashboard_id]
            dashboard_item = dynamodbUtil.get_item_with_key(DYNAMODB_RES.Table(dynamodbUtil.DASHBOARD_TABLE), {'DashboardId': dashboard_id}, audit_log_config)
            for widget in dashboard_item.get("Widgets", []):
                if widget["WidgetId"] == "W_QuicksightDashboard":
                    qs_dashboard_id = widget["Configuration"]["QuicksightDashboardId"]["Value"]
                    user_access_dict = dashboardUtil.check_dashboard_permissions_for_users(qs_dashboard_id, [user_id], audit_log_config)
                    LOGGER.info("In authUtil.update_dashboard_permissions, user_access_dict = %s", user_access_dict)
                    # Fetch quicksight user details if not already fetched
                    if not is_user_fetched:
                        is_user_registered, user_principal = dashboardUtil.check_user_principal(user_id, audit_log_config)
                        is_user_fetched = True
                        LOGGER.info("In authUtil.update_dashboard_permissions, is_user_registered = %s, user_principal = %s", is_user_registered, user_principal)
                    # Check if user lesser access than the requested access type
                    if is_user_registered:
                        if action == "grant":
                            if commonUtil.get_access_priority(user_access_dict.get(user_id, {}).get('AccessType')) < commonUtil.get_access_priority(access_type):
                                dashboardUtil.grant_or_revoke_dashboard_access(action,
                                                                ACCOUNT_ID, qs_dashboard_id,
                                                                actions=commonUtil.QS_DASHBOARD_PERMISSIONS[access_type],
                                                                user_principal=user_principal)
                                event['qs_dashboard_success_list'].append((qs_dashboard_id, dashboard_id))
                        else:
                            # Before revoking check if user has access to this dashboard via some other tag/user(direct)
                            # retrieve user accessible tags
                            tags_list = retrieve_user_accessible_tags(DYNAMODB_RES, user_id, audit_log_config)
                            highest_access_from_other_tags = None
                            for tag in tags_list:
                                if tag != f"{tag_key}#{tag_value}":
                                    tags_access_on_dashboard = retrieve_tag_resource_access(dynamodb_resource, "dashboards", dashboard_id, tag.split('#')[0], tag.split('#')[-1], audit_log_config)
                                    highest_access_from_other_tags = max(highest_access_from_other_tags, tags_access_on_dashboard, key=get_access_priority)
                            # - If so check if access to be revoked > access from other ways
                            if commonUtil.get_access_priority(user_access_dict.get(user_id, {}).get('AccessType')) > commonUtil.get_access_priority(highest_access_from_other_tags):
                                # Revoke current access
                                dashboardUtil.grant_or_revoke_dashboard_access(action,
                                                                ACCOUNT_ID, qs_dashboard_id,
                                                                actions=commonUtil.QS_DASHBOARD_PERMISSIONS[user_access_dict.get(user_id, {}).get('AccessType')],
                                                                user_principal=user_principal)
                                # Grant the read-only access to the user role if the user has registered this quicksight dashboard with some other Amorphic dashboard
                                # Else the user won't have any access to the quicksight dashboard after revoke
                                if dashboardUtil.is_quicksight_dashboard_registered_elsewhere(qs_dashboard_id, user_id, dashboard_id, audit_log_config):
                                    dashboardUtil.grant_or_revoke_dashboard_access("grant",
                                                                    ACCOUNT_ID, qs_dashboard_id,
                                                                    actions=commonUtil.QS_DASHBOARD_PERMISSIONS['read-only'],
                                                                    user_principal=user_principal)
                                #  Grant back access from other ways if not None
                                if highest_access_from_other_tags:
                                    dashboardUtil.grant_or_revoke_dashboard_access("grant",
                                                                ACCOUNT_ID, qs_dashboard_id,
                                                                actions=commonUtil.QS_DASHBOARD_PERMISSIONS[highest_access_from_other_tags],
                                                                user_principal=user_principal)
                                event['qs_dashboard_success_list'].append((qs_dashboard_id, dashboard_id))
                    else:
                        LOGGER.info("In authUtil.update_dashboard_permissions, User %s is not registered in QuickSight so proceeding with lambda-session user %s", user_id, dashboardUtil.LAMBDA_SESSION_USER)
                        if action == "grant":
                            dashboardUtil.check_and_register_session_user()
                            dashboardUtil.grant_or_revoke_dashboard_access(action, ACCOUNT_ID, qs_dashboard_id)
                        elif not dashboardUtil.is_quicksight_dashboard_used_elsewhere(qs_dashboard_id, dashboard_id, audit_log_config):
                            dashboardUtil.grant_or_revoke_dashboard_access(action, ACCOUNT_ID, qs_dashboard_id)

    LOGGER.info("In authUtil.update_dashboard_permissions, Exiting method.")

def get_user_domain_permission(tags_list, dynamodb_resource, domain_name, user_id, audit_log_config):
    """
    Returns the user's permission on a domain including DLA information.

    Key steps:
    1. Retrieves the domain ACLs from the DynamoDB table
    2. Filters the ACLs to only include the ones that belong to the tags list
    3. Retrieves the highest access type from the ACLs
    4. Retrieves the highest DLA access type from the ACLs
    5. Returns the highest access type and highest DLA access type

    Args:
        tags_list: List of tags
        dynamodb_resource: DynamoDB resource
        domain_name: Name of the domain
        user_id: ID of the user
        audit_log_config: Audit log configuration

    Returns:
        highest_access: Highest access type on the domain
        highest_dla_access: Highest DLA access type on the domain
    """
    LOGGER.info("In authUtil.get_user_domain_permission, getting user %s permission for domain %s", user_id, domain_name)
    starting_sort_key = f"domains#{tags_list[0]}#{AccessType.EDITOR.label}"
    ending_sort_key = f"domains#{tags_list[-1]}#{AccessType.READONLY.label}"

    highest_access = None
    highest_dla_access = None
    acl_response = dynamodbUtil.get_items_by_query(
        dynamodb_resource.Table(ACL_RESOURCES_TABLE),
        Key("ResourceId").eq(domain_name) & Key("TagAccessKey").between(starting_sort_key, ending_sort_key),
        "TagAccessKey,AdditionalMetadata",
        audit_log_config,
    )
    if acl_response:
        # Filter out the items that do not belong to tags_list
        filtered_items = [item for item in acl_response if "#".join(item["TagAccessKey"].split("#")[1:3]) in tags_list]
        if filtered_items:
            # Get the highest access type
            highest_access = max(filtered_items, key=lambda x: get_access_priority(x["TagAccessKey"].split("#")[-1]))
        dla_items = [item for item in filtered_items if item.get("AdditionalMetadata", {}).get("IsDatasetLevelAccessProvided", False)]
        if dla_items:
            highest_dla_access = max(dla_items, key=lambda x: get_access_priority(x["TagAccessKey"].split("#")[-1]))

    LOGGER.info("In authUtil.get_user_domain_permission, Highest access for user %s on domain %s is %s, Highest DLA access is %s", user_id, domain_name, highest_access, highest_dla_access)
    return highest_access, highest_dla_access

def get_user_kb_source_acl_bypass(user_id, knowledge_base_id, dynamodb_resource, audit_log_config):
    """
    Returns True if the user is marked with BypassKBSourceACL flag in the AdditionalMetadata of the knowledge base.
    Args:
        user_id: ID of the user
        knowledge_base_id: ID of the knowledge base
        dynamodb_resource: DynamoDB resource
        audit_log_config: Audit log configuration

    Returns:
        True if the user is marked with BypassKBSourceACL flag in the AdditionalMetadata of the knowledge base, False otherwise
    """
    LOGGER.info("In authUtil.get_user_kb_source_acl_bypass, getting user %s permission for knowledge base %s", user_id, knowledge_base_id)

    tags_list = retrieve_user_accessible_tags(dynamodb_resource, user_id, audit_log_config)


    starting_sort_key = f"knowledgebases#{tags_list[0]}#{AccessType.EDITOR.label}"
    ending_sort_key = f"knowledgebases#{tags_list[-1]}#{AccessType.READONLY.label}"

    acl_response = dynamodbUtil.get_items_by_query(
        dynamodb_resource.Table(ACL_RESOURCES_TABLE),
        Key("ResourceId").eq(knowledge_base_id) & Key("TagAccessKey").between(starting_sort_key, ending_sort_key),
        "TagAccessKey,AdditionalMetadata",
        audit_log_config,
    )
    if acl_response:
        # If any entry has BypassKBSourceACL flag set to True, return True
        for item in acl_response:
            if item.get("AdditionalMetadata", {}).get("BypassKBSourceACL", False):
                LOGGER.info("In authUtil.get_user_kb_source_acl_bypass, user %s has bypass for knowledge base source ACL: %s", user_id, knowledge_base_id)
                return True

    LOGGER.info("In authUtil.get_user_kb_source_acl_bypass, user %s does not have bypass for knowledge base %s", user_id, knowledge_base_id)
    return False
