# MetaboMind

MetaboMind is a simple goal-oriented reasoning demo. The main entry point is
`main.py` which launches a small GUI and handles the cycle logic.

Runtime data such as logs or graphs are stored in the `data/` directory.
Triples extracted from reflections and user input are merged via `process_triples` into `data/metabograph.gml`.

## Diagrams

### Class overview

![Class Diagram](https://www.plantuml.com/plantuml/png/bZFLDsIwDET3nKIX6BVQJYSqLrpBcAAT3BLhOigxi94epUrIp-xGM47nWemcgJXPQgdF4FwzguYoUeBuTqsiDE5vgEZgmNH-ZhZj19IbWJBFG-4tvJ_xqdc30eSCccGJUPmxM8-aY8UVXhIMj9K07bEAyfSW5Uh1VsLV6Q5gtzohF5u2sDoyYf9prsIcuY5SZYf88N_yBQ)

### Cycle sequence

![Sequence Diagram](https://www.plantuml.com/plantuml/png/XP4nYyCm38Lt_mhHAJUqFo33KJYEJbaAdOtEKNC6HpQoKYx__k8CRTC4kedlFJqzx6DM51twOD1f5BXa4fCcv9rFo0gx7ZqVqhW3pD1Cyq9jIF4dVeqkq8AV8eO66RkNj8RwAEEMSgPh8AS-yZTtdicK9h3_d6_Mu3aD2af_QWgOXSVj6cHWsy_0kaAgOlqmJvwoybIhXexKTXEeLhP5oneoOyg_KTV6rz8bb4bGoSfTUfkFRMjLV0ga-NqPl96Tq5Ro_RM4yX3K78dRyhN_)

### LLM test sequence

![LLM Test Sequence](https://www.plantuml.com/plantuml/png/PP2z2iCW481tdy8n6V826KgWGwSkfPt5cgC8vXGz2Ntx-bEeiPj-Vdntk0IIdk9cc5HaFRz38F3C9QYLTXAfe5j4xF0LI3xj-QqC7FZ5IlDmgyoPMkFJgOdCt4SKbEvX6DcFPwjfLcqhGAXC1eqkqiWQYKzz6a8qr5MRZMOUoq6y4alZcwU_5iBEitQeVPqworbFR05Sy_zz0000)
