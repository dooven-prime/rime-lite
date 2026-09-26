# P28.5b Candidate Rank-Five Section Return

## Result

The frozen P28.5a candidate satisfies F5 on its declared fixed scope:

```text
for every C in Sec_5,cand^(7),
there exists m in M_5(C),
and there exists x in Lift_5(C,m),
such that target(x) lies in Sec_4,ext^(7).
```

Equivalently,

```text
forall C in Sec_5,cand^(7), exists m in M_5(C): Good_5(C,m).
```

This is a theorem about the 35-context source-local candidate, not the full
15,120-context inherited universe and not a maximal or canonical rank-five
section.

## Two-Phase Quantifier Discipline

The evaluator reads only:

1. the frozen P28.5a candidate artifact;
2. the independently released Paper XXVII lower-section authority.

It does not import or invoke the candidate producer and does not rebuild the
source section, menus, or exact lifts. It first verifies that the released
lower-section projection agrees byte-for-byte at the mathematical payload
level with the authority frozen in P28.5a. Only then does it evaluate

```text
Good_5(C,m)
iff some exact lift in the frozen channel m has a typed target boundary
in the released Sec_4,ext^(7).
```

No preferred or best channel is selected.

## Finite Result

| object | total | successful | unsuccessful |
| --- | ---: | ---: | ---: |
| source contexts | 35 | 35 | 0 |
| abstract channels | 87 | 35 | 52 |
| exact lifts | 214 | 35 | 179 |

Every source has exactly one good channel in this finite candidate. Every good
channel contains exactly one successful exact lift. These uniqueness counts
are derived fixed-scope facts, not part of the general section-return schema.

The 35 successful lifts have uniform local anatomy:

```text
word                 p^2 d
corridor length      3
surplus               0
fusion masses         1+1
target partition      (2,2,2,1)
```

Their target section references are pairwise distinct and exhaust the 35
released extremal rank-four targets. The incoming rank-five distinguished
packet does not participate in the terminal fusion; the outgoing rank-four
distinguished packet is the fresh `1+1` fusion packet. This is a typed ancestry
update, not a requirement to consume the incoming fresh packet.

The released lower section is role-addressed, while the P28.5a lifts retain
the actual source atoms. Each successful row therefore also contains an exact
role handoff: a packetwise bijection from the canonical `F4/D1/D2/s` atom
labelling to the actual target packets. The bijection preserves occupied
coordinates, the rooted action, packet masses, and the distinguished packet.
This is the typed bridge from section membership to a canonical lower-section
continuation; equality of unrelated serialization-specific context IDs is not
assumed.

## Failed Channels as Quantifier Controls

The 52 failed channels and 179 unsuccessful exact lifts remain serialized.
They are not removed from the menu after evaluation. Thus the theorem has the
intended form

```text
forall source, exists a good channel,
```

not the stronger and false form

```text
forall source, every channel is good.
```

Had a source lacked a good channel, the evaluator would have emitted its
complete frozen menu and complete exact receipt fiber under `hostile_sources`.
The observed hostile-source list is empty.

## Recursive Consequence at the Declared Scope

Together with the completed P28.4 section-to-base theorem, the fixed-scope
chain is now

```text
Sec_5,cand^(7) -> Sec_4,ext^(7) -> P_<=3^(7).
```

After transporting a lower-section continuation through the stored role
handoff, the exact-compatible credit identities from P28.2 telescope along
the composed path. This is the first positive-rank section-to-section instance
in Paper XXVIII. It does not establish another rank-five section, an all-rank
return, or stability in `n`.

## Replay

```powershell
python experiments/synchronizing_automata/paper28_evaluate_rank5_section_return.py `
  --n7-extremal-input <paper27-release>/experiments/paper27/results/single_defect_n7_extremal_carrier_input_v1.json

python experiments/synchronizing_automata/validation/validate_paper28_rank5_section_return.py `
  --n7-extremal-input <paper27-release>/experiments/paper27/results/single_defect_n7_extremal_carrier_input_v1.json
```

The validator recomputes only the post-freeze evaluation, checks every
channel/lift partition, confirms the existential source theorem, and validates
the artifact receipt. P28.5a has its own independent construction replay.
