# Agent Validation Provenance

An independent architecture exploration inspired by the discussion in [`guardrails-ai/guardrails#1448`](https://github.com/guardrails-ai/guardrails/issues/1448): **when a runtime validator fixes an LLM output, should that mutation be silent, or should it be observable and auditable?**

This project explores a validation design for long-running agent systems where validator actions are not treated as hidden output filters, but as explicit state transitions with provenance.

## Motivation
