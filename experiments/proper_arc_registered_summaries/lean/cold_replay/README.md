# Isolated Cold Replay

This harness replays the nine owning validators without copying project
builds, local package checkouts, or local Mathlib compiled caches. It uses
the pinned Lean release and Lake lock, fresh network checkouts at each
locked revision, and a freshly downloaded official Mathlib compiled cache.
The Proper-arc and reused `RegisteredAbsorptionChains` modules are compiled
in the new project directory.

The [completed result](RESULT.md) and its versioned evidence bundle record
the first successful run on 2026-11-04: nine owning validators and 94 tests
passed. The acquisition helpers require Python 3.12 or newer and Git; this
run used Python 3.13 on Windows.

The theorem-to-source map is checked before and after replay. Its union
graph counts all audited declarations in the nine frozen reports, not
merely the union of the 17 selected theorem closures.

## Source and Environment

The first run uses a detached worktree at the manuscript content commit
`2a30449b9dc37a36b25b277ebc006515c2addb59`. Before the companion overlay,
the worktree must be pristine and contain no Lean companion directory.
`prepare.py` copies only SHA-256-bound sources and evidence, never `.lake`.

The companion overlay is local: it is not a published companion content
commit. `source-snapshot.v1.json` records that delivery mode and every
copied file. The present run also has a pre-execution driver amendment,
recorded in `source-snapshot.v2.json`: owning validators use their default
CLI, since the origin-interface validator does not accept the optional
historical-Git flag. Separate map checks perform the historical byte checks.
No frozen proof input, validator, manifest, or audit report was amended.

Isolation is on the same host, not a second machine or an independent
review. Downloaded Mathlib compiled artifacts are used; this is not a full
Mathlib source rebuild. Lake may still compile individual missing dependency
artifacts from the freshly acquired sources; the receipt's
`mathlib_source_rebuilt: false` denotes the absence of a full source rebuild,
not a claim that no dependency file was compiled. The new toolchain archive is bound by SHA-256,
checked ZIP CRC, and executable version. No independent publisher asset
digest verification is claimed.

## Run

Use fresh absolute paths for the worktree, runtime, and evidence. From the
owning repository, create a detached worktree at the fixed content commit;
then invoke the preparation script from this Lean directory:

```powershell
python -B cold_replay/prepare.py --worktree <clean-worktree> --evidence <evidence-directory>
python -B cold_replay/download_toolchain.py --output <runtime>/lean-4.33.0-windows.zip --evidence <evidence-directory>
tar.exe -xf <runtime>/lean-4.33.0-windows.zip -C <runtime>
```

The evidence and runtime directories must exist. In the copied Lean
directory, run its copied driver:

```powershell
python -B cold_replay/run_replay.py --evidence <evidence-directory> --toolchain <runtime>/lean-4.33.0-windows --archive <runtime>/lean-4.33.0-windows.zip --snapshot <evidence-directory>/source-snapshot.v1.json --dependency-mode official-cache
```

For the already prepared first run, select `source-snapshot.v2.json`
instead. A new preparation with the current driver needs no amendment.
Use `--resume` only with the same source snapshot and toolchain identity.
Successful steps are reused only when their commands and log hashes match;
failed attempts remain in the receipt and are retried with new log files.

If the host requires a network proxy, supply only the needed transport
configuration to the isolated Git config and download environment. Do not
copy the user's complete Git configuration or credentials into public
evidence. The first run's direct fetch was interrupted before any source
objects arrived. The host's configured proxy was also unreachable. The
next attempt uses direct HTTPS with Git's OpenSSL backend and HTTP/1.1;
both earlier failed steps remain recorded. Git's OpenSSL `curl.exe` is
placed on the download PATH rather than Windows Schannel curl. TLS
certificate verification remains enabled.

The direct pack transfer also disconnected. `bootstrap_mathlib.py` records
the subsequent source-only recovery separately: official GitHub API commit
metadata reconstructs the exact locked Git commit SHA; every recursive tree
object and every codeload archive blob is checked against that commit. The
archive is downloaded afresh. No metadata, source payload, or compiled
artifact is taken from a previous Mathlib checkout. The two tracked benchmark
symlinks use Git's Windows link-text checkout policy. Earlier failed bootstrap
attempts remain in separate versioned receipts.

For a new source-only recovery before any Mathlib build, the API/archive
route can be invoked from the owning Lean checkout (not the copied driver
directory):

```powershell
python -B cold_replay/bootstrap_mathlib.py --project <copied-Lean-directory> --evidence <evidence-directory> --curl <OpenSSL-curl.exe> --api-fallback
```

It is restricted to the locked Mathlib revision, verifies the complete Git
object identities, and refuses to replace existing source files. It does
not provide compiled dependencies or bypass an owning validator. The first
run's successful recovery is the separately retained `v3` attempt.

## Evidence

`cold-replay.v1.json` is the downstream run record, separate from all nine
owning freezes. `PASS` requires all nine default validators, all ten unit
test suites, a final theorem-map check, unchanged snapshot bytes, and
unchanged dependency revisions and lock bytes. Each command has an exit
code, duration, and SHA-256-bound log. A running or failed receipt is not
a successful replay.

Each owning validator recomputes its complete target signatures, axiom
sets and declaration graph, then compares the report with the frozen
report. The map additionally checks consistency across reports and the
historical source bytes. Fixed-pair specialization and the generating
function/asymptotic layer are outside this run.

Once the run has passed, its evidence can be checked from the owning Lean
checkout without invoking Lean:

```powershell
python -B cold_replay/verify_result.py --evidence <evidence-directory>
```

This read-only check validates the recorded evidence closure; it is not a
new execution of the owning validators.
