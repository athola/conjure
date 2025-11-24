---
name: gemini-delegation
description: Gemini CLI delegation workflow with quota tracking, authentication, and usage logging.
category: delegation-implementation
tags: [gemini, cli, delegation, quota-management, authentication, api-usage]
dependencies: [delegation-core]
tools: [gemini-cli, quota-tracker, usage-logger]
usage_patterns:
  - gemini-cli-integration
  - quota-monitoring
  - batch-processing
  - large-context-analysis
complexity: intermediate
estimated_tokens: 1500
---

# Gemini CLI Delegation

## Overview

This skill implements `conjure:delegation-core` for the Gemini CLI. It provides authentication, quota management, and Gemini-specific command construction.

## When to Use
- After `Skill(conjure:delegation-core)` determines Gemini is suitable.
- When you need Gemini's large context window (1M+ tokens).
- For batch processing, summarization, or pattern extraction tasks.
- If the `gemini` CLI is installed and authenticated.

## Prerequisites

**Authentication:**
```bash
# Check status
gemini auth status

# Login if needed
gemini auth login

# Or set API key
export GEMINI_API_KEY="your-key"
```

**Quota Awareness:**
- Free tier: ~60 RPM, ~1000 requests/day, ~1M tokens/day
- Check status: `conjure status` or `python3 ~/conjure/tools/quota_tracker.py`

## Delegation Flow
1. `gemini-delegation:auth-verified`: Verify authentication for Gemini.
2. `gemini-delegation:quota-checked`: Check Gemini API quota.
3. `gemini-delegation:command-executed`: Execute the command via Gemini.
4. `gemini-delegation:usage-logged`: Log Gemini API usage.

## Step 1: Verify Authentication (`gemini-delegation:auth-verified`)

```bash
gemini auth status
# Or smoke test
gemini "ping"
```

If authentication fails:
- For interactive login: use `gemini auth login` (opens browser).
- For API key: Set the `GEMINI_API_KEY` environment variable.
- For model selection: Set `GEMINI_MODEL` if not using default.

## Step 2: Check Quota (`gemini-delegation:quota-checked`)

```bash
# Quick status
~/conjure/hooks/gemini/status.sh

# Detailed quota analysis
python3 ~/conjure/tools/quota_tracker.py
```

**Quota Thresholds:**
- [OK] Healthy: Less than 80% usage.
- [WARNING] Warning: 80-95% usage.
- [CRITICAL] Critical: Over 95% usage (defer non-urgent tasks).

If quota is critical, consider:
- Waiting for rate limit reset (1 minute for RPM).
- Deferring to next day for daily limits.
- Breaking the task into smaller batches.

## Step 3: Execute Command (`gemini-delegation:command-executed`)

**Command Construction:**
```bash
# Basic file analysis
gemini -p "@path/to/file Analyze this code"

# Multiple files
gemini -p "@src/**/*.py Summarize these files"

# Specific model
gemini --model gemini-2.5-pro-exp -p "..."

# JSON output
gemini --output-format json -p "..."
```

**Context Inclusion:**
- Use `@path` to include file contents.
- Use `@directory/**/*` for recursive inclusion.
- Gemini handles large contexts well (1M+ tokens).

**Save Output:**
```bash
# Save to file for audit
gemini -p "..." > delegations/gemini/$(date +%Y%m%d_%H%M%S).md
```

## Step 4: Log Usage (`gemini-delegation:usage-logged`)

After execution, log the usage:
```bash
python3 ~/conjure/tools/usage_logger.py "<command>" <estimated_tokens> <success:true/false> <duration_seconds>
```

**Example:**
```bash
python3 ~/conjure/tools/usage_logger.py "gemini -p '@src/ analyze'" 50000 true 12
```

## Token Usage Estimates

**Gemini Model Capabilities:**
- **Context Window**: Up to 1M tokens for 2.0 models
- **Cost Efficiency**: ~$0.50/1M input tokens, ~$1.50/1M output tokens
- **Speed**: 2.0-flash ~2-3x faster than 2.0-pro

**Task Token Estimates:**
- File analysis: 15-50 tokens per file + 200-500 for analysis
- Code summarization: 1-3% of original file size + 300-800 for summary
- Pattern extraction: 5-20 tokens per match + 100-300 for formatting
- Boilerplate generation: 50-200 tokens per template + output tokens

**Sample Delegation Costs:**
- Analyze 100 Python files (50K tokens): ~$0.025
- Summarize large codebase (200K tokens): ~$0.10
- Generate 20 API endpoints (2K output): ~$0.003

## Gemini CLI Reference

**Common Options:**
| Flag | Purpose |
|------|---------|
| `-p "prompt"` | Specify prompt. |
| `--model <name>` | Select model. |
| `--output-format json` | JSON output. |
| `-s` | Sandbox mode. |
| `@path` | Include file in context. |

**Models:**
- `gemini-2.5-flash-exp`: Fast, good for simple tasks.
- `gemini-2.5-pro-exp`: More capable, higher latency.
- `gemini-exp-1206`: Experimental features.

## Quota Monitoring

**During Session:**
```bash
# Quick overview
~/conjure/hooks/gemini/status.sh

# After heavy usage
python3 ~/conjure/tools/quota_tracker.py
```

**View History:**
```bash
# Recent errors
python3 -c "
from usage_logger import GeminiUsageLogger
logger = GeminiUsageLogger()
print(logger.get_recent_errors())
"
```

## Error Handling & Troubleshooting

### Common Error Scenarios

**Rate Limit Errors (HTTP 429)**
- **Immediate Action**: Wait 60 seconds for RPM reset
- **Investigation**: Run `~/conjure/hooks/gemini/status.sh`
- **Prevention**: Check quota before large tasks, batch requests
- Workaround: Consider `gemini-2.5-flash` to reduce RPM usage.

**Authentication Errors (HTTP 401/403)**
- **Quick Fix**: `gemini auth login` or verify `GEMINI_API_KEY`
- **Check Permissions**: Ensure API key has necessary scopes
- **Browser Issues**: Clear cache, try incognito for OAuth flow
- **Corporate Networks**: May need proxy configuration

**Context Too Large (HTTP 400)**
- **Diagnosis**: Check token count: `wc -c file.txt | awk '{print $1/4}'`
- **Solutions**:
  - Split into multiple requests with `@file1 @file2` patterns
  - Use selective globbing: `src/**/*.py` instead of `src/**/*`
  - Pre-process: `grep -v "^\s*#" file.py` to remove comments

**Model Unavailable (HTTP 404)**
- **Check Model**: `gemini --help | grep -A 10 "model"`
- **Alternative**: Use `gemini-2.5-flash-exp` as a secondary option
- **Region Issues**: Some models available only in certain regions

**Network/Connection Issues**
- **Test Connectivity**: `curl -I https://generativelanguage.googleapis.com`
- **Timeouts**: Increase with environment variable `GEMINI_TIMEOUT=60`
- **Proxy Settings**: Use `HTTPS_PROXY` and `HTTP_PROXY` if required

### Performance Issues

**Slow Response Times**
- **Model Choice**: Use `gemini-2.5-flash-exp` for faster responses
- **Context Optimization**: Remove unnecessary files from `@` includes
- **Batch Processing**: Group multiple small queries into one request

**Inconsistent Results**
- **Temperature Setting**: Use `--temperature 0.0` for deterministic output
- **Seed Parameter**: Use `--seed` for reproducible results (if supported)
- **Prompt Engineering**: Be more specific in instructions

### Debugging Tools

**Enable Debug Logging:**
```bash
export GEMINI_DEBUG=1
gemini -p "test"  # Will show full request/response
```

**Test with Simple Request:**
```bash
gemini -p "Respond with 'OK'"  # Basic connectivity test
```

## Integration Notes

- Hooks in `~/conjure/hooks/gemini/` provide automatic suggestions.
- Validate results before integration (see `delegation-core`).
- Save delegation outputs for audit trail.

## Exit Criteria
- Authentication confirmed working.
- Quota checked and sufficient.
- Command executed successfully.
- Usage logged for tracking.
