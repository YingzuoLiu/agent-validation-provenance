# Agent Validation Provenance

An independent architecture exploration inspired by the discussion in [`guardrails-ai/guardrails#1448`](https://github.com/guardrails-ai/guardrails/issues/1448): **when a runtime validator fixes an LLM output, should that mutation be silent, or should it be observable and auditable?**

This project explores a validation design for long-running agent systems where validator actions are not treated as hidden output filters, but as explicit state transitions with provenance.

## Motivation

Many LLM guardrail systems support actions such as `LOG`, `FIX`, `REASK`, or `EXCEPTION`.

These actions are useful for production systems, but `FIX` introduces a key issue: mutation is often silent.

In long-running agents, this leads to state drift:

- model output is modified
- downstream systems only see modified output
- original intent is lost
- memory may store already-altered data

## Core Idea

We treat validation as a **first-class runtime stage** that produces observable state transitions.

Instead of:

```
LLM → Validator (silent fix) → Final Output
```

We use:

```
LLM → Validator → StatePatch → Reducer → Final Output + Provenance
```

## Validation Actions

```python
PASS
LOG
QUARANTINE
FIX
REASK
EXCEPTION
```

### QUARANTINE
Intermediate state for uncertain validation results.

- does not mutate output
- flags field as unstable
- may escalate to EXCEPTION if repeated

## StatePatch Model

Each mutation is recorded:

```json
{
  "field": "hotel.price",
  "validator": "budget_validator",
  "action": "FIX",
  "before": "320",
  "after": "280",
  "confidence": 0.81,
  "reason": "budget constraint",
  "timestamp": "2026-06-24"
}
```

## Provenance Tracking

We compute how much of the final output was modified:

- raw_model_fields
- fixed_fields
- quarantined_fields
- mutation_ratio

## Example Runtime Flow

```
Planner → Executor → Validator → Patch Log → Reducer → Output
```

## Why This Matters

In agent systems:

- outputs become future inputs
- silent correction creates hidden state shifts
- debugging becomes impossible without trace

This design makes validation **observable and replayable**.

## Comparison

| System | Role | Limitation |
|--------|------|------------|
| Guardrails | runtime validation | FIX is opaque |
| RAGAS | evaluation | post-hoc only |
| TruLens | observability | not runtime control |
| LangGraph | orchestration | no native validation semantics |
| This project | runtime provenance | experimental |

## Next Steps

- implement ValidationEngine
- add replayable traces
- integrate with agent runtime (planner/executor/validator)
- simulate drift scenarios

## Status

Early-stage design + reference implementation.