## GridWorld

| Failure | Delta_supp | Delta_brw | Delta_brl | Delta_dep | Delta_frz=(R1,W,L) | Delta_cns | Delta_ctrl | Delta_wal |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| F1 action aliasing | 0 | 0 | 0 | 0 | (0, 0, 0) | 18 | 0 | -- |
| F2 persistence loss | 0 | 0 | 18 | 0 | (0, 0, -78) | 2 | 6 | -- |
| F3 forbidden edge | 2 | 6 | 6 | 48 | (-2, -48, -66) | 1 | 2 | -- |
| F4 bridge deletion | 0 | 0 | 8 | 0 | (0, 0, -52) | 0 | 10 | -- |
| F5 deformation | 12 | 30 | 16 | 108 | (0, 0, +20) | 6 | 24 | 5 steps |

## SIR

| Failure | Delta_supp | Delta_brw | Delta_brl | Delta_dep | Delta_frz=(R1,W,L) | Delta_cns | Delta_ctrl | Delta_wal |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| F1 rate equalization | 0 | 0 | 0 | 0 | (0, 0, 0) | 0 | 4 | -- |
| F2 missing edge | 2 | 2 | 2 | 4 | (+2, +4, +4) | 0 | 2 | -- |
| F3 forbidden direct | 2 | 4 | 2 | 2 | (-2, 0, 0) | 1 | 2 | -- |
| F4 rate distortion | 0 | 0 | 0 | 0 | (0, 0, 0) | 0 | 2 | -- |
| F5 wall record | 0 | 0 | 0 | 0 | path-dependent* | 0 | 2 | 11 steps |

## Traffic

| Failure | Delta_supp | Delta_brw | Delta_brl | Delta_dep | Delta_frz=(R1,W,L) | Delta_cns | Delta_ctrl | Delta_wal |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| F1 phase aliasing | 4 | 4 | 0 | 8 | (+4, +8, +4) | 2 | 8 | -- |
| F2 missing phase | 4 | 4 | 0 | 8 | (+4, +8, +4) | 0 | 8 | -- |
| F3 forbidden diagonal | 2 | 8 | 4 | 2 | (-2, 0, -4) | 1 | 2 | -- |
| F4 timing distortion | 0 | 0 | 0 | 0 | (0, 0, 0) | 0 | 8 | -- |
| F5 wall record | 0 | 0 | 0 | 0 | (0, 0, 0) | 0 | 8 | 21 steps |

## Compiler IR

| Failure | Delta_supp | Delta_brw | Delta_brl | Delta_dep | Delta_frz=(R1,W,L) | Delta_cns | Delta_ctrl | Delta_wal |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| F1 CFG/def-use aliasing | 2 | 10 | 12 | 4 | (+2, 0, +10) | 2 | 6 | -- |
| F2 dead branch loss | 4 | 8 | 8 | 8 | (+4, +8, +8) | 0 | 6 | -- |
| F3 spurious CFG edge | 2 | 2 | 4 | 2 | (-2, 0, 0) | 1 | 2 | -- |
| F4 lost def-use | 0 | 0 | 4 | 0 | (0, 0, 0) | 0 | 2 | -- |
| F5 pass-pipeline wall | 0 | 0 | 0 | 0 | (0, 0, 0) | 0 | 0 | 3 steps |

## Network Routing (Appendix)

| Failure | Delta_supp | Delta_brw | Delta_brl | Delta_dep | Delta_frz=(R1,W,L) | Delta_cns | Delta_ctrl | Delta_wal |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| F1 route aliasing | 6 | 4 | 4 | 6 | (+6, +6, +6) | 3 | 12 | -- |
| F2 blocked prefix | 2 | 0 | 0 | 2 | (+2, 0, 0) | 0 | 2 | -- |
| F3 forbidden route | 0 | 2 | 4 | 0 | (0, 0, 0) | 1 | 2 | -- |
| F4 metric distortion | 0 | 0 | 0 | 0 | (0, 0, 0) | 0 | 6 | -- |
| F5 ACL policy wall | 0 | 0 | 0 | 0 | (0, 0, 0) | 0 | 0 | 4 steps |

*SIR F5 has frozen-count delta (-2, -4, -4) at beta=0 and (0, 0, 0) for every sampled beta>0.*

*Traffic F5 records a 21-step rate-order / trajectory-mismatch path; the sampled interval rho in [0.01, 100] excludes the rho -> 0 and rho -> infinity limit walls, so frozen-count deltas remain (0, 0, 0).*

*Compiler IR F5 has zero single-snapshot mismatch but a 3-step pass-path wall record: the reference follows simplifycfg while the candidate remains fixed at the pre-simplifycfg snapshot.*

*Network Routing is an appendix validation domain. F2 is an ACL edge-removal signature, while F3 has zero direct-support mismatch but nonzero bridge and constraint diagnostics.*
