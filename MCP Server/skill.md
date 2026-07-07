# Azure Feature Builder Skill

## Purpose

Use this skill to implement source-code changes from an Azure DevOps Work Item.

The skill must:

1. Fetch the Azure DevOps Work Item details using the configured `azure-devops` MCP server.
2. Read and analyze the fetched Work Item requirements.
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
    └── skills
        └── azure-feature-builder
            └── skill.md
```

### Skill Definition

```text
.agents\skills\azure-feature-builder\skill.md
```

---

## Required MCP Server

This skill requires the Azure DevOps MCP server to be configured in Antigravity with the server name:

```text
azure-devops
```

The MCP server must use the `work-items` domain.

Recommended Antigravity MCP configuration:

```json
{
  "mcpServers": {
    "azure-devops": {
      "command": "C:\\nvm4w\\nodejs\\mcp-server-azuredevops.cmd",
      "args": [
        "infraon",
        "--authentication",
        "pat",
        "-d",
        "work-items"
      ],
      "env": {
        "PERSONAL_ACCESS_TOKEN": "<BASE64_EMAIL_COLON_PAT>"
      }
    }
  }
}
```

The `PERSONAL_ACCESS_TOKEN` value must be the base64-encoded form of:

```text
<azure-devops-email>:<azure-devops-pat>
```

Required Azure DevOps permission:

```text
Work Items - Read
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

### 1. Fetch Work Item Details Through Azure DevOps MCP

Fetch the Work Item details using the configured `azure-devops` MCP server.

Use the MCP work-item tools only. Do **not** run local extraction scripts.

The agent must fetch the specific Work Item ID provided by the user.

Required data to collect:

```text
id
type
title
state
module / area path
assigned_to
created_by
changed_by
created_date
changed_date
tags
description
acceptance_criteria
acceptance_scenarios
integration_cases
implementation_notes
impact_analysis
repro_steps / steps_to_reproduce
rca
test_cases
discussion / comments
```

Always fetch and read discussion/comments because they may contain newer clarifications than the original description.

Rules:

```text
- Use the Azure DevOps MCP server as the source of truth.
- Use only the Work Item ID provided by the user.
- Do not list projects unless the MCP server requires project context.
- Do not search for unrelated Work Items.
- Do not fetch repositories, pipelines, wiki pages, or PRs during this step.
- Do not run extract_work_item.py.
- Do not use fetch_azure_work_item.py.
```

If the MCP response returns raw Azure DevOps fields, map them into the required context before planning.

Suggested field mapping:

```text
System.Id                                  -> id
System.WorkItemType                        -> type
System.Title                               -> title
System.State                               -> state
System.AreaPath                            -> module
System.AssignedTo                          -> assigned_to
System.CreatedBy                           -> created_by
System.ChangedBy                           -> changed_by
System.CreatedDate                         -> created_date
System.ChangedDate                         -> changed_date
System.Tags                                -> tags
System.Description                         -> description
Microsoft.VSTS.Common.AcceptanceCriteria   -> acceptance_criteria
Microsoft.VSTS.TCM.ReproSteps              -> repro_steps / steps_to_reproduce
Custom.AcceptanceScenarios                 -> acceptance_scenarios
Custom.AcceptanceScenario                  -> acceptance_scenarios
Custom.Scenarios                           -> acceptance_scenarios
Custom.IntegrationCases                    -> integration_cases
Custom.IntegrationCase                     -> integration_cases
Custom.ImplementationNotes                 -> implementation_notes
Custom.ImplementationNote                  -> implementation_notes
Custom.ImpactAnalysis                      -> impact_analysis
Custom.Impact                              -> impact_analysis
Custom.RCA                                 -> rca
Custom.RootCauseAnalysis                   -> rca
Custom.RootCause                           -> rca
Microsoft.VSTS.CMMI.RootCause              -> rca
Custom.TestCases                           -> test_cases
Custom.TestCase                            -> test_cases
Custom.TestCaseDetails                     -> test_cases
Microsoft.VSTS.TCM.TestCases               -> test_cases
```

---

### 2. Read and Normalize the Work Item Context

After fetching the Work Item, analyze all available fields from the MCP response.

Prepare a normalized internal summary before creating the implementation plan.

Minimum normalized structure:

```text
- Work Item ID
- Work Item Type
- Title
- State
- Module / Area Path
- Description
- Acceptance Criteria
- Repro Steps / Steps to Reproduce
- Acceptance Scenarios
- Integration Cases
- Implementation Notes
- Impact Analysis
- RCA
- Test Cases
- Latest Discussion / Comments
```

Do not ignore empty or missing fields. If a key field is missing, mention that in the plan under assumptions or missing information.

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

Always fetch the Work Item details using the configured Azure DevOps MCP server before planning or implementation.

Do not use local scripts for Work Item fetching.

Disallowed fetch methods:

```text
.agents\skills\azure-feature-builder\extract_work_item.py
fetch_azure_work_item.py
manual assumptions from the Work Item ID only
```

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

Azure DevOps access is handled through the Antigravity MCP server configuration.

The skill does not require `.agents\.env` for Work Item fetching.

Required MCP environment variable:

```text
PERSONAL_ACCESS_TOKEN=<base64(email:pat)>
```

Required Azure DevOps permission:

```text
Work Items - Read
```

---

## Example Workflow

```text
1. User provides Work Item ID.
2. Agent uses the configured azure-devops MCP server to fetch the Work Item.
3. Agent fetches and reads discussion/comments for the Work Item.
4. Agent normalizes the Work Item details.
5. Agent analyzes requirements, acceptance criteria, impact, RCA, test cases, and discussion.
6. Agent provides an implementation plan.
7. User approves the plan.
8. Agent applies code changes.
9. Agent runs relevant tests.
10. Agent reports changed files, test results, and remaining risks.
```

---

## Example User Prompt

```text
Implement work item 3762
```

Expected agent behavior:

```text
1. Use the azure-devops MCP server.
2. Fetch Work Item 3762.
3. Fetch comments/discussion for Work Item 3762.
4. Summarize the requirement.
5. Provide an implementation plan.
6. Wait for approval before changing code.
```

---

## Expected Consumer

The primary consumer of this skill is an implementation agent that:

```text
- Fetches Azure Work Item context through MCP.
- Creates an implementation plan.
- Waits for approval.
- Applies source-code changes.
- Tests the changes.
- Reports the result.
```

This skill is implementation-focused, but Azure DevOps access remains read-only.
