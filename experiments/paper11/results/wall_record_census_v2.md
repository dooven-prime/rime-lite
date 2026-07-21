# Paper XI v2 Wall-Record Coverage Census

- Frozen v1 records retained: **24**
- Post-v1 records added: **4**
- v2 registered wall records: **28**
- v2 first-pass eligible records: **19**
- Coverage target: at least 3 eligible records, 2 species, and 2 deformation origins per class.
- Coverage means predeclared finite-sample curation coverage, not taxonomy completeness.
- Class A closes through a constructed witness; natural non-Rubik breadth remains open.

- Registered wall records: **28**
- First-pass eligible records: **19**
- Class memberships: **38** (multi-label records allowed)
- Coverage target: at least 3 eligible records, 2 species, and 2 deformation origins per class.

## Class Coverage

| Class | Registered | Membership share | Eligible | Species | Deformations | Status |
|---|---:|---:|---:|---:|---:|---|
| A Collision/spectral | 4 | 10.5% | 3 | 2 | 3 | **pass** |
| B Repair | 10 | 26.3% | 6 | 6 | 6 | **pass** |
| C Terminal-structure | 5 | 13.2% | 4 | 4 | 4 | **pass** |
| D Plateau/rate | 5 | 13.2% | 5 | 5 | 5 | **pass** |
| E Nonsmooth/discrete | 6 | 15.8% | 5 | 5 | 5 | **pass** |
| F Bridge/incidence | 8 | 21.1% | 3 | 3 | 3 | **pass** |

## Species Prevalence

This retains the original 15-species denominator and does not count repeated records as new species.

| Class | Species count | Prevalence |
|---|---:|---:|
| A Collision/spectral | 1 | 6.7% |
| B Repair | 5 | 33.3% |
| C Terminal-structure | 2 | 13.3% |
| D Plateau/rate | 2 | 13.3% |
| E Nonsmooth/discrete | 2 | 13.3% |
| F Bridge/incidence | 3 | 20.0% |

## Coverage Gaps

All classes meet the first-pass coverage target.

## Record Inventory

| Record | Classes | Species | Deformation | Eligible | Evidence |
|---|---|---|---|:---:|---|
| `A-rubik-collision-quotient` | A | Rubik QT/HT | affine projection parameter | yes | `experiments/paper4/rubik_collision_quotient.py` |
| `A-rubik-endpoint-pair-closures` | A | Rubik QT/HT | single QT generator weight | yes | `experiments/paper11/spectral_ade_collision.py` |
| `A-rubik-simultaneous-pair-gap-response` | A | Rubik QT/HT | two-weight diagonal QT path | no | `experiments/paper11/spectral_ade_collision.py` |
| `BF-rubik-r2-repair` | B,F | Rubik accessibility | fixed generator family | no | `experiments/paper5/path_commutator_cancellation.py` |
| `F-rubik-type-iii-cancellation` | F | Rubik Type III/IV wild | static natural-sector audit | no | `experiments/paper10/rubik_wild_type34_audit.py` |
| `F-rubik-type-iv-incidence` | F | Rubik Type III/IV wild | algebraic bridge perturbation | yes | `experiments/paper7/incidence_variety_codim.py` |
| `BF-synthetic-complement-repair` | B,F | Synthetic Type III/IV | constructed obstruction control | no | `experiments/paper5/complement_explosion.py` |
| `BCF-quantum-cnot-threshold` | B,C,F | Quantum Clifford+CNOT | CNOT-strength matrix interpolation | yes | `experiments/paper11/repair_persistence_quantum.py` |
| `BF-control-kalman-chain` | B,F | Control Kalman | static chain realization | no | `experiments/paper10/control_pde_combinatorial_sof.py` |
| `B-transformer-lie-depth-repair` | B | NN Transformer activation | single synthetic transformer realization | no | `experiments/paper12/transformer_activation_sof.py` |
| `BC-moe-bias-repair` | B,C | Mixture-of-Experts routing | load-bias update trajectory | yes | `experiments/paper12/moe_bias_repair_sof.py` |
| `B-diffusion-denoising-repair` | B | Diffusion / denoising | forward diffusion and reverse denoising time | yes | `experiments/paper12/diffusion_denoising_sof.py` |
| `BE-maze-door-wall` | B,E | Dynamic maze connectivity | discrete door closure/reopening path | yes | `experiments/paper12/maze_wall_crossing.py` |
| `BF-recommender-targeted-bridge` | B,F | Recommender structural coverage | targeted interaction intervention | yes | `experiments/paper12/recommender_sof.py` |
| `C-markov-absorbing-endpoint` | C | Markov absorbing | endpoint contrast across transition systems | no | `experiments/paper11/cross_species_wall_audit.py` |
| `C-barrier-stopping-boundary` | C | Barrier option GBM | log-price diffusion | yes | `experiments/paper10/barrier_option_sof.py` |
| `D-xu-ridge-rate-hierarchy` | D | Xu ridge model | optimization time | yes | `experiments/paper9/state_mixing_fft.py` |
| `D-mechanism-separated-rates` | D | Mechanism-separated SOF | gradient/regularization response time | yes | `experiments/paper10/mechanism_separation_theorem.py` |
| `D-yang-state-mixing-plateau` | D | Yang-like photonic | state-mixing parameter | yes | `experiments/paper9/state_mixing_fft.py` |
| `D-rubik-generator-weight-plateau` | D | Rubik deformation probes | QT generator-weight deformation | yes | `experiments/paper9/state_mixing_fft.py` |
| `E-graph-edge-removal` | E | Graph P3/C4 | discrete edge removal | yes | `experiments/paper11/cross_species_wall_audit.py` |
| `E-relu-kink` | E | NN Transformer activation | activation bias | yes | `experiments/paper11/piecewise_smooth_activation_wall.py` |
| `E-topk-rank-selection` | E | NN Transformer activation | activation bias samples | no | `experiments/paper11/piecewise_smooth_activation_wall.py` |
| `F-ncg-t7-bridge` | F | Finite spectral triple | static finite spectral-triple realization | no | `experiments/paper10/ncg_spectral_triple_sof.py` |
| `A-constructed-goe-endpoint` | A | Constructed real-symmetric spectral family | degenerate endpoint with GOE splitting direction | yes | `experiments/paper11/validation/degenerate_endpoint_collision.py` |
| `BE-nested-percolation-opening` | B,E | Erdos-Renyi percolation ensemble | nested edge-threshold probability path | yes | `experiments/paper11/validation/percolation_wall.py` |
| `DE-kuramoto-freezing-crossover` | D,E | Kuramoto oscillator ensemble | matched coupling-strength sweep | yes | `experiments/paper11/validation/kuramoto_wall.py` |
| `C-grn-terminal-basin-loss` | C | GRN toggle-switch flow | continuous regulatory-edge weakening | yes | `experiments/paper11/validation/grn_toggle_wall.py` |
