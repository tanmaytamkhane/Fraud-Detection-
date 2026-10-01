# Money movement typologies and evidence

The supplied `dataset MM/transactions.csv` has transfer-level fraud labels. `alerts.csv` labels only `fan_in` and `cycle` among the fraud transfers. Its column names closely match IBM AMLSim, a synthetic AML dataset generator, but the supplied files contain no source metadata. Treat their origin as unconfirmed until the teammate provides a download link and generation settings. [IBM AMLSim](https://github.com/IBM/AMLSim)

## MM-V1 Rapid cash-out

Pattern: inbound funds are forwarded quickly through an intermediary to a withdrawal or off-ramp. Observable sequence: source → intermediary → destination, with short dwell and high pass-through. Signals: transit velocity and amount layering ratio. [ASSUMPTION] The supplied data has only `TRANSFER` and no withdrawal channel or cash-out label; this typology is simulated here and cannot be evaluated directly against the supplied labels. An adaptive attacker can lengthen dwell or split transfers across quiet accounts. Payroll and normal wallet transfers are plausible lookalikes.

## MM-V2 Layered fan-out

Pattern: one source distributes funds to several accounts, optionally forwarding them to later hops. Signals: distinct receivers in a recent window, transit velocity, and pass-through. [ASSUMPTION] There is no currency or reporting threshold in the supplied data. Do not claim that small transfers are structured below a legal threshold without the currency, jurisdiction, and applicable rule. An adaptive attacker can reduce fan-out per time window or rotate source accounts. Payroll is a legitimate lookalike.

## MM-V3 Fan-in consolidation

Pattern: many sources send to one receiver, which may forward funds later. Signals: distinct incoming senders and pass-through. The supplied `fan_in` alerts provide a direct but limited label for this pattern (783 transfers). An adaptive attacker can use several consolidation hubs and stagger arrival times. Merchants and marketplaces are legitimate lookalikes.

## MM-V4 Dormant mule activation

Pattern: an account with a long activity gap becomes involved in a transfer chain. Signals: account dormancy, transit velocity, and pass-through. [ASSUMPTION] No `dormant` subtype label exists in the supplied alerts, and the duration of a timestamp step is unknown. This variant is synthetic only. An adaptive attacker can warm the account with low-volume activity. A legitimate returning customer is a lookalike.

## Observed cycle pattern

The supplied alerts contain 936 `cycle` transfers. A round trip in a directed transfer graph is observable from previous edges, but a cycle alone does not prove money laundering. The present six-signal model does not yet include an explicit causal cycle-closure feature, so these labels are reported separately instead of relabeled as one of MM-V1–V4. This is a priority for the next model iteration.
