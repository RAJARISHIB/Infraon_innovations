# Azure Feature Builder Agent Usage

This README explains how to configure and use the Azure Feature Builder skill in Antigravity.

The workflow is:

```text
1. Configure .agents/.env
2. Tag the skill.md file in Antigravity
3. Ask the agent to implement a Work Item
4. Review the implementation plan
5. Approve the plan or comment required changes
6. Let the agent apply code changes
7. Let the agent run tests and report the result
```

---

## Folder Structure

Expected structure:

```text
D:\Folder\Repository
└── .agents
    ├── .env
    └── skills
        └── azure-feature-builder
            ├── extract_work_item.py
            └── skill.md
```

The skill entry file is:

```text
.agents\skills\azure-feature-builder\skill.md
```

The Work Item extraction script is:

```text
.agents\skills\azure-feature-builder\extract_work_item.py
```

---

## Environment Setup

Create or rename the environment file from:

```text
.env.conf
```

to:

```text
.env
```

Final path:

```text
D:\Folder\Repository\.agents\.env
```

Use the following values:

```env
AZDO_ORG=YOUR_AZURE_ORGANIZATION_NAME
AZDO_PROJECT=YOUR_AZURE_PROJECT_NAME
AZDO_PAT=<YOUR_AZURE_PERSONAL_ACCESS_TOKEN>
```

### Notes

- `AZDO_ORG` is the Azure DevOps organization name.
- `AZDO_PROJECT` is the Azure DevOps project name.
- `AZDO_PAT` must be a valid Azure DevOps Personal Access Token.
- The PAT needs at least this permission:

```text
Work Items - Read
```

Do not commit `.env` into Git.

---

## Install Python Requirements

From the repository root:

```powershell
pip install python-dotenv requests
```

If you use a virtual environment, activate it first.

Example:

```powershell
.\.venv\Scripts\activate
pip install python-dotenv requests
```

---

## Verify Work Item Fetching

From the repository root:

```powershell
python .\.agents\skills\azure-feature-builder\extract_work_item.py <WORK_ITEM_ID>
```

Example:

```powershell
python .\.agents\skills\azure-feature-builder\extract_work_item.py 3762
```

Expected result:

```text
The script should fetch and print normalized Azure Work Item details.
```

If it fails, check:

```text
- .agents\.env exists
- AZDO_ORG is correct
- AZDO_PROJECT is correct
- AZDO_PAT is valid
- PAT has Work Items - Read permission
- Network/VPN access to Azure DevOps is available
```

---

## Using the Skill in Antigravity

In Antigravity, tag the skill file and ask it to implement a Work Item.

Use this format:

```text
@.agents/skills/azure-feature-builder/skill.md Implement work item xxxxx
```

Example:

```text
@.agents/skills/azure-feature-builder/skill.md Implement work item 3762
```

The agent should first run:

```powershell
python .\.agents\skills\azure-feature-builder\extract_work_item.py 3762
```

Then it should read the Work Item details and provide an implementation plan.

---

## Implementation Plan Review

After you ask:

```text
@.agents/skills/azure-feature-builder/skill.md Implement work item xxxxx
```

the agent must not directly modify code.

It should first provide an implementation plan with:

```text
- Work Item summary
- Requirement interpretation
- Impacted files/modules
- Backend changes, if any
- Frontend changes, if any
- Query/data model changes, if any
- Edge cases
- Test plan
- Risks and assumptions
```

Review the plan carefully.

If changes are needed, comment on the plan.

Example:

```text
Change the implementation plan. Do not touch the UI. Only update the backend validation and tests.
```

or:

```text
Add API-level test cases also.
```

The agent should revise the plan and wait again.

---

## Approving the Plan

If the plan is correct, approve it explicitly.

Examples:

```text
Approved. Apply the changes and run tests.
```

```text
Proceed with this implementation plan.
```

```text
Looks good. Continue.
```

Only after approval should the agent modify files.

---

## Implementation and Testing

After approval, the agent should:

```text
1. Inspect impacted files.
2. Apply minimal required code changes.
3. Avoid unrelated refactoring.
4. Follow existing project patterns.
5. Run relevant tests or checks.
6. Report changed files and test results.
```

Possible test commands depend on the changed module.

Backend examples:

```powershell
python manage.py check
python manage.py test
```

Frontend examples:

```powershell
npm run build
npm run test
```

The agent should choose commands based on the actual impacted code.

---

## Manual Application Testing

If application login is required for manual testing, the agent may ask for:

```text
Application username and password
```

Rules:

```text
- Provide credentials only when required for testing.
- Do not ask the agent to store credentials.
- Do not put credentials in source code.
- Do not put credentials in .env unless they are explicitly intended config values.
- Do not commit credentials.
```

---

## MCP Reference

If implementation or testing needs MCP-specific guidance, the agent may refer to:

```text
.claude\skills\infraon_mcp\SKILL.md
```

Use this only when required for MCP behavior, product flow, or testing context.

---

## Final Report Expected From Agent

After implementation/testing, the agent should report:

```text
- Files changed
- Summary of changes
- Tests/checks run
- Test results
- Remaining risks
- Manual verification needed, if any
```

The workflow ends after implementation and testing.

The agent must not create or raise a pull request.

---

## Common Prompt Templates

### Start implementation planning

```text
@.agents/skills/azure-feature-builder/skill.md Implement work item 3762
```

### Ask for plan correction

```text
Update the implementation plan. Add validation for empty input and include backend test cases.
```

### Approve the plan

```text
Approved. Apply the changes and run the relevant tests.
```

### Ask for final verification

```text
Show me the files changed, test commands run, and remaining risks.
```
