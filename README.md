# MetaboMind

MetaboMind is a simple goal-oriented reasoning demo.  The core framework lives
in the ``control/`` package and can be used from the command line or via the
Tk-based GUI in ``interface/metabo_gui.py``.  The GUI spawns worker threads for
each user cycle and MetaboTakt so that the interface remains responsive.

Runtime data such as logs or graphs are stored in the `data/` directory.
The `MemoryManager` also keeps its entropy snapshot under
`data/last_entropy.txt` by default.

## Setup

Install the dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

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

## Diagrams

### Class overview

![Class Diagram](https://www.plantuml.com/plantuml/png/VLHDJyCm3BtlL-J69ZQuSq2J04sJc90GGzefyXAlZMYTaRXivTUJTX-aNRlRav_jz-8-TUeP71TvDhYvln7BhGP6BM33w0HeRIWH3hyBup17Od_7Unwe3BmN2p1qWiYmja-bol1OcLd85a2Ge3ltvDQLpTgSE2mrbcOEjkcn-8wR35LLVQ74q6dZ1tnnex0oj09AtfnAqRC3jcSfg_4PbT6HU6LmjfoVx5LwdmPteIF2ua7SQWUxuQXTbPRahxLvDnDc4baVyWgVsnyCT8VjMhRs6veq3dDaPvGV2yOzZuKlrb9RmYkpwoAHMsU8UmLaQdn0PO2l0VMjaieIXm_hPK4ANGMv75O-HeFeh97Zqf0imwQ3zOFZumF2I9WNaybZ8o4HhhauAsskcPesUn6LTaDNHYuaehGqv6gs5T7_57ROQv6DTvqEqUyefBDzgd3cmgCNd3e4tUgBrAwrzKMzut5J95tz2Vu0)

### Cycle sequence

![Sequence Diagram](https://www.plantuml.com/plantuml/png/XP4nYyCm38Lt_mhHAJUqFo33KJYEJbaAdOtEKNC6HpQoKYx__k8CRTC4kedlFJqzx6DM51twOD1f5BXa4fCcv9rFo0gx7ZqVqhW3pD1Cyq9jIF4dVeqkq8AV8eO66RkNj8RwAEEMSgPh8AS-yZTtdicK9h3_d6_Mu3aD2af_QWgOXSVj6cHWsy_0kaAgOlqmJvwoybIhXexKTXEeLhP5oneoOyg_KTV6rz8bb4bGoSfTUfkFRMjLV0ga-NqPl96Tq5Ro_RM4yX3K78dRyhN_)

### LLM test sequence

![LLM Test Sequence](https://www.plantuml.com/plantuml/png/PP2z2iCW481tdy8n6V826KgWGwSkfPt5cgC8vXGz2Ntx-bEeiPj-Vdntk0IIdk9cc5HaFRz38F3C9QYLTXAfe5j4xF0LI3xj-QqC7FZ5IlDmgyoPMkFJgOdCt4SKbEvX6DcFPwjfLcqhGAXC1eqkqiWQYKzz6a8qr5MRZMOUoq6y4alZcwU_5iBEitQeVPqworbFR05Sy_zz0000)
