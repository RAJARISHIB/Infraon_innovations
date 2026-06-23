# Azure Feature Builder Skill

## Purpose

Use this skill to implement source-code changes from an Azure DevOps Work Item.

The skill must:

1. Fetch the Azure Work Item details using the Work Item ID given by the user.
2. Read and analyze the fetched requirements.
3. Prepare an implementation plan.
4. Wait for the user to accept the plan.
5. Apply the approved code changes.
6. Test the changes.
7. Report the final result.

This skill does **not** raise or create pull requests.

---

## Current Location

The skill is located inside the repository-level `.agents` directory.

```text
D:\Infraon\Infraon-1
└── .agents
    ├── .env
    └── skills
        └── azure-feature-builder
            ├── extract_work_item.py
            └── skill.md
```

### Skill Definition

```text
.agents\skills\azure-feature-builder\skill.md
```

### Work Item Extraction Script

```text
.agents\skills\azure-feature-builder\extract_work_item.py
```

### Environment File

```text
.agents\.env
```

---

## When To Use

Use this skill when the user provides an Azure DevOps Work Item ID and asks to implement, analyze, plan, or build the related change.

Examples:

```text
Implement work item 3762
Build the feature from Azure item 3762
Fetch work item 3762 and give me the implementation plan
Apply the changes for this Azure bug
```

---

## Required Input

```python
work_item_id: int
```

The Work Item ID must come from the user.

Do not invent or assume the Work Item ID.

---

## Actions

### 1. Fetch Work Item Details

Fetch the Work Item details by running `extract_work_item.py` with the Work Item ID provided by the user.

From the repository root:

```powershell
python .\.agents\skills\azure-feature-builder\extract_work_item.py <WORK_ITEM_ID>
```

Example:

```powershell
python .\.agents\skills\azure-feature-builder\extract_work_item.py 3762
```

If already inside the skill directory:

```powershell
python .\extract_work_item.py <WORK_ITEM_ID>
```

The script is the source of truth for Azure Work Item data.

Do not use the old `fetch_azure_work_item.py` path.

---

### 2. Read the Extracted Work Item Context

After fetching the Work Item, analyze all available fields from the script output.

Important fields to inspect:

```text
id
type
title
state
module
description
acceptance_criteria
acceptance_scenarios
integration_cases
implementation_notes
impact_analysis
repro_steps
assigned_to
created_by
changed_by
created_date
changed_date
tags
discussion
```

Always read discussion/comments because they may contain newer clarifications than the original description.

---

### 3. Build the Implementation Plan

Before modifying code, provide a clear implementation plan based on the fetched Work Item details.

The plan must include:

```text
- Summary of the Work Item
- Requirement interpretation
- Impacted modules/files
- Proposed backend changes, if any
- Proposed frontend changes, if any
- Data model/query changes, if any
- Validation rules or edge cases
- Test plan
- Risks or assumptions
```

If requirements are unclear, list the missing information and assumptions explicitly.

Do not apply source-code changes before the user accepts the implementation plan.

---

### 4. Wait for User Approval

After presenting the implementation plan, wait for explicit user approval.

Accepted approval examples:

```text
Proceed
Apply the changes
Looks good
Approved
Continue
```

If the user asks for changes to the plan, revise the plan first and wait again for approval.

---

### 5. Apply Approved Code Changes

After the user accepts the implementation plan:

1. Inspect the relevant source files.
2. Make the smallest safe changes required.
3. Avoid unrelated refactoring.
4. Preserve existing code style and project conventions.
5. Keep changes limited to the Work Item scope.
6. Do not modify secrets, credentials, generated files, or unrelated configuration.

If the implementation requires deeper product context or existing Infraon MCP behavior, refer to:

```text
.claude\skills\infraon_mcp\SKILL.md
```

Use that file only when required for MCP-specific implementation, testing, or product behavior guidance.

---

### 6. Test the Changes

After applying changes, run relevant tests or verification steps.

Testing may include:

```text
- Unit tests
- API tests
- UI build
- TypeScript compile checks
- Lint checks
- Django checks
- Manual API verification
- Manual UI verification
```

Use the smallest reliable test set first, then expand if failures indicate broader impact.

Example commands may include:

```powershell
npm run build
npm run test
python manage.py test
python manage.py check
```

Use commands that are valid for the affected module.

---

### 7. Application Login for Manual Testing

If manual application testing is required and credentials are not available, ask the user for the required application login details.

Allowed request:

```text
Please provide the application username and password needed to test this change.
```

Rules:

```text
- Request credentials only when required for testing.
- Do not store credentials.
- Do not write credentials into source code, logs, commits, or documentation.
- Do not expose credentials in the final response.
```

---

### 8. Report Final Result

After implementation and testing, provide a concise completion report.

Include:

```text
- Files changed
- What was changed
- Tests/commands run
- Test results
- Any remaining risks
- Any manual verification still required
```

Do not raise or create a pull request.

---

## Requirement Priority

If Work Item data conflicts, use this priority order:

```text
Acceptance Criteria
    ↓
Latest Discussion / Comments
    ↓
Acceptance Scenarios
    ↓
Integration Cases
    ↓
Implementation Notes
    ↓
Impact Analysis
    ↓
Description
```

---

## Important Rules

### Do Not Skip Work Item Fetch

Always fetch the Work Item details using:

```text
.agents\skills\azure-feature-builder\extract_work_item.py
```

before planning or implementation.

---

### Do Not Implement Before Plan Approval

The agent must provide the implementation plan first.

Source-code changes are allowed only after explicit user approval.

---

### Do Not Assume Missing Requirements

If required information is missing:

```text
- Identify the missing information.
- Record assumptions explicitly.
- Continue only when the plan is accepted.
```

Avoid speculative behavior.

---

### Keep Changes Minimal

Prefer:

```text
- Small targeted patches
- Existing project patterns
- Existing utilities/helpers
- Existing validation style
```

Avoid:

```text
- Large rewrites
- Unrelated cleanup
- New dependencies unless required
- Changing public behavior outside the Work Item scope
```

---

### No Pull Request Creation

This skill must not:

```text
- Create a pull request
- Raise a pull request
- Push branches
- Perform PR automation
```

The final output should stop after implementation, testing, and reporting.

---

## Environment Requirements

The `.env` file should be located at:

```text
.agents\.env
```

Expected Azure DevOps configuration:

```env
AZDO_ORG=<organization>
AZDO_PROJECT=<project>
AZDO_PAT=<personal_access_token>
```

Required Azure DevOps permission:

```text
Work Items - Read
```

---

## Example Workflow

```text
1. User provides Work Item ID.
2. Agent runs:
   python .\.agents\skills\azure-feature-builder\extract_work_item.py <WORK_ITEM_ID>
3. Agent reads the extracted Work Item details.
4. Agent analyzes requirements, acceptance criteria, impact, and discussion.
5. Agent provides an implementation plan.
6. User approves the plan.
7. Agent applies code changes.
8. Agent runs relevant tests.
9. Agent reports changed files, test results, and remaining risks.
```

---

## Example Script Usage

```python
from extract_work_item import get_work_item_context

work_item = get_work_item_context(3762)

print(work_item["title"])
print(work_item["description"])
print(work_item["acceptance_criteria"])
print(work_item["discussion"])
```

---

## Expected Consumer

The primary consumer of this skill is an implementation agent that:

```text
- Fetches Azure Work Item context.
- Creates an implementation plan.
- Waits for approval.
- Applies source-code changes.
- Tests the changes.
- Reports the result.
```

This skill is implementation-focused, but Azure DevOps access remains read-only.
