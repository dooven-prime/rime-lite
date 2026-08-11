# Paper XIII Archive

`results/` contains the frozen SOFRS v1 source reports, SOFAUDIT v1 records,
and their derived signature table. They are retained only as source-addressed
inputs to the active v2 migration and as compatibility fixtures for the
historical Paper XIV prototype.

Current SOFRS v2 source-report stacks, SOFAUDIT v2 records, migration indexes,
and object certificates live under `../results/`.

`regenerate_tables_v1.py` rebuilds `results/signature_tables.md` and checks it
against the retained Paper XIII v1 manuscript. It is not an active manuscript
table generator.
