# Fusion-log Companion: Current Status

This is the current navigation entry. The package-root `README.md` remains
an exact input of the frozen M3 manifest, so its historical status is not
edited when a downstream milestone closes.

| Layer | Proved interface | Owning evidence |
| --- | --- | --- |
| M1-M3 | Actual fusion-free routing and exact endpoint restoration | `proof-manifest.v1.json`, `M3_THEOREM_MAP.md` |
| M4-B | Source-ordered complete-log replay with B/K/M bounds | `m4-development-manifest.v2.json`; archive `10.5281/zenodo.23976349` |
| M4-C | Arbitrary initial packet interpretation of the same actual word and complete log | `m4c-development-manifest.v1.json`, `M4C_THEOREM_MAP.md` |
| M4-D | Independent admissible-schedule/compatible-endpoint iff and B(n,t,s) | `m4d-development-manifest.v1.json`; source tag `fusion-log-m4d-source-v1.0` |
| M5 | Section 5 exact actual joint counts and unrestricted actual literal-endpoint log fibres | `m5-development-manifest.v1.json`, `M5_THEOREM_MAP.md` |

## M5 Completion

For a legal positive rank-t literal start, n >= 3 and 1 <= s <= t, M5 proves
the actual rank-s joint count `(t! / s!) * s * choose n s`. At a fixed
reachable literal endpoint it counts all actual complete logs, not merely
members of a preselected schedule family: `(t-s)!` at rank at least two and
`t!` at rank one. Its dependent equivalences preserve full event lists and
packet contents at every physical site.

The extra surviving-boundary choice at rank one is retained in the ordered
log but is absent from the literal endpoint. Coordinate-only fibres remain
a different observation and do not replace these actual-object results.

[M5 README](lean_m5/README.md) gives the public hypotheses and reproduction
commands. [Theorem map](M5_THEOREM_MAP.md) identifies the owning declarations;
the saved replay receipts identify which environment actually ran them.
Public tag/CI/deposit facts are separate from historical local manifests.

All-R optimality and shortest-word uniqueness remain separate work. The HAL
mathematical reader, M4-D tag and all ancestor proof bytes are unchanged.
