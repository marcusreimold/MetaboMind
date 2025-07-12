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

![Sequence Diagram](https://www.plantuml.com/plantuml/png/XPF1QiCm38RlVWf3BksXBv33A6oZx306WmvwCggZ9OP4DhAoBcy_EuSsISDw2xz-V_vbAViemD9thG8hdlKn8gkG96TT01BzZW9dVpY-hQZFWsrnfXyyjEz0KDzHEi_3MkKJlrkquZozKkreZZivEW7L7smRZCAG4iwnli8NjAvQG0yCeVboU4bwxaZldcwDbDfHw4KB_egwgZVBs5MfkIVJZOAnMTba_rONXJICK1M5cjZ7qxSmfQx63pCuCaFgm7IfkDcgYKVlbZTcpnAwyW9N-CXC4TdPk5Khpdy0vxusWHr93ZM_SZB3KjSefax2lMqsqb97WX0Rly9RJZX32LCID7mjFUH3LPdKQMXHukCmy8CcIMla-IemnhvThC5aUz9JCLpK7gdA_yWV)
Updated after logging mode decision via logger.info.

