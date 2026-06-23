import argparse
import base64
import json
import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


AGENTS_ENV_PATH = Path(r"D:\Folder\Repository\.agents\.env")

def load_environment() -> None:
    """Load Azure DevOps credentials from the fixed .agents/.env file."""
    if not AGENTS_ENV_PATH.is_file():
        raise FileNotFoundError(f"Unable to find .env file: {AGENTS_ENV_PATH}")

    load_dotenv(dotenv_path=AGENTS_ENV_PATH, override=True)

load_environment()

AZDO_ORG = os.environ["AZDO_ORG"]
AZDO_PROJECT = os.environ["AZDO_PROJECT"]
AZDO_PAT = os.environ["AZDO_PAT"]

BASE_URL = f"https://dev.azure.com/{AZDO_ORG}/{AZDO_PROJECT}/_apis"


def build_auth_header() -> dict[str, str]:
    token = base64.b64encode(f":{AZDO_PAT}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def get_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(build_auth_header())
    return session


def azure_get(session: requests.Session, path: str, params: dict[str, Any]) -> dict:
    url = f"{BASE_URL}/{path.lstrip('/')}"
    response = session.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def get_field(fields: dict, *keys: str, default: str = "") -> str:
    for key in keys:
        value = fields.get(key)
        if value not in (None, ""):
            return value
    return default


def get_identity(value: Any) -> str:
    if isinstance(value, dict):
        return value.get("displayName", "")
    return value or ""


def fetch_work_item(session: requests.Session, work_item_id: int) -> dict:
    return azure_get(
        session,
        f"wit/workitems/{work_item_id}",
        {
            "$expand": "all",
            "api-version": "7.1",
        },
    )


def fetch_work_item_comments(
    session: requests.Session,
    work_item_id: int,
    top: int = 100,
) -> list[dict]:
    comments = []
    continuation_token = None

    while True:
        params = {
            "$top": top,
            "order": "asc",
            "api-version": "7.1-preview.4",
        }

        if continuation_token:
            params["continuationToken"] = continuation_token

        url = f"{BASE_URL}/wit/workItems/{work_item_id}/comments"
        response = session.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        comments.extend(
            {
                "id": item.get("id"),
                "text": item.get("text", ""),
                "created_date": item.get("createdDate", ""),
                "modified_date": item.get("modifiedDate", ""),
                "created_by": get_identity(item.get("createdBy")),
                "modified_by": get_identity(item.get("modifiedBy")),
                "is_deleted": item.get("isDeleted", False),
            }
            for item in data.get("comments", [])
        )

        continuation_token = response.headers.get("x-ms-continuationtoken")
        if not continuation_token:
            return comments


def normalize_work_item(raw: dict, comments: list[dict] | None = None) -> dict:
    fields = raw.get("fields", {})

    return {
        "id": raw.get("id"),
        "type": get_field(fields, "System.WorkItemType"),
        "title": get_field(fields, "System.Title"),
        "state": get_field(fields, "System.State"),
        "assigned_to": get_identity(fields.get("System.AssignedTo")),
        "created_by": get_identity(fields.get("System.CreatedBy")),
        "changed_by": get_identity(fields.get("System.ChangedBy")),
        "created_date": get_field(fields, "System.CreatedDate"),
        "changed_date": get_field(fields, "System.ChangedDate"),
        "tags": get_field(fields, "System.Tags"),
        "module": get_field(fields, "Custom.Module", "System.AreaPath"),
        "description": get_field(fields, "System.Description"),
        "acceptance_criteria": get_field(
            fields,
            "Microsoft.VSTS.Common.AcceptanceCriteria",
        ),
        "acceptance_scenarios": get_field(
            fields,
            "Custom.AcceptanceScenarios",
            "Custom.AcceptanceScenario",
            "Custom.Scenarios",
        ),
        "integration_cases": get_field(
            fields,
            "Custom.IntegrationCases",
            "Custom.IntegrationCase",
        ),
        "implementation_notes": get_field(
            fields,
            "Custom.ImplementationNotes",
            "Custom.ImplementationNote",
        ),
        "impact_analysis": get_field(
            fields,
            "Custom.ImpactAnalysis",
            "Custom.Impact",
        ),
        "repro_steps": get_field(fields, "Microsoft.VSTS.TCM.ReproSteps"),
        "discussion": comments or [],
    }


def get_work_item_context(work_item_id: int) -> dict:
    session = get_session()
    raw_work_item = fetch_work_item(session, work_item_id)
    comments = fetch_work_item_comments(session, work_item_id)
    return normalize_work_item(raw_work_item, comments)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("work_item_id", type=int)
    args = parser.parse_args()

    context = get_work_item_context(args.work_item_id)

    print(json.dumps(context, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()