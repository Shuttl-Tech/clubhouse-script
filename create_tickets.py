import os

from typing import List
from utils.github_service_owners import GITHUB_SERVICE_OWNERS
from utils.clubhouse_members import CLUBHOUSE_MEMBERS
from utils.clubhouse_projects import CLUBHOUSE_PROJECTS

import requests
import inquirer

reqs_session = requests.Session()

CLUB_HOUSE_URL = "https://api.clubhouse.io/api/v2"
CLUBHOUSE_API_TOKEN = os.environ["CLUBHOUSE_API_TOKEN"]
DEFAULT_STORY_TYPE = "chore"
DEFAULT_DESCRIPTION = "TODO: Add details"
EPIC_ID = 2031  # Audit Table


def confirm(msg):
    print(msg)
    print("Press CTRL-C to exit, any key to proceed:")
    input("")


def _create_clubhouse_ticket(
    name: str,
    project_id: int,
    owner_ids: List,
    epic_id: int,
    story_type: str = None,
    description: str = None,
):
    response = reqs_session.post(
        f"{CLUB_HOUSE_URL}/stories",
        json={
            "name": name,
            "owner_ids": owner_ids,
            "project_id": project_id,
            "story_type": story_type or DEFAULT_STORY_TYPE,
            "epic_id": epic_id,
            "description": description or DEFAULT_DESCRIPTION,
        },
        params={"token": CLUBHOUSE_API_TOKEN},
        headers={"Content-Type": "application/json"},
    )

    if response.status_code == 201:
        return response.json()["app_url"]
    else:
        print(
            f"Unable to create a ticket: {name} Response code: {response.status_code} Response text: {response.text}"
        )


github_services = GITHUB_SERVICE_OWNERS.keys()

question = {
    inquirer.Checkbox(
        "selected_services",
        message="Create a clubhouse ticket for the following services:",
        choices=github_services,
    )
}

answers = inquirer.prompt(question)

selected_services = answers["selected_services"]

for service in selected_services:

    owner = GITHUB_SERVICE_OWNERS.get(service)
    clubhouse_member_id = CLUBHOUSE_MEMBERS.get(owner)

    for project in CLUBHOUSE_PROJECTS:
        if service in project["services"]:
            project_id = project["id"]
            clubhouse_team = project["project"].upper()

    print(
        f"For {service.upper()} assigning ticket to {owner} for {clubhouse_team} team"
    )

    confirm("Proceed?")
    print("")

    app_url = _create_clubhouse_ticket(
        name=f"Fix increment id in existing audit table that uses trigger in {service} service",
        owner_ids=[clubhouse_member_id],
        epic_id=EPIC_ID,
        description="reference:https://paper.dropbox.com/doc/Audit-Tables-and-Increment-Id-fixes-37x8OuHdq80QmfqQN8snh",
        project_id=project_id,
    )

    print(f"Ticket created : {app_url}")

print("All Done!!")
