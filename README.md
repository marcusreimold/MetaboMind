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

![Class Diagram](https://www.plantuml.com/plantuml/png/ZLPBRzim3BxxL-ZM54ss-mv3WRKe2hJOiAq3Yc4G59jnXCcI9z5ftM7_VHJzjfDr5qScQJu-ygDo6L1vh0gJdBqz4mzbfX0oeNO8NgWiqpON7dvLsaC15iCRVCOaDIe4SQ-qxOw0Qki-rAc1LdBZbBbNLkNavdSYn2OdWImLxiKxyOb-eip3pa2AsjcPvY87bF6BrNby2zrRVB34E9N9uVFMJ1rWB4HunlFaJvzZuNmzpkaYzwgCKMyjKctqoKqKH4t11SdEeAclqsx84oTjNFu_rMp8kNTbFIyoeFCWqUlI08PLTpWVTADYXkCh0BJ9hIYetCAEtAn5F7DBsInL9gqCzLcsYQq6bmGLJiLD9XFvGPaAM5ceifDAT7ti30og0VeflWtsEssWnIEWvsui9wJlq7rbK5_flZzisob7Sgw1vID4HkyqqQS0jweCUuU37ST0hspGN5JfuQ1T5LYn5XQUP3-FtRno_esBWmwLClgbY-ygB2jaWm6Pptq7hsskRSUUh-edJWIFsZugct_qwHu8BaKzQM0iN0PnnAGxWFSwWnxFZUGk11BSwO3VTuGD_c35NiUcrfs6x5ivq2hOWaBIQ8iiiqGYsShYRa1TGCV967mL7rnm1Yd5RuL0uAPXBI87ro9KMvavszZ9r5catH5aPLFmyOZrdApav8hzjNMspcjjPKr0D54QvssiCTEPhG-ttIwA-7_JyDGxy-gfQP8aihuuLmnlfCibxyIPh224LqCGTdhTZFwNb2ZI-bwIYzlFlk2vD5JjN3FB-oX7NYC43opFsH3kzB2Vs01J3aJky6aZ8wtQOm4-1saZ_F517QvBQh2hV0hpKkvStk_Q8xNG-fHfl3DMsaPgDEqSbXhvRfDkDjXYcz6nMJZhEAuGYLh7799uDOdDvltaOXgTMJUweXQwoMMnq2vOEpSuGjTbY674a-dT5BMpAsbfCBwIXdLn9FcPSb9r1zFfV8b5So2fWrM0873lGMKpkr6qVvcDA7cajYMtaZ67v-KlcpSCNt89Del_Rlu2)

### Cycle sequence

![Sequence Diagram](https://www.plantuml.com/plantuml/png/XLB1QiCm3BtdAmovj8UoUmwxRANiK0OR7VHaL4TB38vjP6LTzlLpCaWQ9wpNfwSdFUc1OaVY590o3yHQQG-MnH4PBkvmUbb1dpfbS8OV79WZMAWMAesZRgtoXfy65MjdzxRITYvtrlOCjdebLMDWWhZXNDQL-8nAbudeWS3N7nglQ_ZUCZdVlIj7iTmR5hl7svP2b0JLmuzppLWUpr08RNtBWl6Rin6TACDD2a6jbSq0IDKZcvw_5NdEDI6KUPxTq8Vvq-KAKI7BAWARRKgR7R8GmO8FjUCbSMcr40gCQWqmIlmhnBObJ-nICw77qm7fu_gjBLAlJcFfhW4eIycalK4Ezzt2LrozSUlAAs69dnpI8PiOb4ty1saLbbEc58qDdRQoYsffvqHTdgcdPYjR_BFSfQsa9sqN3vn7ZZ2q9ebR6jZhBm00)

### LLM test sequence

![LLM Test Sequence](https://www.plantuml.com/plantuml/png/PP2z2iCW481tdy8n6V826KgWGwSkfPt5cgC8vXGz2Ntx-bEeiPj-Vdntk0IIdk9cc5HaFRz38F3C9QYLTXAfe5j4xF0LI3xj-QqC7FZ5IlDmgyoPMkFJgOdCt4SKbEvX6DcFPwjfLcqhGAXC1eqkqiWQYKzz6a8qr5MRZMOUoq6y4alZcwU_5iBEitQeVPqworbFR05Sy_zz0000)
