---
name: qwen-delegation
description: Qwen MCP-specific delegation workflow utilizing Qwen's large context window and sandbox capabilities.
category: delegation-implementation
tags: [qwen, mcp, delegation, large-context, sandbox, code-execution]
dependencies: [delegation-core]
tools: [qwen-code-mcp, mcp-client]
usage_patterns:
  - mcp-integration
  - large-file-analysis
  - sandbox-execution
  - multi-file-comparison
complexity: intermediate
estimated_tokens: 1300
---

# Qwen MCP Delegation

## Overview

This skill implements `conjure:delegation-core` for Qwen via MCP (Model Context Protocol). It handles Qwen-specific invocation patterns and utilizes its large context window.

## When to Use
- After `Skill(conjure:delegation-core)` determines delegation is suitable.
- When you need Qwen's large context window.
- For sandbox code execution in an isolated environment.
- For bulk code generation or file analysis.
- If the Qwen MCP server is configured and accessible.

## Prerequisites

**MCP Configuration:**
Ensure Qwen is configured in your MCP settings (typically `~/.claude/mcp.json` or project settings).

**Verify Connectivity:**
```bash
# Test MCP tool availability
claude-code status  # Should show qwen-code tools listed

# Alternative verification via MCP client
mcp list-tools | grep qwen-code

# Direct tool test
claude-code -c "Use qwen-code:ask-qwen to test connectivity"
```

## Delegation Flow
1. `qwen-delegation:mcp-verified`: Verify Qwen MCP (Multi-Cloud Platform) access.
2. `qwen-delegation:context-prepared`: Prepare context for Qwen.
3. `qwen-delegation:request-executed`: Execute the request via Qwen.
4. `qwen-delegation:output-reviewed`: Review Qwen's output.

## Step 1: Verify MCP Connection (`qwen-delegation:mcp-verified`)

Check that Qwen MCP tools are available:
- `qwen-code:ask-qwen`: General queries.
- `qwen-code:sandbox`: Isolated code execution (if available).

**Verification Commands:**
```bash
# List available MCP tools
claude-code --list-tools | grep qwen

# Test basic connectivity
qwen-code:ask-qwen "Hello, can you respond with 'MCP connection successful'?"

# Check Qwen model info
qwen-code:ask-qwen "What model are you and what are your context limits?"
```

If tools aren't visible, verify MCP server configuration:
```bash
# Check MCP server status
systemctl --user status mcp-server

# Restart MCP server if needed
systemctl --user restart mcp-server

# Verify configuration file
cat ~/.claude/mcp.json | jq '.servers[].name' | grep qwen
```

## Step 2: Prepare Context (`qwen-delegation:context-prepared`)

**Formulate the Request:**
- Write a clear, self-contained prompt.
- Include all necessary file references using `@path` syntax.
- Specify the expected output format.
- Note any constraints or requirements.

**Context Guidelines:**
- Qwen handles very large contexts well.
- Use `@` references for file inclusion.
- Be explicit about output format expectations.

**Example Context:**
```
Analyze @src/main.rs and @src/lib.rs
List all public functions with their signatures
Output as a markdown table with columns: Function, Arguments, Return Type
```

## Step 3: Execute Request (`qwen-delegation:request-executed`)

**Basic Query:**
```
/qwen-code:ask-qwen "Analyze @src/main.rs for potential improvements"
```

**With Multiple Files:**
```
/qwen-code:ask-qwen "Compare @old/module.py with @new/module.py and list differences"
```

**Sandbox Execution (if available):**
```
/qwen-code:sandbox "Run this Python code in isolation: ..."
```

**Best Practices:**
- Include all necessary context in a single request.
- Be specific about the expected output format.
- Provide examples if output structure matters.

## Step 4: Review and Integrate (`qwen-delegation:output-reviewed`)

**Validation Checklist:**
- [ ] Output matches expected format.
- [ ] Code suggestions are syntactically correct.
- [ ] Factual claims are plausible.
- [ ] No obvious hallucinations or errors.

**Integration:**
- Apply only validated results.
- Adapt to local code style if needed.
- Run tests/linting on any code changes.

**Document:**
- What was delegated.
- What was returned.
- What was integrated vs. discarded.

## Qwen Strengths

**Good For:**
- Very large file analysis (100K+ lines).
- Multi-file comparisons.
- Bulk code generation.
- Pattern extraction across codebases.
- Explanations of complex code.
- Sandbox experimentation.

**Less Suitable For:**
- Tasks requiring external tool access.
- Real-time iterative development.
- Security-sensitive operations.
- Tasks needing specific local context.

## Error Handling & Troubleshooting

### MCP Connection Issues

**Tools Not Visible**
- **Check Server Status**: `systemctl --user status mcp-server`
- **Verify Configuration**: `cat ~/.claude/mcp.json | jq '.servers[] | select(.name | contains("qwen"))'`
- **Restart Service**: `systemctl --user restart mcp-server`
- **Manual Test**: `mcp list-tools | grep qwen`

**Connection Timeouts**
- **Network Issues**: Test basic connectivity to MCP server
- **Port Conflicts**: Check if another service is using the MCP port
- **Resource Limits**: Monitor system resources: `htop | grep mcp`
- **Configuration Errors**: Validate JSON syntax: `jq . ~/.claude/mcp.json`

### Delegation-Specific Issues

**Context Window Exceeded**
- **Qwen Advantage**: Qwen typically handles 100K+ tokens, verify model limits
- **Diagnostic**: Use `/qwen-code:ask-qwen "What is your context window size?"`
- **Solutions**:
  - Split large files: `split -l 1000 large_file.py part_`
  - Use selective analysis: `@src/main.rs @src/lib.rs` instead of `@src/**/*`
  - Pre-filter content: Remove comments, tests, or examples if not needed

**Poor Quality Results**
- **Prompt Optimization**: Include output format examples
- **Context Enrichment**: Add style guides or similar examples
- **Step-by-Step**: Break complex analysis into sequential questions
- **Validation**: Ask Qwen to self-check its work

**Sandbox Execution Failures**
- **Permission Issues**: Check file system permissions for working directory
- **Missing Dependencies**: Verify required packages are installed in sandbox
- **Timeout Issues**: Break long-running code into smaller chunks
- **Resource Limits**: Monitor memory/CPU usage during execution

### Performance Issues

**Slow Response Times**
- **Model Selection**: Check if faster model variants are available
- **Context Optimization**: Minimize @file inclusions to essential content
- **Batch Operations**: Combine multiple related questions into single request

**Inconsistent Output Format**
- **Explicit Instructions**: Specify exact output format with examples
- **JSON Mode**: If available, use structured output mode
- **Post-Processing**: Plan for output cleanup if needed

### Debugging Tools

**MCP Diagnostic Commands:**
```bash
# Check MCP server logs
journalctl --user -u mcp-server -f

# Test tool availability
mcp call-tool qwen-code:ask-qwen '{"prompt": "test"}'

# Monitor resource usage
watch -n 1 'ps aux | grep -E "(mcp|qwen)"'
```

**Qwen Model Information:**
```bash
# Check available models
/qwen-code:ask-qwen "What model are you? What are your capabilities and limits?"

# Test basic functionality
/qwen-code:ask-qwen "Analyze this simple Python function and explain what it does: def add(a, b): return a + b"
```

## Integration Notes

- Use `delegation-core` for task assessment before invoking.
- Validate results before integration.
- Document delegations for pattern analysis.
- Consider latency for time-sensitive workflows.

## Exit Criteria
- MCP connection verified.
- Context prepared with all necessary information.
- Request executed successfully.
- Output reviewed and validated before integration.
