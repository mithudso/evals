# MCP applicability

This repository neither implements nor requires an MCP server. `.mcp.json` and
`.vscode/mcp.json` contain empty server maps. The Python CLI commands work without
MCP authentication, tokens, tool registration, or a running agent harness.

An operator may use external development tools, including a task tracker, but
those connections belong to the operator's environment. They are not runtime
dependencies of Evals and no repository tool inventory is implied.

If a future change adds an MCP server, document its actual command, tools,
authentication boundary, and tests here before adding configuration. Never commit
real credentials to an MCP configuration file.
