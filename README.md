# MetaboMind

MetaboMind is a simple goal-oriented reasoning demo. The main entry point is
`main.py` which launches a small GUI and handles the cycle logic.

Runtime data such as logs or graphs are stored in the `data/` directory.
The `MemoryManager` also keeps its entropy snapshot under
`data/last_entropy.txt` by default.

All prompts used for LLM interactions are defined centrally in `cfg/config.py`.
The Metabo rules are stored in `METABO_PROMPT` and automatically prefixed to
each system prompt.

## Diagrams

### Class overview

![Class Diagram](https://www.plantuml.com/plantuml/png/RP512i8m44NtFKKlq2j8GQIuA8AuwNACOnfC9pAPBdfxQMaqYTaD_tzctcTQBy0oJxPI5holUp0KHXIuk-EYBEvAvy3sGA2Hlvd9yP9gPn8aCOuwXlUuYrTyMbIhUY9jA6oymKiIOJ0q0EaBgn6zC8ZZQcMgc-QG44NpviLikPTIvkuVMXueCiKhjrHM-zUiW92P2NieMxhQ8ZtMNtq0)

### Cycle sequence

![Sequence Diagram](https://www.plantuml.com/plantuml/png/XP8nQyCm48Lt_OeZKpgqFq1329JIoHGA7JA9gtHr1F99IETI__j87j8uDcGJttjwUdVeM0IpZ4DGQ2Lc-2gKLQh8Mv-G1NO3Udv9qmwmG5VF2xKZmU_uEjb02_uUCNJ8sD-bTJJ4F6qfd_GJo8gF_CQzvsNSoVC9kV_8zan5CjQcgZM5vyFSIOFdD0e8_ObgO1R-ksd88vjX1iOsic_M9tNZQLSstj7Wo7f7PeYEzgiRDuDgw4bCNy7QjfXRGs5CvHnbRRnVGmjbgat8vAlqC1-TCv9z2YJbSHdy9LFHLl9rlvdA64GTYLtxB1S0)
