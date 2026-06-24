from agent_validation_provenance import ValidationEngine, ValidationAction, ValidationPatch


# --- example validators ---

def budget_validator(output):
    price = output.get("hotel", {}).get("price")
    budget = output.get("budget", 300)

    if price is None:
        return None

    if price > budget:
        # FIX: adjust price down
        return ValidationPatch(
            field="hotel.price",
            validator="budget_validator",
            action=ValidationAction.FIX,
            before=price,
            after=int(budget * 0.9),
            confidence=0.86,
            reason="exceeds budget"
        )

    return ValidationPatch(
        field="hotel.price",
        validator="budget_validator",
        action=ValidationAction.PASS,
        before=price,
        after=price,
        confidence=1.0,
        reason="within budget"
    )


def quarantine_validator(output):
    # simulate soft constraint violation
    if output.get("hotel", {}).get("rating", 0) < 3:
        return ValidationPatch(
            field="hotel.rating",
            validator="quarantine_validator",
            action=ValidationAction.QUARANTINE,
            before=output["hotel"]["rating"],
            after=output["hotel"]["rating"],
            confidence=0.6,
            reason="low confidence hotel"
        )
    return None


if __name__ == "__main__":

    agent_output = {
        "budget": 300,
        "hotel": {
            "name": "Tokyo Grand",
            "price": 420,
            "rating": 2.8
        }
    }

    engine = ValidationEngine(validators=[budget_validator, quarantine_validator])

    result = engine.validate(agent_output)

    print("\n=== RAW OUTPUT ===")
    print(result.raw_output)

    print("\n=== FINAL OUTPUT ===")
    print(result.final_output)

    print("\n=== STATUS ===")
    print(result.status)

    print("\n=== PATCHES ===")
    for p in result.patches:
        print(p.to_dict())

    print("\n=== PROVENANCE ===")
    print(result.to_dict()["provenance"])
