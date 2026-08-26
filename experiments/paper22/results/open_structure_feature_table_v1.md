# Paper XXII Open-Structure Feature Table

Status: computational observation derived from the published Paper XXI arbitrary-depth replay.
The table is a research baseline, not a new theorem or release receipt.

## Uniformity

| depth | generic zero | eligible primes | mismatches | status |
|---:|---:|---|---:|---|
| 1 | 0 | 2,3,5,7,11,13,17,19 | 0 | MATCHED |
| 2 | 14 | 3,5,7,11,13,17,19 | 0 | MATCHED |
| 3 | 115 | 5,7,11,13,17,19 | 0 | MATCHED |
| 4 | 732 | 5,7,11,13,17,19 | 0 | MATCHED |
| 5 | 4094 | 7,11,13,17,19 | 0 | MATCHED |
| 6 | 21635 | 7,11,13,17,19 | 0 | MATCHED |
| 7 | 110486 | 11,13,17,19 | 0 | MATCHED |
| 8 | 553550 | 11,13,17,19 | 0 | MATCHED |
| 9 | 2740395 | 11,13,17,19 | 0 | MATCHED |
| 10 | 13468388 | 11,13,17,19 | 0 | MATCHED |

## Growth

| depth | candidates | generic zero | zero fraction | successive ratio | empirical root |
|---:|---:|---:|---:|---:|---:|
| 1 | 9 | 0 | 0.00000000 | - | - |
| 2 | 45 | 14 | 0.31111111 | - | 3.74165739 |
| 3 | 216 | 115 | 0.53240741 | 8.21428571 | 4.86294413 |
| 4 | 1053 | 732 | 0.69515670 | 6.36521739 | 5.20149003 |
| 5 | 5103 | 4094 | 0.80227317 | 5.59289617 | 5.27751611 |
| 6 | 24786 | 21635 | 0.87287178 | 5.28456277 | 5.27868990 |
| 7 | 120285 | 110486 | 0.91853515 | 5.10681766 | 5.25378703 |
| 8 | 583929 | 553550 | 0.94797484 | 5.01013703 | 5.22269431 |
| 9 | 2834352 | 2740395 | 0.96685062 | 4.95058260 | 5.19173568 |
| 10 | 13758417 | 13468388 | 0.97891989 | 4.91476156 | 5.16334996 |

## Arithmetic Structure

| depth | exceptional characteristics | determinant spectrum | max entry | pole-class sum |
|---:|---|---|---:|---:|
| 1 | - | [1] | 1 | 6 |
| 2 | - | [1] | 1 | 22 |
| 3 | [2] | [1, 2] | 2 | 74 |
| 4 | [2] | [1, 2] | 2 | 240 |
| 5 | [2, 3] | [1, 2, 3] | 3 | 766 |
| 6 | [2, 3] | [1, 2, 3] | 3 | 2422 |
| 7 | [2, 3, 5] | [1, 2, 3, 4, 5] | 5 | 7612 |
| 8 | [2, 3, 5] | [1, 2, 3, 4, 5] | 5 | 23818 |
| 9 | [2, 3, 5, 7] | [1, 2, 3, 4, 5, 7, 8] | 8 | 74274 |
| 10 | [2, 3, 5, 7] | [1, 2, 3, 4, 5, 7, 8] | 8 | 230980 |

## Fixed-Field Automata

| prime | reachable states | ambient bound | state-bound fraction |
|---:|---:|---:|---:|
| 2 | 6 | 6 | 1.00000000 |
| 3 | 9 | 10 | 0.90000000 |
| 5 | 21 | 34 | 0.61764706 |
| 7 | 60 | 130 | 0.46153846 |
| 11 | 606 | 2050 | 0.29560976 |
| 13 | 1918 | 8194 | 0.23407371 |
| 17 | 24518 | 131074 | 0.18705464 |
| 19 | 85185 | 524290 | 0.16247687 |

Deficit layers record the number of reachable sector-1 survivor subsets with `k = p - |S|`. Repeated tail values are a candidate uniformity signal only.

| prime | deficit-layer counts (`k: count`) |
|---:|---|
| 2 | 0:1, 1:2, 2:1 |
| 3 | 0:1, 1:2, 2:3, 3:1 |
| 5 | 0:1, 1:2, 2:3, 3:7, 4:5, 5:1 |
| 7 | 0:1, 1:2, 2:3, 3:7, 4:19, 5:18, 6:7, 7:1 |
| 11 | 0:1, 1:2, 2:3, 3:7, 4:19, 5:56, 6:126, 7:189, 8:137, 9:52, 10:11, 11:1 |
| 13 | 0:1, 1:2, 2:3, 3:7, 4:19, 5:56, 6:150, 7:339, 8:519, 9:479, 10:252, 11:75, 12:13, 13:1 |
| 17 | 0:1, 1:2, 2:3, 3:7, 4:19, 5:56, 6:174, 7:503, 8:1301, 9:2924, 10:5342, 11:6670, 12:4679, 13:2050, 14:634, 15:133, 16:17, 17:1 |
| 19 | 0:1, 1:2, 2:3, 3:7, 4:19, 5:56, 6:174, 7:503, 8:1403, 9:3616, 10:8334, 11:16040, 12:22601, 13:18416, 14:9452, 15:3451, 16:917, 17:168, 18:19, 19:1 |

## Boundary

- This is a deterministic feature extraction from an existing exact replay.
- It does not prove uniformity beyond the listed sample primes.
- It does not establish a scalar asymptotic, recurrence, or periodicity law.
- The next theorem candidates are a generic profile recurrence, a uniform automaton quotient, or an arithmetic recurrence for `E_d`.
