---
name: corticallabs-api
description: Use for Cortical Labs CL API and CL SDK tasks, including `cl.open()` workflows, closed-loop `neurons.loop()` logic, stimulation design (`ChannelSet`, `StimDesign`, `BurstDesign`), recordings and `RecordingView` analysis, and app CLI flows (`cl.app.init`, `cl.app.pack`, `cl.app.run`, `cl.playback`).
---

# Cortical Labs API

## When to use

Use this skill when the user asks to:
- write or debug code using the Python `cl` API
- build closed-loop spike/stimulation loops
- create or inspect recordings (`.h5`) and data streams
- run CL analysis functions (`analyse_*`, plotting)
- scaffold/package/test CL applications with `python -m cl.app.*`
- run or troubleshoot playback/visualisation tooling

## Workflow

1. Identify target runtime:
- CL1 hardware
- Simulator (`cl-sdk`) on local machine

2. Route to the smallest reference file:
- core API surface: `references/upstream-text/cl.txt`
- tutorial-style examples: `references/upstream-text/index.txt`
- analysis metrics/results: `references/upstream-text/cl/analysis.txt`
- app packaging/runtime: `references/upstream-text/cl/app.txt` and `references/upstream-text/cl/app/*.txt`
- playback and visualisation: `references/upstream-text/cl/playback.txt`, `references/upstream-text/cl/visualisation*.txt`
- SDK source-derived signatures: `references/external/sdk-signatures.md`
- notebook examples: `references/external/cl-api-doc-index.md`
- whitepaper context: `references/external/whitepaper/whitepaper-abstract.txt` and `references/external/whitepaper/whitepaper-fulltext.txt`

3. Build the smallest correct solution:
- prefer `with cl.open() as neurons:` for session lifecycle
- use explicit types (`ChannelSet`, `StimDesign`, `BurstDesign`) over ambiguous scalar shortcuts when possible
- include recording/analysis/playback paths only if the user needs them

4. Validate assumptions with docs lookup:
- use targeted `rg` searches (examples below) before answering edge-case API questions
- if behavior differs between CL1 and simulator, call that out explicitly

## No-guesswork protocol

- Treat `references/external/source-lock.json` as the source version lock for all external context.
- For any API signature or parameter/default question, verify against `references/external/sdk-signatures.md` first.
- If docs text and source signatures disagree, prioritize source signatures and call out the mismatch.
- If information is not present in local sources, explicitly state `unknown from available Cortical Labs sources` and propose the minimal experiment to resolve it.
- Do not infer hardware timings, channel constraints, or safety semantics beyond what is explicitly documented.

## High-signal constraints

- Preferred connection entrypoint is `cl.open()`; do not instantiate `cl.Neurons` directly.
- Loop timing is strict (`neurons.loop()`); code overruns can raise `TimeoutError` on CL1.
- Simulator jitter behavior differs from CL1 and may not enforce the same timing failure path.
- Stimulation safety/limits in docs:
  - amplitude type guidance in `cl.app.model`: valid `StimAmplitudeMicroAmps` is `(0.0, 3.0]`
  - pulse width is in microseconds and constrained to 20 us steps in model docs
  - non-stimmable channels are excluded (0, 4, 7, 56, 63)
- `cl.playback` and `cl.app.run` are CLI tooling intended for local development workflows.

## Fast lookup commands

Run these from the skill root:

```bash
rg -n "^ def loop|recover_from_jitter|^ def record|^ def create_data_stream" references/upstream-text/cl.txt
rg -n "StimDesign|BurstDesign|ChannelSet|lead_time_us" references/upstream-text/cl.txt
rg -n "^ def analyse_|^ class AnalysisResult" references/upstream-text/cl/analysis.txt
rg -n "python -m cl\\.app\\.(init|pack|run)|required files|info.json|default.json" references/upstream-text/cl/app*.txt references/upstream-text/cl/app/*.txt
rg -n "python -m cl\\.playback|CLI Controls|WebSocket" references/upstream-text/cl/playback.txt
rg -n "^## src/cl|^- `def |^- `class " references/external/sdk-signatures.md
rg -n "generated_at_utc|commit|version" references/external/source-lock.json
```

## Key commands

```bash
# SDK install
pip install cl-sdk

# App scaffolding and packaging
python -m cl.app.init my-app
python -m cl.app.pack my-app
python -m cl.app.run my-app my-app/default.json

# Recording playback
python -m cl.playback my_experiment.h5
```

## Refresh the local docs scrape

Use these when sources change:

```bash
# Refresh docs.corticallabs.com mirror
python scripts/scrape_corticallabs_docs.py --max-pages 2000

# Refresh external repos + whitepaper + derived artifacts
python scripts/refresh_external_context.py
```

The scripts update:
- `references/upstream-html/` (raw mirrored pages)
- `references/upstream-text/` (plain-text extraction)
- `references/scrape-manifest.json` (crawl manifest)
- `references/external/source-lock.json` (commit/version lock)
- `references/external/sdk-signatures.md` (source-derived API signatures)
- `references/external/cl-api-doc-index.md` (notebook index)
- `references/external/whitepaper/*` (whitepaper artifacts)
