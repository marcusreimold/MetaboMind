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
GUI tabs while the chat only shows the user text and the final LLM answer.
The "Wissensgraph" tab visualises the knowledge graph with zoomable nodes and
edges, including tooltips for quick inspection. The graph can be panned by
dragging with the left mouse button, zoomed via the mouse wheel and it updates
automatically whenever new triplets are recorded.

## Diagrams

### Class overview

![Class Diagram](https://www.plantuml.com/plantuml/png/VLD1QiCm4Bpx5JecDFb03oNG5XD8A9Isa9DPorjRr5u5QKthtrTsx5HIxDw6tT7EQ4VQMGR3RLCdiWPhnH4KJH0PSltOoHh7IggXFW91YURAQRJfmjgU68cLfjJ0kHgBh_XPe-ohprGgcYQ-mHS7XPEY4r3vOcI5bWsmlahf0fzGgi8Jxmscx_l9Ng_teV3RCMRcY7jnLmm3iiRDMZN8Hacx4Om_l16spRD24wwNp-PjcPsD8bujaR9AMOSw1myE9PvfJxvJb7NkyCN7HNvqiqxw1CHs-n3ityD3pqyYxeMPnDsR86B2N08t4buMWTpGZHx0NyOpzg9cSAzf4SkENFRngjoQMujMS6KGYeZdgVr7yn-IX-SkjqCg-j_p2m00)

### Cycle sequence

![Sequence Diagram](https://www.plantuml.com/plantuml/png/XP4nYyCm38Lt_mhHAJUqFo33KJYEJbaAdOtEKNC6HpQoKYx__k8CRTC4kedlFJqzx6DM51twOD1f5BXa4fCcv9rFo0gx7ZqVqhW3pD1Cyq9jIF4dVeqkq8AV8eO66RkNj8RwAEEMSgPh8AS-yZTtdicK9h3_d6_Mu3aD2af_QWgOXSVj6cHWsy_0kaAgOlqmJvwoybIhXexKTXEeLhP5oneoOyg_KTV6rz8bb4bGoSfTUfkFRMjLV0ga-NqPl96Tq5Ro_RM4yX3K78dRyhN_)

### LLM test sequence

![LLM Test Sequence](https://www.plantuml.com/plantuml/png/PP2z2iCW481tdy8n6V826KgWGwSkfPt5cgC8vXGz2Ntx-bEeiPj-Vdntk0IIdk9cc5HaFRz38F3C9QYLTXAfe5j4xF0LI3xj-QqC7FZ5IlDmgyoPMkFJgOdCt4SKbEvX6DcFPwjfLcqhGAXC1eqkqiWQYKzz6a8qr5MRZMOUoq6y4alZcwU_5iBEitQeVPqworbFR05Sy_zz0000)
