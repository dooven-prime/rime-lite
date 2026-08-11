# Figure Assets and Renderers

`figures/` owns manuscript image assets and presentation-only rendering code.
Scientific calculations, validation scripts, and structured numerical results
belong under `experiments/`.

## Current Layout

```text
figures/
|-- README.md
|-- style.py                 shared current display helpers
|-- paperN/
|   |-- render.py            active paper-local renderer, when migrated
|   |-- fig*.png
|   `-- fig*.pdf
|-- ccs/                     companion-archive figures
`-- archive/                 retired figure builders and legacy style code
```

Papers I--X currently use:

```text
figures/paperN/render.py
```

The companion archive uses the same contract through:

```text
figures/ccs/render.py
```

It generates only the current white-listed CCS figures. It does not invoke the
retired all-in-one CCS atlas builder.

Other `paperN/` directories may contain only retained image assets. When a
figure workflow is rebuilt, its active entry point should be
`figures/paperN/render.py`.

## Renderer Contract

An active renderer:

- reads frozen or source-addressed records from
  `experiments/paperN/results/`;
- verifies declared source hashes when the result format provides them;
- performs presentation work only: layout, labels, colors, and export;
- writes manuscript assets into its own `figures/paperN/` directory;
- may use shared helpers from `figures/style.py`;
- must not rerun expensive experiments or treat display data as a scientific
  certificate.

Run a migrated renderer from the repository root, for example:

```bash
python figures/paper2/render.py
```

The owning paper and `experiments/paperN/README.md` identify the scientific
source and validation command. A successful figure render does not promote a
Computational Observation to a Computational Certificate or Theorem.

## Archive Boundary

`figures/archive/` contains retired all-in-one `paperN_figures.py` builders,
combined-paper/trilogy renderers, and the legacy `trilogy_style` package. These
files are preserved for release provenance and historical reproduction only.
They are not active build entry points and should not be imported by new
paper-local renderers.

Do not move an artifact required by an immutable release merely to satisfy the
current layout. During a versioned paper reopening, migrate the renderer to
`figures/paperN/render.py`, update manuscript and documentation references, and
retain the old implementation under `figures/archive/` when it remains useful
for provenance.

Loose legacy images at the root of `figures/` are compatibility artifacts.
New manuscript outputs should be written to the owning `paperN/` directory.
