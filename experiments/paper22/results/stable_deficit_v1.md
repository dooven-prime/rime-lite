# Stable Deficit Analysis

Status: computational observation from the Paper XXI v1.0 replay.

## Fixed-deficit layers

| k | observations by prime | stable tail | observed threshold |
|---:|---|---:|---:|
| 0 | p=2:1, p=3:1, p=5:1, p=7:1, p=11:1, p=13:1, p=17:1, p=19:1 | 1 | 2 |
| 1 | p=2:2, p=3:2, p=5:2, p=7:2, p=11:2, p=13:2, p=17:2, p=19:2 | 2 | 2 |
| 2 | p=2:1, p=3:3, p=5:3, p=7:3, p=11:3, p=13:3, p=17:3, p=19:3 | 3 | 3 |
| 3 | p=3:1, p=5:7, p=7:7, p=11:7, p=13:7, p=17:7, p=19:7 | 7 | 5 |
| 4 | p=5:5, p=7:19, p=11:19, p=13:19, p=17:19, p=19:19 | 19 | 7 |
| 5 | p=5:1, p=7:18, p=11:56, p=13:56, p=17:56, p=19:56 | 56 | 11 |
| 6 | p=7:7, p=11:126, p=13:150, p=17:174, p=19:174 | 174 | 17 |
| 7 | p=7:1, p=11:189, p=13:339, p=17:503, p=19:503 | 503 | 17 |
| 8 | p=11:137, p=13:519, p=17:1301, p=19:1403 | - | - |
| 9 | p=11:52, p=13:479, p=17:2924, p=19:3616 | - | - |
| 10 | p=11:11, p=13:252, p=17:5342, p=19:8334 | - | - |
| 11 | p=11:1, p=13:75, p=17:6670, p=19:16040 | - | - |
| 12 | p=13:13, p=17:4679, p=19:22601 | - | - |
| 13 | p=13:1, p=17:2050, p=19:18416 | - | - |
| 14 | p=17:634, p=19:9452 | - | - |
| 15 | p=17:133, p=19:3451 | - | - |
| 16 | p=17:17, p=19:917 | - | - |
| 17 | p=17:1, p=19:168 | - | - |
| 18 | p=19:19 | - | - |
| 19 | p=19:1 | - | - |

Observed stable prefix: `[1, 2, 3, 7, 19, 56, 174, 503]`

Recurrence diagnostics (finite fit only): []

Boundary: this does not prove eventual stabilization, a closed form, or a uniform automaton quotient.
