---
name: tdd-workflow
description: Use this skill when writing new features, fixing bugs, or refactoring code. Enforces test-driven development with 80%+ coverage including unit, integration, and E2E tests.
origin: ECC
---

# Test-Driven Development Workflow

## When to Activate

- Writing new features or functionality
- Fixing bugs or issues
- Refactoring existing code

## Core Principles

1. **Tests BEFORE Code** — always write tests first
2. **Coverage** — minimum 80% (unit + integration + E2E)
3. **Git Checkpoints** — commit after each TDD stage

## TDD Steps

### Step 1: Write User Journeys
```
As a [role], I want to [action], so that [benefit]
```

### Step 2: Write Failing Tests
```typescript
describe('Feature', () => {
    it('does expected thing', async () => { /* test */ })
    it('handles edge case', async () => { /* edge case */ })
    it('handles error', async () => { /* error path */ })
})
```

### Step 3: Run Tests (RED — they must fail)
```bash
npm test
# Tests should fail — RED gate mandatory
```
Commit: `test: add reproducer for <feature>`

### Step 4: Implement Minimal Code
Write just enough code to make tests pass.

### Step 5: Run Tests (GREEN)
```bash
npm test
# Tests must now pass
```
Commit: `fix: <feature>`

### Step 6: Refactor
Improve quality while keeping tests green.
Commit: `refactor: clean up after <feature>`

### Step 7: Verify Coverage
```bash
npm run test:coverage
# Must be 80%+
```

## Coverage Thresholds
```json
{
  "coverageThresholds": {
    "global": { "branches": 80, "functions": 80, "lines": 80 }
  }
}
```

## Anti-Patterns
- Writing code before tests
- Testing implementation details instead of behavior
- Brittle CSS selectors in E2E tests — use semantic selectors
- Tests that depend on each other
