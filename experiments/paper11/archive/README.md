# Paper XI Historical Compatibility

This directory stores internal implementations and generated tables retired
from the active Paper XI evidence chain:

- the configuration-level PCA/redundancy audit;
- the 15-species wall-density table;
- the original 24-record v1 census;
- the 28-record v1.1 census.

These artifacts retain their historical claim boundaries. They do not support
the current typed wall spectrum, main-wall admission ledger, or morphology
counts. The active typed census reads the frozen v1.1 JSON in
`results/wall_record_census_v2.json` and verifies its SHA-256; it does not
import these historical Python implementations.

These files do not represent separately published Paper XI manuscripts. The
archived implementations are not stable entry points and are not imported by
current evidence. The repository exposes only the current Paper XI manuscript
and active validation commands.
