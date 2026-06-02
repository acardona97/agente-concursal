# /ship — Feature Ship Pipeline

Runs the 4-agent pipeline: Planner → Coder → Tester → Reviewer.

## Usage

```
/ship <feature description>
```

## Pipeline

```
Planner (Opus)  →  .pipeline/spec.md
     ↓
Coder (Sonnet)  →  source changes + .pipeline/changes.md
     ↓
Tester (Sonnet) →  .pipeline/test-results.md
     ↓
Reviewer (Opus) →  .pipeline/review.md
```

## Steps

1. **Planner** — reads the feature request, writes `.pipeline/spec.md`
   - Agent: `.claude/agents/planner.md`
   - Done signal: `SPEC_DONE`

2. **Coder** — reads spec, implements changes, writes `.pipeline/changes.md`
   - Agent: `.claude/agents/coder.md`
   - Done signal: `CODE_DONE`

3. **Tester** — reads spec + changes, verifies acceptance criteria, writes `.pipeline/test-results.md`
   - Agent: `.claude/agents/tester.md`
   - Done signal: `TEST_DONE: SHIP` or `TEST_DONE: BLOCK`

4. **Reviewer** — reads all pipeline files + source, makes final call, writes `.pipeline/review.md`
   - Agent: `.claude/agents/reviewer.md`
   - Done signal: `REVIEW_DONE: APPROVE` or `REVIEW_DONE: REQUEST_CHANGES`

## Pipeline Directory

All handoff files live in `.pipeline/` (git-ignored by default):
```
.pipeline/
  spec.md           ← Planner output
  changes.md        ← Coder output
  test-results.md   ← Tester output
  review.md         ← Reviewer output
```

## Abort Conditions

- If Tester outputs `TEST_DONE: BLOCK`, Reviewer must address the block before APPROVE.
- If Reviewer outputs `REQUEST_CHANGES`, the pipeline stops — fix the issues and re-run `/ship`.

## Example

```
/ship add PDF export button to the analysis view
```

This runs all 4 agents sequentially. You can watch progress via the done signals.
