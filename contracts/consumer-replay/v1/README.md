# Event-Anchored Consumer Replay Contract v1

**Versioned specification snapshot for a finite consumer replay Case.** This
package fixes the definitions, representations, and adapter conventions used
to check a finite witness. It is not a paper release, a machine-checked proof
certificate, an independent validator, or an authorization to use a result as
current knowledge. A successful Case does not certify an all-size theorem.

The contract is self-contained. It does not import a protocol authority from
the numbered papers or from an unpublished research draft. Its fixed domain
has one labelled cycle, one binary-kernel defect, a singleton packet seed,
and one selected fusion block. No shortest-word, checkpoint, settlement, or
other admission rule is included.

| File | Role |
|---|---|
| [CONSUMER_SPEC.md](CONSUMER_SPEC.md) | Log oracle, registration, report, and `Carry`/`Absorb` domains and updates |
| [FOREST_MODEL.md](FOREST_MODEL.md) | Placed forest state, generator updates, and event-ancestor decoder |
| [UFE_ADAPTER.md](UFE_ADAPTER.md) | Placed forward-UFE state, ordered-port calls, prefix decoder, and command correspondence |
| [candidate-reports.schema.json](candidate-reports.schema.json) | Structural JSON contract for optional complete Case reports |
| [examples/witness.json](examples/witness.json) | One finite data witness, not a certificate or expected result blob |
| [manifest.json](manifest.json) | Exact-byte inventory and editorial scope record |

## Finite Witness Encoding

The mathematical sets use integer atom labels in this JSON profile. Atom
blocks are sorted lists without duplicates; placements are lists of records
ordered by position. `omega` is the atom enumeration used by the parallel
`iota` positions. `ufe_enumeration` lists those same atoms in the order used
to assign UFE identifiers `0,...,N-1`. The two `kernel_ports` are ordered:
the first is `k_0`, the second `k_1`. Swapping them changes event-address
data even when it leaves the unordered packet partition unchanged.

| JSON field | Mathematical object |
|---|---|
| `environment.q_size`, `p` | `Q = Z/nZ`, `p(q) = q + 1 mod n`; `p` is `successor_mod_n` |
| `environment.d` | Array with `d[q] = f_d(q)`; one rank-`n-1` binary kernel |
| `environment.omega`, `iota` | Atom set and injective singleton seed placement |
| `environment.ufe_enumeration` | Bijection `e` from atoms to UFE identifiers |
| `environment.kernel_ports`, `collision_image` | Ordered `(k_0,k_1)` and common image `c` |
| `prefix` | Chronological word over `p,d` from the singleton seed |
| `selected_block` | Fixed nonempty `F`, which must equal an actual logged fresh block |
| `commands` | Requested `Carry(a)` or `Absorb(a)` steps after `prefix` |
| `candidate_reports` | May be omitted or `null`; otherwise an array of complete Case reports: one after `prefix` registration and one after each command |

A non-null `candidate_reports` value follows
[candidate-reports.schema.json](candidate-reports.schema.json). Each report has
exactly `partition`, `selected_block`, `origin`, `absorptions`, and `carrier`:

| Report field | JSON encoding |
|---|---|
| `partition` | Complete placed partition `[{"q": q, "block": [atoms]}, ...]`, ordered by increasing `q` |
| `selected_block` | The fixed registered atom block `F` |
| `origin` | `{"letter": "d", "ports": [k_0, k_1], "input_blocks": [B_0, B_1], "collision_image": c, "fresh_block": F}`; blocks follow port order |
| `absorptions` | Chronological array of `{"letter": "d", "carrier_port": q_e, "carrier_before": C_e, "other_port": s_e, "other_block": B_e, "collision_image": c, "carrier_after": C_e union B_e}` |
| `carrier` | Current placed packet `{"q": q_h, "block": C_h}` containing `F` |

All atom blocks are sorted lists of distinct integer labels. A non-null
array has exactly `1 + len(commands)` reports, including the state reached by
the entire prefix before the first command. The schema fixes field names,
types, and required presence; replay checks the remaining semantic
constraints: positions are in `Q`, partition blocks are disjoint and cover
`omega`, `origin` is the logged registration event, each absorption is an
actual later event, and the carrier agrees with the placed partition. The
reports are supplied comparisons, never sources for state reconstruction.

An adapter may wrap this data with its own contract/checker identity obtained
from the deployment. Such an envelope is not a premise of the mathematical
consumer, is intentionally absent from the example, and must not be embedded
in this package's byte manifest. The checker may impose finite service limits
on `n`, word length, request size, and time; these are not bounds in the
consumer specification.

For the example, `prefix = dpp` registers `F = {0,6}` at its first `d`.
The following `Carry(d)` fuses the packets on atoms `{3}` and `{5}` while
the selected carrier remains `{0,6}` at position `2`. Thus the complete
partition and union history change, but the selected absorption list stays
empty. The seed prefix and every command must be replayed from source data;
uploaded reports or a claimed registration flag are never trusted.

## Decision Boundary

- **PASS:** the request is well-formed; `F` is logged; all requested command
  guards hold; independently computed log, forest, and placed-UFE views agree
  on each checked prefix, the complete partition and current placement, and
  every required report field. Optional candidate reports also agree.
- **FAIL:** a well-formed request has a false registration or command claim,
  a candidate report mismatch, or a route disagreement. The first failure
  position and reason should be retained. A correct rejection is not PASS for
  the submitted witness.
- **INVALID_REQUEST:** the JSON shape, declared action, seed, atom encoding,
  or deployment identity is malformed or inconsistent. No semantic replay
  verdict is issued.

A checker crash or missing dependency is unresolved, never PASS. Successful
execution of the checker is a separate axis from the witness verdict.
Neither PASS nor FAIL grants qualification, current-use admission, action
authority, or trust in the checker implementation.

The manifest binds its listed files by exact SHA-256 and size. It does not
hash itself or include a receipt that depends on itself; the publishing Git
commit anchors the manifest and this package. Local agreement among three
routes is not independent validation of their common specification.
