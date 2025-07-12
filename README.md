# MetaboMind

MetaboMind is a simple goal-oriented reasoning demo. The main entry point is
`main.py` which launches a small GUI and handles the cycle logic.

Runtime data such as logs or graphs are stored in the `data/` directory.
The `MemoryManager` also keeps its entropy snapshot under
`data/last_entropy.txt` by default.

All prompts used for LLM interactions are defined centrally in `cfg/config.py`.
The Metabo rules are stored in `METABO_PROMPT` and automatically prefixed to
each system prompt.

Yin and Yang are primarily selected by an LLM via the function
`decide_yin_yang_mode(user_input, metrics)`.  The metrics include the current
entropy delta and a rough emotion estimate.  The orchestrator keeps a simple
heuristic fallback and prints a short debug message whenever the mode changes.

## Diagrams

### Class overview

![Class Diagram](https://www.plantuml.com/plantuml/png/dZLBqsIwEEX3_YosFfUH3kIEeYigPBA3rso0GdtgOpHJFOzf24pVk1d3l3tvJpNDVkGApaldph2EoPZgaZAoUPh1qx0-nY0HtweCEvnVqT23sbclQRLracNwrZ7mAc8Ode_-UmlpmHiEi0TGydIJqPxjXWEQBvGcjXjqR80Mamswr73BSY3CVoe5ErzJXIWmyI0nnH4_WzRlfmVLMvlWyisbOtV2cteprEejFotlBOZDP7JPRGkWw0rTf4TSwhiaaOSjldB_Ax5ZIQmj3YfHjt26QjL9l7kD)

### Cycle sequence

![Sequence Diagram](https://www.plantuml.com/plantuml/png/hZJBawMhEIXv_oohp82h_QF7KIFSeloKgR5ykolOjeCOorOl---rOaTZZGlu8t7z8zm6K4JZpjEoNBIzfBbKKlXJG5-QBTYjen5O8wawwFDXC3cgwWN8nU2ghf4eMQzI6G5oA40xz2vOnr4CGfGR39h5XuIOng_I7iObExXJWJuq1hSeXs6devCcJgGhH1FNOBt_3XrIE-vxLGjTlK5Ft-oq07asnNODJeMt6TFa6ioie1O2aiX5D-A4OZ2yZ-nujryaVA-ORLsq3McWg-uhMKZyiiu82zk2KFNtQjpfrId8tFbXm6ZAUh6XwW_SVVojXx4oU5mCqB2xbb_tFw==)

