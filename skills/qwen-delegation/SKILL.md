---
name: qwen-delegation
description: Qwen CLI delegation workflow with quota tracking, authentication, and usage logging. Utilizes shared shell execution infrastructure for consistent delegation patterns.
category: delegation-implementation
tags: [qwen, cli, delegation, quota-management, large-context, shell-execution]
dependencies: [delegation-core]
tools: [qwen-cli, delegation-executor, quota-tracker, usage-logger]
usage_patterns:
  - qwen-cli-integration
  - large-context-analysis
  - bulk-processing
  - multi-file-comparison
  - shell-delegation
complexity: intermediate
estimated_tokens: 1500
---

# Qwen CLI Delegation

## Overview

This skill implements `conjure:delegation-core` for the Qwen CLI using the shared shell execution infrastructure. It provides authentication, quota management, and Qwen-specific command construction with consistent delegation patterns.

## When to Use
- After `Skill(conjure:delegation-core)` determines Qwen is suitable.
- When you need Qwen's large context window (100K+ tokens).
- For batch processing, summarization, or multi-file analysis.
- For code generation and pattern extraction tasks.
- If the `qwen` CLI is installed and configured.

## Prerequisites

**CLI Installation:**
```bash
# Install Qwen CLI (if not already installed)
pip install qwen-cli

# Verify installation
qwen --version

# Check available models
qwen --help | grep -A 10 "model"
```

**Authentication Setup:**
```bash
# Check authentication status
qwen auth status

# Login if needed
qwen auth login

# Or set API key
export QWEN_API_KEY="your-key"

# Verify authentication
qwen "ping"  # Should respond successfully
```

**Service Configuration:**
- Update delegation configuration in `~/.claude/hooks/delegation/config.json`
- Set Qwen-specific quota limits and model preferences

## Delegation Flow
1. `qwen-delegation:auth-verified`: Verify authentication for Qwen CLI.
2. `qwen-delegation:quota-checked`: Check Qwen API quota and limits.
3. `qwen-delegation:command-executed`: Execute the command via Qwen CLI.
4. `qwen-delegation:usage-logged`: Log Qwen API usage.

## Step 1: Verify Authentication (`qwen-delegation:auth-verified`)

```bash
# Check authentication status
qwen auth status

# Test basic connectivity
qwen "Respond with 'OK'"

# Verify model access
qwen --model qwen-max "What model are you?"
```

If authentication fails:
- For interactive login: use `qwen auth login`
- For API key: Set the `QWEN_API_KEY` environment variable
- For model selection: Set `QWEN_MODEL` if not using default

## Step 2: Check Quota (`qwen-delegation:quota-checked`)

```bash
# Quick status using shared delegation executor
python ~/conjure/tools/delegation_executor.py verify qwen

# Check quota status
python ~/conjure/tools/delegation_executor.py usage --service qwen

# Comprehensive status check
make quota-status
```

**Quota Thresholds:**
- [OK] Healthy: Less than 80% usage
- [WARNING] Warning: 80-95% usage
- [CRITICAL] Critical: Over 95% usage (defer non-urgent tasks)

If quota is critical, consider:
- Waiting for rate limit reset
- Using a different service (Gemini)
- Breaking the task into smaller batches

## Step 3: Execute Command (`qwen-delegation:command-executed`)

**Using Shared Delegation Executor:**
```bash
# Basic file analysis
python ~/conjure/tools/delegation_executor.py qwen "Analyze this code" --files src/main.py

# With specific model
python ~/conjure/tools/delegation_executor.py qwen "Summarize these files" \
  --files src/**/*.py --model qwen-max

# With output format
python ~/conjure/tools/delegation_executor.py qwen "Extract functions" \
  --files src/main.py --format json
```

**Direct CLI Usage:**
```bash
# Basic file analysis
qwen -p "@path/to/file Analyze this code"

# Multiple files
qwen -p "@src/**/*.py Summarize these files"

# Specific model
qwen --model qwen-max -p "..."

# JSON output
qwen --format json -p "..."
```

**Context Inclusion:**
- Use `@path` to include file contents
- Use `@directory/**/*` for recursive inclusion
- Qwen handles large contexts well (100K+ tokens)

**Save Output:**
```bash
# Save to file for audit
qwen -p "..." > delegations/qwen/$(date +%Y%m%d_%H%M%S).md
```

## Step 4: Log Usage (`qwen-delegation:usage-logged`)

Usage is automatically logged by the shared delegation executor. For manual logging:
```bash
# Log manual usage
python ~/conjure/tools/usage_logger.py --log "qwen analysis" 50000 true 15

# View usage report
python ~/conjure/tools/delegation_executor.py usage

# Check recent usage
make usage-report
```

## Token Usage Estimates

**Qwen Model Capabilities:**
- **Context Window**: Up to 100K+ tokens for standard models
- **Cost Efficiency**: Varies by model tier, typically competitive with Gemini
- **Speed**: Fast models available for quick tasks, more capable models for complex analysis

**Task Token Estimates:**
- File analysis: 10-30 tokens per file + 150-400 for analysis
- Code summarization: 1-2% of original file size + 200-600 for summary
- Pattern extraction: 3-15 tokens per match + 80-200 for formatting
- Boilerplate generation: 40-150 tokens per template + output tokens

**Sample Delegation Costs:**
- Analyze 100 Python files (50K tokens): Competitive pricing
- Summarize large codebase (200K tokens): Cost-effective for bulk analysis
- Generate 50 API endpoints (3K output): Efficient for code generation

## Qwen CLI Reference

**Common Options:**
| Flag | Purpose |
|------|---------|
| `-p "prompt"` | Specify prompt |
| `--model <name>` | Select model |
| `--format <type>` | Output format (json, markdown) |
| `--temperature <0-1>` | Control randomness |
| `@path` | Include file in context |

**Models:**
- `qwen-turbo`: Fast, good for simple tasks
- `qwen-max`: More capable, larger context window
- `qwen-coder`: Specialized for code tasks (if available)

## Smart Delegation

The shared delegation executor can automatically select the best service:

```bash
# Auto-select best service based on requirements
python ~/conjure/tools/delegation_executor.py auto "Analyze large codebase" \
  --files src/**/* --requirement large_context

# Force specific service for comparison
python ~/conjure/tools/delegation_executor.py gemini "Quick analysis" --files src/main.py
python ~/conjure/tools/delegation_executor.py qwen "Detailed analysis" --files src/main.py
```

## Usage Monitoring and Analytics

**Real-time Monitoring:**
```bash
# Check current usage across all services
python ~/conjure/tools/delegation_executor.py usage

# Service-specific usage
python ~/conjure/tools/delegation_executor.py usage --service qwen
python ~/conjure/tools/delegation_executor.py usage --service gemini

# Usage for last N days
python ~/conjure/tools/delegation_executor.py usage --days 30
```

**Performance Analytics:**
- Success rates per service
- Average response times
- Token consumption patterns
- Error frequency and types
- Cost analysis

## Error Handling & Troubleshooting

### Common Error Scenarios

**Authentication Errors (HTTP 401/403)**
- **Quick Fix**: `qwen auth login` or verify `QWEN_API_KEY`
- **Check Permissions**: Ensure API key has necessary scopes
- **Token Refresh**: Re-authenticate if token expired
- **Regional Issues**: Some models available only in certain regions

**Rate Limit Errors (HTTP 429)**
- **Immediate Action**: Wait for rate limit reset
- **Investigation**: Run `python ~/conjure/tools/delegation_executor.py verify qwen`
- **Prevention**: Check quota before large tasks, batch requests
- **Alternative**: Consider gemini service if Qwen is rate-limited

**Context Too Large (HTTP 400)**
- **Diagnostic**: Estimate tokens: `python ~/conjure/tools/delegation_executor.py --estimate --files src/**/*`
- **Solutions**:
  - Use qwen-max for larger context windows
  - Split into multiple requests with selective file inclusion
  - Pre-process: remove comments, tests, or binary files
  - Use globbing patterns instead of recursive inclusion

**Model Unavailable (HTTP 404)**
- **Check Model**: `qwen --help | grep -A 10 "model"`
- **Alternative**: Use `qwen-turbo` for faster, smaller tasks
- **Version Issues**: Update qwen-cli to latest version

**Command Not Found**
- **Installation**: `pip install qwen-cli`
- **PATH Issues**: Ensure `~/.local/bin` is in PATH
- **Verification**: `which qwen` and `qwen --version`

### Performance Issues

**Slow Response Times**
- **Model Choice**: Use `qwen-turbo` for faster responses
- **Context Optimization**: Remove unnecessary files from `@` includes
- **Batch Processing**: Group multiple small queries into one request

**Inconsistent Results**
- **Temperature Setting**: Use `--temperature 0.0` for deterministic output
- **Seed Parameter**: Use `--seed` for reproducible results (if supported)
- **Prompt Engineering**: Be more specific and provide examples

### Debugging Tools

**Enable Debug Logging:**
```bash
export QWEN_DEBUG=1
qwen -p "test"  # Will show full request/response
```

**Test with Simple Request:**
```bash
qwen -p "Respond with 'OK'"  # Basic connectivity test
```

**Validate Configuration:**
```bash
# Test shared delegation executor
python ~/conjure/tools/delegation_executor.py list-services

# Verify qwen service
python ~/conjure/tools/delegation_executor.py verify qwen
```

## Integration with Existing Workflow

The updated qwen-delegation skill now uses the same patterns as gemini-delegation:

- **Consistent API**: Both services use `delegation_executor.py`
- **Unified Logging**: All usage logged to central location
- **Shared Quota Management**: Common quota tracking interface
- **Standardized Error Handling**: Consistent error patterns and recovery
- **Smart Service Selection**: Automatic service optimization

## Exit Criteria
- Authentication confirmed working.
- Quota checked and sufficient.
- Command executed successfully using shared infrastructure.
- Usage logged for tracking with unified analytics.
- Results validated and ready for integration.
