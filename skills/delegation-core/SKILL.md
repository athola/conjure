---
name: delegation-core
description: Framework for delegating tasks to external LLM services, with a focus on strategic oversight and quality control.
category: delegation-framework
tags: [delegation, external-llm, gemini, qwen, task-management, quality-control]
dependencies: []
tools: []
usage_patterns:
  - task-assessment
  - delegation-planning
  - quality-validation
  - integration-workflows
complexity: intermediate
estimated_tokens: 1200
---

# Delegation Core Framework

## Overview

A structured method for deciding when, what, and how to delegate tasks to external LLM services (Gemini, Qwen, local models, etc.). This approach helps maintain quality control and strategic oversight. The core principle: delegate execution, retain Claude's intelligence.

## When to Use
- Before invoking any external LLM for task assistance.
- When operations are token-heavy and exceed local context limits.
- When batch processing benefits from different model characteristics.
- When tasks require routing between models.

## Philosophy

**Delegate execution, retain intelligence:**
- **Claude handles**: Architecture, strategy, design decisions, complex reasoning, quality review.
- **External LLMs perform**: Data processing, pattern extraction, bulk operations, summarization.

## Delegation Flow
1. `delegation-core:task-assessed`: Assess the task for delegation suitability.
2. `delegation-core:delegation-suitability`: Determine if delegation to an external LLM is appropriate.
3. `delegation-core:handoff-planned`: Plan the handoff to the external LLM.
4. `delegation-core:results-integrated`: Integrate results from the external LLM.

## Step 1: Assess the Task (`delegation-core:task-assessed`)

Classify the task along two dimensions:

**Intelligence Level:**
- **High Intelligence** (keep local): Architecture analysis, design decisions, trade-off evaluation, strategic recommendations, nuanced code review, creative problem solving.
- **Low Intelligence** (delegate): Pattern counting, bulk extraction, boilerplate generation, large-file summarization, repetitive transformations.

**Context Requirements:**
- **Large Context** (favor delegation): Multi-file analysis, codebase-wide searches, log processing.
- **Small Context** (either): Single-file operations, focused queries.

**Decision Matrix:**
| Intelligence | Context | Recommendation |
|-------------|---------|----------------|
| High | Any | Keep local |
| Low | Large | Delegate |
| Low | Small | Either |

Record: task objective, files involved, intelligence level, context size, failure impact.

## Token Usage Estimates

**Low Intelligence Tasks (Good for Delegation):**
- Pattern counting across files: 10-50 tokens/file
- Bulk data extraction: 20-100 tokens/file
- Boilerplate generation: 100-500 tokens/template
- Large file summarization: 1-5% of file size tokens

**Context Size Estimations:**
- Single Python file (500 lines): ~2,000-3,000 tokens
- Small module (10 files): ~15,000-25,000 tokens
- Medium project (50 files): ~75,000-150,000 tokens
- Large codebase (200+ files): 300,000+ tokens

**Delegation Thresholds:**
- **Efficient to delegate**: >25,000 total tokens or >50 files
- **Consider delegation**: 10,000-25,000 tokens or 20-50 files
- **Keep local**: <10,000 tokens and <20 files

## Cost Estimation Guidelines

### Service Cost Comparisons

**Gemini 2.0 Models (per 1M tokens):**
- Input: $0.50, Output: $1.50 (Pro version)
- Input: $0.075, Output: $0.30 (Flash version)
- Context: Up to 1M tokens

**Qwen Models (per 1M tokens):**
- Input: $0.20-0.50, Output: $0.60-1.20 (varies by provider)
- Context: Up to 100K+ tokens
- Sandbox execution: Typically $0.001-0.01 per request

### Cost Decision Framework

**Calculate Cost-Benefit Ratio:**
```
Cost = (input_tokens * input_rate) + (output_tokens * output_rate)
Benefit = time_saved * hourly_rate + quality_improvement_value

Delegate if: Benefit > Cost * 3 (safety margin for quality risks)
```

### Practical Cost Examples

**Low-Cost Delegations (<$0.01):**
- Count function occurrences: 50 files × 30 tokens = $0.000015
- Extract import statements: 100 files × 50 tokens = $0.000025
- Generate 10 boilerplate files: ~2K output tokens = $0.003

**Medium-Cost Delegations ($0.01-0.10):**
- Summarize 50K lines of code: ~125K tokens = $0.06-0.19
- Analyze architecture of 100 files: ~80K tokens = $0.04-0.12
- Generate 20 API endpoints: ~3K output tokens = $0.005

**High-Cost Delegations ($0.10+):**
- Review entire codebase (500K+ tokens): $0.25-0.75
- Generate comprehensive documentation: $0.15-0.45
- Complex refactoring analysis: $0.20-0.60

### Cost Optimization Strategies

**Input Optimization:**
- Remove comments, tests, examples when not needed
- Use selective file patterns instead of entire directories
- Pre-filter with grep/awk for relevant content
- Compress multiple small queries into one request

**Model Selection:**
- Use Flash/cheaper models for simple extraction tasks
- Reserve Pro models for complex analysis only
- Consider batch processing for repetitive tasks

**Alternative Strategies:**
- Break large tasks into smaller, targeted analyses
- Use local processing for sensitive operations
- Cache results for repeated analysis requests

### Cost Monitoring

**Set Daily/Weekly Budgets:**
- Development: $1-5/day
- Batch processing: $10-50/month
- Enterprise: $100-500/month

**Tracking Methods:**
- Use built-in usage logging tools
- Monitor API dashboard for consumption
- Set up alerts for unexpected spikes

## Step 2: Evaluate Delegation Suitability (`delegation-core:delegation-suitability`)

**Check Prerequisites:**
- [ ] Authenticate and ensure external service is reachable.
- [ ] Confirm quota/rate limits have capacity for the task.
- [ ] Verify task does not involve sensitive data requiring local processing.
- [ ] Ensure expected output format is well-defined.

**Evaluate Service Fit:**
- Does the external model excel at this task type?
- Is the latency acceptable for the workflow?
- Can results be easily validated?

**Red Flags (stay local):**
- Security-sensitive operations (auth, crypto, secrets).
- Tasks requiring real-time iteration.
- Complex multi-step reasoning chains.
- Subjective quality judgments.

## Step 3: Plan the Handoff (`delegation-core:handoff-planned`)

**Formulate the Request:**
1. Write a clear, self-contained prompt.
2. Include all necessary context (files, constraints, examples).
3. Specify the exact output format expected.
4. Define success criteria for validation.

**Document the Plan:**
```markdown
## Delegation Plan
- **Service**: [Gemini CLI / Qwen MCP / Other]
- **Command/Call**: [Exact invocation]
- **Input Context**: [Files, data provided]
- **Expected Output**: [Format, content type]
- **Validation Method**: [How to verify correctness]
- **Contingency**: [What to do if delegation fails]
```

## Step 4: Execute and Integrate (`delegation-core:results-integrated`)

**Execute:**
1. Run the delegation with the planned command.
2. Capture full output (save to file for audit trail).
3. Log usage metrics (tokens, duration, success/failure).

**Validate:**
- Does output match the expected format?
- Are results factually plausible?
- Do code suggestions compile/lint?
- Are there obvious errors or hallucinations?

**Integrate:**
- Apply results only after validation.
- Document what was delegated and the outcome.
- Note lessons learned for future delegations.

## Collaborative Workflows

For complex tasks requiring both intelligence AND scale:

```
1. Claude: Define framework, criteria, evaluation rubric
2. External: Process data, extract patterns, generate candidates
3. Claude: Analyze results, make decisions, provide recommendations
```

**Example - Large Codebase Review:**
1. Claude: Define architectural principles to evaluate
2. Gemini: Catalog all modules, extract dependency graphs
3. Claude: Analyze patterns against principles, recommend changes

## Anti-Patterns

**Don't delegate:**
- "Review this code and tell me if it's good" (intelligence task)
- "What's the best architecture for X?" (strategic decision)
- "Fix the bugs in this file" (requires understanding intent)

**Do delegate:**
- "List all functions in these 50 files" (extraction)
- "Count occurrences of pattern X across codebase" (counting)
- "Generate boilerplate for these 20 endpoints" (templating)

## Integration Notes

- Use service-specific skills for detailed workflows:
  - `Skill(conjure:gemini-delegation)` - Gemini CLI specifics
  - `Skill(conjure:qwen-delegation)` - Qwen MCP specifics
- Log all delegations for pattern analysis.
- Monitor quotas to prevent service exhaustion.

## Troubleshooting

### Delegation Decision Issues

**Problem: Uncertain whether to delegate**
- **Solution**: Use the decision matrix. If high intelligence required, keep local.
- **Check**: Does this task require understanding intent, context, or making judgments?

**Problem: Delegated task produces poor results**
- **Common Causes**:
  - Task was actually high-intelligence (reclassify)
  - Instructions were ambiguous (make more specific)
  - Context was insufficient (add more examples)
  - Wrong tool for the job (try different service)

**Problem: External service fails unexpectedly**
- **Immediate**: Default to local processing
- **Investigation**: Check authentication, quotas, service status
- **Prevention**: Validate prerequisites before delegation

### Quality Control Issues

**Problem: Can't validate delegated results**
- **Solution**: Break task into smaller, verifiable chunks
- **Alternative**: Include self-validation in the delegation prompt
- **Prevention**: Always define success criteria before delegating

**Problem: Results integrate poorly**
- **Common Causes**:
  - Output format mismatch (specify exact format)
  - Style inconsistencies (provide style examples)
  - Missing context (include integration patterns)

## Exit Criteria
- Task assessed and classified correctly.
- Delegation decision justified with clear rationale.
- Results validated before integration.
- Lessons captured for future delegations.
