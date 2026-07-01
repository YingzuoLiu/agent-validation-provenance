# MCP File Memory Demo

A small, interview-oriented MCP demo for an enterprise Agent Platform scenario.

The project wraps a local file-memory knowledge base as MCP tools and adds the parts that matter in enterprise agent work:

- project-level access control
- safe file path resolution
- structured error payloads
- provenance metadata for retrieved memory
- Docker packaging
- stdlib unit tests for the backend logic

## Why this exists

In real Agent Platform work, MCP is often used to expose internal systems to agents through a standard tool interface.

This demo focuses on the common pattern:

```text
Agent Runtime
  -> MCP Client / Gateway
  -> MCP Server
  -> Internal File Memory / Knowledge Base
```

The implementation is intentionally small so the security and runtime boundaries are easy to inspect.

## Tools exposed by the MCP server

### `search_file_memory`

Searches project file memory after checking whether the user can access the project.

Input:

```json
{
  "user_id": "alice",
  "project_id": "project_alpha",
  "query": "refund policy",
  "top_k": 5
}
```

Returns matched file snippets plus provenance metadata:

```json
{
  "ok": true,
  "results": [
    {
      "path": "refund_policy.md",
      "score": 8.5,
      "snippet": "Project Alpha supports refund review...",
      "provenance": {
        "source_path": "refund_policy.md",
        "project_id": "project_alpha",
        "trust_level": "internal",
        "source_type": "file_memory",
        "access_checked": true
      }
    }
  ]
}
```

### `read_file_memory`

Reads one project file after ACL and path traversal checks.

Input:

```json
{
  "user_id": "alice",
  "project_id": "project_alpha",
  "relative_path": "refund_policy.md"
}
```

## Quick start: backend logic only

This path does not require the MCP package.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m unittest discover -s tests
python -m mcp_file_memory_demo.cli_demo --user alice --project project_alpha --query "refund policy"
```

Expected behavior:

- `alice` can search and read `project_alpha`
- `alice` cannot access `project_beta`
- path traversal such as `../project_beta/security_review.md` is blocked

## Run as an MCP server

Install the optional MCP dependency:

```bash
pip install -e ".[mcp]"
python -m mcp_file_memory_demo.server
```

By default it reads:

```bash
FILE_MEMORY_DATA_DIR=sample_data
ACL_PATH=config/acl.json
```

## Docker

```bash
docker build -t mcp-file-memory-demo .
docker run --rm -i mcp-file-memory-demo
```

For a production setup, this would usually run behind an MCP gateway or an agent runtime service rather than being called directly by a user.

## What this demo is meant to show

This is not meant to be a full retrieval system. The search function is intentionally simple lexical scoring so the demo stays dependency-light.

The important enterprise-agent ideas are:

1. Tool calls need identity and project context.
2. File memory should return provenance, not just text.
3. The tool server should reject cross-project access.
4. File reads must block path traversal.
5. MCP servers should be packaged and deployable as services.

## Next steps

Useful extensions:

- replace lexical search with BM25 + dense retrieval + RRF
- add document-level ACLs
- add an audit log for every tool call
- expose an HTTP transport behind a gateway
- store provenance edges in a trust graph
- add a reranker after candidate retrieval
