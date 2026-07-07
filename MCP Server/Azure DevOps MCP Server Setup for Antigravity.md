# Azure DevOps MCP Server Setup for Antigravity

This document explains how to configure the Azure DevOps MCP server in Antigravity to fetch Azure DevOps work items.

## 1. Prerequisites

Install Node.js and npm.

Check:

```powershell
node -v
npm -v
```

Install the Azure DevOps MCP server globally:

```powershell
npm install -g @azure-devops/mcp
```

Verify the installed command:

```powershell
where mcp-server-azuredevops
```

Expected output example:

```text
C:\nvm4w\nodejs\mcp-server-azuredevops
C:\nvm4w\nodejs\mcp-server-azuredevops.cmd
```

Use the `.cmd` path in Antigravity on Windows.

---

## 2. Create Azure DevOps PAT

Create a Personal Access Token from Azure DevOps.

Minimum recommended permission:

```text
Work Items: Read
```

Do not give full access unless required.

---

## 3. Encode PAT for MCP Server

The Azure DevOps MCP server expects the token in this format:

```text
base64(email:pat)
```

Use PowerShell:

```powershell
$raw = "your-email@example.com:YOUR_AZURE_DEVOPS_PAT"
$bytes = [System.Text.Encoding]::UTF8.GetBytes($raw)
[Convert]::ToBase64String($bytes)
```

Copy the generated base64 value.

---

## 4. Antigravity MCP Config

Open Antigravity MCP configuration:

```text
Agent Panel → MCP Servers → Manage MCP Servers → View raw config
```

Add this config:

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
        "PERSONAL_ACCESS_TOKEN": "REPLACE_WITH_BASE64_EMAIL_COLON_PAT"
      }
    }
  }
}
```

Replace:

```text
REPLACE_WITH_BASE64_EMAIL_COLON_PAT
```

with the generated base64 token.

---

## 5. Why This Config Is Faster

Do not use this slower config:

```json
"command": "cmd",
"args": [
  "/c",
  "npx",
  "--no-install",
  "@azure-devops/mcp",
  "infraon",
  "--authentication",
  "pat",
  "-d",
  "work-items"
]
```

Use the installed binary directly instead:

```json
"command": "C:\\nvm4w\\nodejs\\mcp-server-azuredevops.cmd"
```

This avoids `npx` startup overhead.

---

## 6. Tool Domain Restriction

The config uses:

```json
"-d", "work-items"
```

This loads only Azure DevOps work item tools.

Do not add repositories, pipelines, wiki, or other domains unless needed. Loading fewer tools makes the MCP server faster and easier for the agent to use correctly.

---

## 7. Test Prompt in Antigravity

Use a prompt like:

```text
Use the Azure DevOps MCP server to fetch work item 3762 from Azure DevOps.
Summarize the title, description, acceptance criteria, repro steps, RCA, test cases, and comments.
Then prepare an implementation plan.
Do not modify code until I approve the plan.
```

---

## 8. Recommended Skill Instruction

Add this to the Antigravity skill:

```text
When the user says "Implement work item <id>", use the Azure DevOps MCP server to fetch that specific work item.

Fetch the work item details and comments/discussion.

Include:
- title
- description
- acceptance criteria
- repro steps
- RCA
- test cases
- implementation notes
- impact analysis
- discussion/comments

After fetching the details, prepare an implementation plan.

Do not apply code changes until the user accepts the implementation plan.

After the user accepts the plan:
- apply the required changes
- test the changes
- ask the user for application username/password only if required for testing
```

---

## 9. Security Notes

Do not commit the MCP config if it contains the real token.

Do not share this value publicly:

```json
"PERSONAL_ACCESS_TOKEN": "..."
```

Use a PAT with minimum permissions, preferably only:

```text
Work Items: Read
```

Regenerate the PAT if it is exposed.
