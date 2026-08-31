from defend.adaptive_memory import AdaptiveMemory


memory = AdaptiveMemory()


# Store a legitimate transaction
memory.store(
    transaction_id="TX001",
    features={
        "new_device": 0,
        "new_beneficiary": 0,
        "amount_deviation": 0.2,
        "velocity_deviation": 0.1,
        "location_change": 0,
        "time_deviation": 0.2
    },
    risk_score=0.026,
    decision="ALLOW",
    actual_label=0
)


# Store a suspicious transaction
memory.store(
    transaction_id="TX002",
    features={
        "new_device": 1,
        "new_beneficiary": 1,
        "amount_deviation": 5.0,
        "velocity_deviation": 3.0,
        "location_change": 1,
        "time_deviation": 5.0
    },
    risk_score=0.939,
    decision="BLOCK"
)


print("\n========== MEMORY ==========\n")

print(
    memory.to_dataframe().to_string(index=False)
)


print("\nMemory size:")
print(memory.size())


# Later the analyst confirms TX002 as ATO
updated = memory.update_outcome(
    "TX002",
    actual_label=1
)

print("\nTX002 outcome updated:")
print(updated)


print("\nConfirmed ATO transactions:")
print(
    len(memory.get_confirmed_ato())
)