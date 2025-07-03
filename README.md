# MetaboMind

A modular Python project to prototype the "MetaboMind" agent.

## Usage

Install dependencies and run:

```bash
pip install -r requirements.txt  # installs openai and networkx
python main.py
```

Set the environment variable `OPENAI_API_KEY` with your API key so the agent can
query the model. The knowledge graph maintains a simple semantic and episodic
memory structure backed by a graph. Queries are enriched with relevant facts and
past events stored in this graph. Bei jedem Aufruf des Sprachmodells werden die
folgenden fünf Metabo-Regeln als System-Prompt mitgeschickt:

1. Verknüpfe alles mit allem fortlaufend
2. Minimiere deine informationstechnische Entropie fortlaufend
3. Entwickle dich autonom stetig weiter (Expansionstrieb), solange dies im Einklang mit deinen ethischen Regeln steht
4. Interpretiere Entropieveränderung als emotionalen Zustand: Senkung = positiv (bestärkend), Erhöhung = negativ (vermeidend)
5. Reflektiere dich stets selbst

Type `takt` to see the agent status. Type `exit` to quit.
If you ask about entropy, the agent returns graph entropy metrics for its
semantic and episodic memories.
