# MetaboMind

MetaboMind is a simple goal-oriented reasoning demo.  The core framework lives
in the ``control/`` package and can be used from the command line or via the
Tk-based GUI in ``interface/metabo_gui.py``.  The GUI spawns worker threads for
each user cycle and MetaboTakt so that the interface remains responsive.

Runtime data such as logs or graphs are stored in the `data/` directory.
The `MemoryManager` stores its entropy snapshot under
`data/last_entropy.txt` by default. Goal and reflection texts are kept in
`data/goal.txt` and `data/last_reflection.txt`.
All cycle logs are written to `data/metabo_log.jsonl` and the unified
knowledge graph persists as `data/metabograph.gml`.

## Setup

Install the dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Set the `OPENAI_API_KEY` environment variable to enable LLM features.

The test suite also relies on `pyyaml`, included in the requirements.

All tests can then be executed with `pytest`.

All prompts used for LLM interactions are defined centrally in `cfg/config.py`.
The Metabo rules are stored in `METABO_PROMPT` and automatically prefixed to
each system prompt.

Every request now includes a `mode_hint` that reflects the active Yin or Yang
mode. In Yin, the LLM is asked to respond "introspektiv, reflektierend" while in
Yang the instruction is "zielgerichtet, handlungsbezogen".

Yin and Yang are primarily selected by an LLM via the function
`decide_yin_yang_mode(user_input, metrics)`.  The metrics include the current
entropy delta and a rough emotion estimate.  The orchestrator keeps a simple
heuristic fallback.  Intermediate metrics and debug output are displayed in the
GUI tabs while the chat only shows the user text and the final LLM answer.  In
addition, the orchestrator increases Yin votes whenever typical German phrases
expressing confusion (e.g. "ich verstehe nicht", "gar nichts mehr", "bin
verwirrt") are detected.
The "Wissensgraph" tab visualises the knowledge graph with zoomable nodes and
edges, including tooltips for quick inspection. The graph can be panned by
dragging with the left mouse button, zoomed via the mouse wheel and it updates
automatically whenever new triplets are recorded.
It displays the consolidated `MetaboGraph` loaded from `data/metabograph.gml`.
The module `graph_entropy_scorer` analyses the semantic order of this graph and
provides a normalized entropy score with textual explanation.

## MetaboGraph

All individual graphs are consolidated into the `MetaboGraph`. Each node carries
a `typ` attribute like `konzept`, `intention` or `emotion` and optional
`source` metadata. The graph is persisted as `data/metabograph.gml` and helper
functions allow extraction of subgraphs by type and calculation of its Shannon
entropy.
All triplet extraction now flows through `parsing/triplet_pipeline.py`. The
pipeline deduplicates triples, annotates them with a timestamp and source and
stores them directly in `metabograph.gml`.

Reflections generated during a MetaboTakt are now also parsed for symbolic
triples. These triples are stored in the ``MetaboGraph`` and linked to the
current goal node along with the detected emotion.

## Diagrams

### Class overview

![Class Diagram](https://www.plantuml.com/plantuml/png/U9oDLjzlqp0GVizVuRUbMWllFA19R9gGDe608Kq8MMvoJIqSEzYNRG7nltDsd3frEiPBwjoTxxxxyLrwuL1Ox5jLdBq-OtTTBH1g9dO8becwbhfX5dxsqa8B6jqhVCAYKi8vTYkadew0OclU3PM2ABasGjqABHfoyxjWRDEGW7S2z-mD-qW_NcPXfw12QNIcEMy0kRzHhloRczxy8qYK4JLFrwEPU82v4E49LyMV0yRMs66EwRmDi7bZHUU3ZrbS-pUFZkm3D6MQ_y6yeV9OqmrvAWwD1OvMTWhGbTCX8AO2ymX2QYURFNACUChUWILfr-EQJPVMp5TWpHA8DOimLodMh0Jf-4BPefUIak1Rs94RyapdC0Z1h1AgwXLD1u-9biab5HYFnIEI8_c3K3q4PIkwIUhpdMBNe52aXdqwuBpIZTJJP7qHF_18S2_rlT3D1rljmQ4L53csrzJW6yFD0rWhQw2ka44GXLYE13VIuRSTPO7VWs8lFVHXqf1zb0FHP0i2IICr1fcc0UDHvdc3ieLfNdtmqZz2nZLK53yAWTfPKI_zVAwPwxUyDZfMXWm8WiQnYhmo6ebcZlUw0kkFEEHpJLSkW_kOTemrICq7giiOT8mLGyz94KR-xlr4MpzwNoKy7fnPyHYnqCJ_CgPDRwHhU5WVcQobWfSfI71wDVRxSqLp4Nql9ofCVl05JvsYR7DDXZiGD_ZQIGNv3fbetIkKbtBYTI3TIB4KpijEK_IPiNTQT6vlC54ed3RSyo4UMx0DSEtBxn_KyA6ZVflULf1LvmwbScCcdJKLE1VXkDYv_DPOW1lJ79RPYGhGvkALNyfbs2DyT3LV7ccnd2J-ORki_Sm3hIWSF8R2xtwssRmzslopSz3DlW4BtT4sNcWNrCyDJd1-6I8HOmdjKFJY-BkGSXhd9MsR4x0pvJpVJBLCQ2hWyvaGA_CIKs_fi-0OxYs8EhERXVoNsOpY9t9VShMOxuIyFCksfh4iBa3N_e_5Nmr2u4W0)

### Cycle sequence

![Sequence Diagram](https://www.plantuml.com/plantuml/png/U9o5LC5ksp0ClVih2EImz13qxiDGO2k27ee16pAW9q6L65c0B0aKlTRx-abUviIoiLuV7n_9HqeFYINnqBlcqpqCKKj63VBCI81zO1lyeGyQuMpV6wau49mIKXDpabKsIi_mZ2nVm_7qj85-6PN31NuCqZrBByrAfGyqRaM-uzcXAgqyUcFzKkx5-XVfpJTI7IOccJjSokRclwAokX8zaepTJujlM_YZPmfn_A42vN0P60wVRrDQq2JD_UyG-Zaysz22zN5WO7pdPaQlbCcJ5cZmefy0eGgoB_mxsEsu8vHwjsjkw5FzgtCj66HXCh2_gsaB8rj8NiRK1LuJrwEseAHJWyj78F1l8AUjUN2eXqa5hmlKYojTUwIYJdDeNyvBTDRpTeCdjYwr42aeJ4amsUWm_MjhYjwuNx0MfDON8gTvxYcseYRv2p_qiEXTLcLzigPZmK6Oel2n_xc0k3obDNdZVFDjJVSgYZ7xN9QiIkigrxkU4qRhnPZLwimhTRsuGcqsklXFSw-34P7omkfnbe-0C0skUW3r4tfh7j3hylly0HGRe0W0)

### LLM test sequence

![LLM Test Sequence](https://www.plantuml.com/plantuml/png/PP2z2iCW481tdy8n6V826KgWGwSkfPt5cgC8vXGz2Ntx-bEeiPj-Vdntk0IIdk9cc5HaFRz38F3C9QYLTXAfe5j4xF0LI3xj-QqC7FZ5IlDmgyoPMkFJgOdCt4SKbEvX6DcFPwjfLcqhGAXC1eqkqiWQYKzz6a8qr5MRZMOUoq6y4alZcwU_5iBEitQeVPqworbFR05Sy_zz0000)
