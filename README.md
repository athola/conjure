# Conjure: An Intelligent Delegation Framework

Conjure is a framework for intelligently delegating tasks to external LLM services. It provides a structured approach to decide when, what, and how to use these services (e.g., Gemini, Qwen, local models) while ensuring strategic control and quality. The core principle is to **delegate execution while retaining the essential intelligence** within Claude.

## Philosophy

Claude handles:
- Architecture, strategy, and design decisions.
- Complex reasoning and quality review.

External LLMs are used for:
- Data processing and pattern extraction.
- Bulk operations and summarization.

## Skills

### Core Framework

#### delegation-core
Framework for intelligently delegating tasks to external LLM services.

**When to Use:**
- Before invoking any external LLM for task assistance
- When facing token-heavy operations that exceed local context
- When batch processing would benefit from different model characteristics

**Delegation Flow:**
1. `delegation-core:task-assessed`: Assess the task for delegation suitability.
2. `delegation-core:delegation-suitability`: Determine if delegation to an external LLM is appropriate.
3. `delegation-core:handoff-planned`: Plan the handoff to the external LLM.
4. `delegation-core:results-integrated`: Integrate results from the external LLM.

### Service-Specific Implementations

#### gemini-delegation
Gemini CLI-specific delegation with quota tracking and authentication.

**When to Use:**
- After `delegation-core` determines Gemini is suitable
- When you need Gemini's large context window (1M+ tokens)
- For batch processing, summarization, or pattern extraction

**Delegation Flow:**
1. `gemini-delegation:auth-verified`: Verify authentication for Gemini.
2. `gemini-delegation:quota-checked`: Check Gemini API quota.
3. `gemini-delegation:command-executed`: Execute the command via Gemini.
4. `gemini-delegation:usage-logged`: Log Gemini API usage.

#### qwen-delegation
Qwen MCP-specific delegation leveraging massive context and sandbox capabilities.

**When to Use:**
- After `delegation-core` determines Qwen is suitable
- When you need Qwen's massive context window
- For sandbox code execution in isolated environment

**Delegation Flow:**
1. `qwen-delegation:mcp-verified`: Verify Qwen MCP (Multi-Cloud Platform) access.
2. `qwen-delegation:context-prepared`: Prepare context for Qwen.
3. `qwen-delegation:request-executed`: Execute the request via Qwen.
4. `qwen-delegation:output-reviewed`: Review Qwen's output.

## Plugin Structure

```
conjure/
├── plugin.json              # Plugin configuration
├── README.md               # This file
├── skills/
│   ├── delegation-core/    # Core delegation framework
│   ├── gemini-delegation/  # Gemini CLI specifics
│   └── qwen-delegation/    # Qwen MCP specifics
├── hooks/
│   └── gemini/             # Gemini-specific hooks
│       ├── bridge.on_tool_start
│       └── bridge.after_tool_use
├── tools/
│   ├── quota_tracker.py    # Quota monitoring
│   └── usage_logger.py     # Usage logging
└── bin/
    └── status.sh           # Quick status check
```

## Usage

```bash
# Core delegation assessment
Skill(conjure:delegation-core)

# Service-specific workflows
Skill(conjure:gemini-delegation)
Skill(conjure:qwen-delegation)

# Quick status check
~/conjure/bin/status.sh
```

## Decision Matrix

| Intelligence | Context | Recommendation |
|-------------|---------|----------------|
| High | Any | Keep local (Claude) |
| Low | Large | Delegate |
| Low | Small | Either (prefer local) |

## What to Delegate

**Good for Delegation:**
- Pattern counting, bulk extraction
- Boilerplate generation
- Large-file summarization
- Repetitive transformations
- Multi-file comparisons

**Keep Local:**
- Architecture analysis
- Design decisions
- Trade-off evaluation
- Nuanced code review
- Creative problem solving

## Dependencies

None (foundational plugin)

## License

MIT License
