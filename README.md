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

## Diagrams

### Class overview

![Class Diagram](https://www.plantuml.com/plantuml/png/ZLPBRzGm4BxdL_ZMLDs5EmTKYLPLfLOWe4WLGfQRp6Oj4ZlOasrJn7zdxDXn7blA9UlCJERrpJVUSul2ODVKsSdR4tRNbWAXP6A7O9WeIwagPk1N9mqqeD2-mIVCYbfOosw5LF48A1xqXxwe8KYkjAXlXH8LkVcTCRQjIC1RWNlsZdsY7oSpiAkXGAdLGdDM0NBtHNxgtcnySmylgRKeUVeyc8a3J8K8JtYQ_HbpRBJffpcTLKQqBkgrGggDFhbo0gTfV44y6WprHUsMFFcaQrtzJpLRScvqso-BjAWDS3IohG5j7W--5cez3qb8PMMrHuuXdxopO4ZQThXXyQCDSxtPi9J4XeKqJrEiINFIyPM61Yyv5S4VO4Tko3ET_OXuiqBKHLVJtF1GQ9vSKkjnBXuocSaFekx0AnlHHgchDyOkeKQHe9pZDM2vapM4_beq7jtrn8s8ttOroWivukrjet8YzpKCNKyTcRmxc8u3Q9LexLvZilCnq0Y2qnVL6ZX8tLa-8AVWaO_p7UVVvp-uE4ZRYLe-n_YwGve0Rv0wytb4y59LKaKsVXK_SIQub-fUgEgZAVP0xHA4oT36HfVWHfRh0nWZInZxkUKU1Kk26sdn-uvwWp-yOYyTg7tKa7sG0wsM1n186gdGonIHaWUPspKe6uWSTy5pz_05br1G_204Qcv1K-uulM6sU-2bLeCTBxH2saMMTwe0uuxOBybFJYwylr1dSDvBnNjgn11bS1vYJJU7P__TTTnjhl_V93oEpenu743YHFvdhPlqHhgA-nsxa3NKuJm5yKulXz7_KX15WkyrkJpytXSyjJLLkzGiyZxAaTS8uGVMpraAz_Amlx01vXnmtF6dBNUq2iS6J0LSkVQx1o7SjmImxam1or9kT3NkxYErq3hcXRk3ShyS-G3dT2EcRNbqcuqhS-F65HnHUvT3vguwjjs-drrqaxFNJQwybMvs-QoqAzOk3OxGTHqYZNWsl-kSTd75hGscLrnQ5qUINoXdLSSslPmliMZPI4AGRZJBS6z0b0kxIRH_cKqeUQIsDRUoAOUNvQ_1IyENdOCgtR-blm00)

### Cycle sequence

![Sequence Diagram](https://www.plantuml.com/plantuml/png/XLHDI-mm5DttLmHcySR5CFik7eBAu4847mgkmZMvamRQ9DpSFgs_tgHgPzeKtPvxplqyoMLa8Ewxjlgp5ttGmAW571b9OEVPUhVhl4Pnj6yLAFOa7YDI5PB8AXl0iRX3XXT_UBnTGQy6rU8CFtXexy21AR9qdeQro0CUMrIvbHjdh9kdUxRk6Pov9zLWP8BKuJnjQluQbTMBf0U2q3nPV5t3RnoJ3yC_vIc5yy1Yz_TSKWjDOFRltdTJU5f3BQmBFGl6Dwucz4GPTr8BwftiHa2gZ6mp_q9iDjmGWjvigZFwMF-qkLeOP6aIiBrOqcQBh4Lq46BZkIIMezP2GQlwDfb0ucSWoKgUs2s7YHbV5bWUBdVja79scaA_3W1QV-_9kcXDmvAzDBcfKNj6FZj33dzgcMneaUDKQ8mLr0Z_yVTb9fByUXSbUSMBoIYZ-MH-HDiq1baLooedaqw2mJevf6nBvObQNY5JgvKkVcZkfJSoa7M5F-QE9enzkt3pyZsyLfVeTFvAFW00)

### LLM test sequence

![LLM Test Sequence](https://www.plantuml.com/plantuml/png/PP2z2iCW481tdy8n6V826KgWGwSkfPt5cgC8vXGz2Ntx-bEeiPj-Vdntk0IIdk9cc5HaFRz38F3C9QYLTXAfe5j4xF0LI3xj-QqC7FZ5IlDmgyoPMkFJgOdCt4SKbEvX6DcFPwjfLcqhGAXC1eqkqiWQYKzz6a8qr5MRZMOUoq6y4alZcwU_5iBEitQeVPqworbFR05Sy_zz0000)
