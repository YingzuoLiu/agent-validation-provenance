from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import copy
from datetime import datetime


class ValidationAction(str, Enum):
    PASS = "PASS"
    LOG = "LOG"
    QUARANTINE = "QUARANTINE"
    FIX = "FIX"
    REASK = "REASK"
    EXCEPTION = "EXCEPTION"


@dataclass
class ValidationPatch:
    field: str
    validator: str
    action: ValidationAction
    before: Any
    after: Any
    confidence: float
    reason: str = ""
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "field": self.field,
            "validator": self.validator,
            "action": self.action.value,
            "before": self.before,
            "after": self.after,
            "confidence": self.confidence,
            "reason": self.reason,
            "timestamp": self.timestamp,
        }


@dataclass
class ValidationOutcome:
    raw_output: Dict[str, Any]
    final_output: Dict[str, Any]
    patches: List[ValidationPatch] = field(default_factory=list)
    status: ValidationAction = ValidationAction.PASS

    def add_patch(self, patch: ValidationPatch):
        self.patches.append(patch)

    def to_dict(self):
        return {
            "raw_output": self.raw_output,
            "final_output": self.final_output,
            "status": self.status.value,
            "patches": [p.to_dict() for p in self.patches],
            "provenance": compute_provenance(self.raw_output, self.final_output, self.patches),
        }


class ValidationEngine:
    def __init__(self, validators: Optional[List[Callable]] = None):
        self.validators = validators or []

    def validate(self, output: Dict[str, Any]) -> ValidationOutcome:
        raw = copy.deepcopy(output)
        current = copy.deepcopy(output)
        outcome = ValidationOutcome(raw_output=raw, final_output=current)

        for validator in self.validators:
            result = validator(current)

            if not result:
                continue

            if isinstance(result, ValidationPatch):
                outcome.add_patch(result)

                # apply mutation if FIX
                if result.action == ValidationAction.FIX:
                    self._set_field(current, result.field, result.after)

                if result.action == ValidationAction.QUARANTINE:
                    outcome.status = ValidationAction.QUARANTINE

                if result.action == ValidationAction.EXCEPTION:
                    outcome.status = ValidationAction.EXCEPTION
                    break

        outcome.final_output = current
        return outcome

    def _set_field(self, obj: Dict[str, Any], path: str, value: Any):
        keys = path.split(".")
        for k in keys[:-1]:
            obj = obj.setdefault(k, {})
        obj[keys[-1]] = value


def compute_provenance(raw: Dict[str, Any], final: Dict[str, Any], patches: List[ValidationPatch]):
    raw_keys = set(_flatten_keys(raw))
    final_keys = set(_flatten_keys(final))

    fixed_fields = len([p for p in patches if p.action == ValidationAction.FIX])
    quarantined_fields = len([p for p in patches if p.action == ValidationAction.QUARANTINE])

    if len(final_keys) == 0:
        mutation_ratio = 0.0
    else:
        mutation_ratio = fixed_fields / len(final_keys)

    return {
        "raw_fields": len(raw_keys),
        "final_fields": len(final_keys),
        "fixed_fields": fixed_fields,
        "quarantined_fields": quarantined_fields,
        "mutation_ratio": mutation_ratio,
    }


def _flatten_keys(d: Dict[str, Any], prefix=""):
    keys = []
    for k, v in d.items():
        full = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            keys.extend(_flatten_keys(v, full))
        else:
            keys.append(full)
    return keys
