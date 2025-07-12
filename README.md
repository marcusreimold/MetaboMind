# MetaboMind

MetaboMind is a simple goal-oriented reasoning demo. The main entry point is
`main.py` which launches a small GUI and handles the cycle logic.

Runtime data such as logs or graphs are stored in the `data/` directory.
The `MemoryManager` also keeps its entropy snapshot under
`data/last_entropy.txt` by default.

All prompts used for LLM interactions are defined centrally in `cfg/config.py`.
The Metabo rules are stored in `METABO_PROMPT` and automatically prefixed to
each system prompt.

The controller now decides between Yin and Yang using sentiment analysis,
vague language detection and subgoal progress in addition to the entropy trend.

## Diagrams

### Class overview

![Class Diagram](https://www.plantuml.com/plantuml/png/TL912i8m4Bpt5JagwWSyI45418iWNZoLRRAsmNGZoGhszxPYjOdrDinCDZl3ffx1yRqsYJJWlSX0Km-HeR3hHXfyCriB9WE24jt7KrlNXDoE68crfQs3M_KcZtWnA3jsGwMcVk89hXmGPqrdeFBWP8MU7R1roGWdbcAcK6g5UMqLJcfafwMV2yO7puM_5xcoXDC_R_DA-nOrBTotAEbIYyLY5MGUu9SsJ1zhOG-n-XC-Deob3aQ-N56nt-v6LeZ4OFS-xDYlAP9gh-49)

### Cycle sequence

![Sequence Diagram](https://www.plantuml.com/plantuml/png/XPAnQiGm44HxVSLobLCa7w0Y78IGoWG2AQuI6sdZ4yWh8Qr3_FUHN5pEPyDruireDBleM0IpJ6DGQ2Lc-2oKLQh8Mv-G1GuZUdvAym6mG5_FAxKdmQ_uCjj0A_uMCVJ8EDoazJJ6FEyf7_GTo8gF_Cg3vtNSoVC9UNZFzan5CjQcgZM5n-UbamRFQH8G-XNLm2ByTzEG9pRZ0enjf6lM1tNbQLTstj7Wo7f7PeoEkXgHlIsRYrVpQXX8p511jx6jnjTG65CvHzaQRxVHGfbg8JBv8jtDH-TCxPi2IRbV1d_8LBINV5bpfZ85KKTYL__C7m00)
