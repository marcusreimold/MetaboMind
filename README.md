# MetaboMind

MetaboMind ist ein modular aufgebauter KI-Agent. Die Kommunikation mit dem Sprachmodell erfolgt über die OpenAI ChatCompletion API und interne Informationen werden in einem Graphspeicher gehalten. Der Agent verknüpft jede neue Nachricht mit bestehenden Knoten und bewertet fortlaufend seine Entropie.

Die wichtigsten Funktionen greifen ineinander: Die **EmotionEngine** interpretiert Entropieänderungen als Gefühle, der **GoalManager** speichert Aufgaben und kontrolliert ihren Fortschritt, während **RepoManager** und **GitManager** es erlauben, Code direkt aus der Oberfläche heraus zu analysieren, zu testen und zu verändern.

So kann MetaboMind selbstständig Code ausführen, Ziele verfolgen und den eigenen Wissensgraphen erweitern. Die fünf Metabo-Regeln sind dauerhaft im Systemprompt eingebettet, wodurch alle Module zu einem ganzheitlichen Konzept verschmelzen.

## Voraussetzungen

Es werden Python-Pakete wie ``networkx`` und ``matplotlib`` benötigt. Diese lassen sich mit ``pip install networkx matplotlib`` installieren. Für die LLM-Anbindung ist ein OpenAI API-Key nötig.

## Module 
- **MetaboKernel**: Orchestriert Taktschritte und LLM-Aufrufe
 - **GraphMemory**: Speichert alle Nachrichten in einem gerichteten Graphen,
   berechnet einfache Einbettungen, merkt sich einen Zeitstempel pro Nachricht
  und verknüpft neue Einträge automatisch mit den ähnlichsten Vorgängern.
  Die Kanten tragen Gewichte zur Ähnlichkeitsbewertung. 
  
  Der Parameter ``max_nodes`` (Standard 1000) legt fest, wie viele Nachrichten
  maximal gespeichert werden. Sobald diese Grenze erreicht ist, entfernt der
  Speicher automatisch die ältesten Einträge. Werden Nachrichten entfernt und
  beim Anlegen des Speichers ein ``archive_path`` angegeben, landen die
  gelöschten Einträge zeilenweise in ``memory_archive.jsonl``.
- **PromptManager**: Baut Prompts aus Kontext und aktuellem Zustand
- **LLMInterface**: Bindet die OpenAI API ein
  (API-Schlüssel kann auch über die Umgebungsvariable `OPENAI_API_KEY` gesetzt werden)
- **EmotionEngine**: Leitet aus Entropieänderungen Emotionen ab
- **UIManager**: Tk-basierte Oberfläche
- **GoalManager**: Verwalten aktiver und erledigter Ziele
- **ContextSelector**: Wählt relevante Knoten für Prompts aus
  (Ähnlichkeitssuche)
- **GitManager**: Führt Git-Befehle wie ``status``, ``diff`` oder ``commit`` aus
- **RepoManager**: Beschränkt Dateioperationen auf das Repository und erlaubt
  das Ausführen von Python-Dateien, Schreiben und Lesen von Dateien sowie
  Kompilieren und Analysieren des Codes

## Funktionen

MetaboMind verbindet die Module zu einem autonomen Agenten mit vielfältigen
Fähigkeiten:

- speichert jede Nachricht im Graphspeicher samt Einbettung und Zeitstempel
- verknüpft neue Einträge automatisch mit den ähnlichsten Vorgängern
- bewertet Entropieänderungen als Emotion und zeigt deren Intensität an
- führt regelmäßig Selbstreflexionen durch und ergänzt das Gedächtnis
- durchsucht den Speicher nach Stichwörtern und liefert kontextabhängige Antworten
- verwaltet Ziele, die in der Oberfläche angelegt, abgeschlossen oder entfernt
  werden können
- führt Python-Dateien aus, kompiliert das Repository, startet Testläufe und liefert Code-Statistiken (Dateien, Zeilen, Funktionen, Klassen, Schleifen)
- erlaubt Git-Operationen wie ``status`` oder ``commit`` direkt über Chat oder GUI
- zeigt mit ``git diff`` oder dem Diff-Button die aktuellen Änderungen an
- wendet Patches im Unified-Diff-Format per ``patch``-Befehl oder Patch-Button an
- durchsucht den Repository-Code mit ``grep <Begriff>`` nach Vorkommen
- kann Dateien im Repository lesen, bearbeiten und ausführen
- listet Verzeichnisse mit ``ls [Pfad]`` auf
- nutzt die OpenAI Function-Calling API, um Repository- und Git-Funktionen autonom aufzurufen
- das LLM entscheidet über Ausgaben an den Nutzer und ruft dazu die Funktion ``send_user_message`` auf
- die fünf Metabo-Regeln sind im Systemprompt hinterlegt und steuern das Verhalten des Sprachmodells
- speichert Gedächtnis und Ziele automatisch und auf Wunsch manuell ab
- stellt den Gedächtnisgraphen, zentrale Knoten und Statistiken grafisch dar
- kann den Gedächtnisgraphen als PNG exportieren (Befehl `export <Datei>` oder Export-Button)
- zeigt die häufigsten Wörter im Gedächtnis an (Chat-Befehl ``words``)
- durch Suchen mit ``archive <Begriff>`` kann auch das Archiv durchsucht werden
- das LLM kann den Speicher über ``memory_search`` gezielt nach Begriffen durchsuchen
- der kürzeste Pfad zwischen zwei Begriffen wird mit ``path <wort1> <wort2>`` ermittelt (auch im Such-Reiter)

## Starten der Anwendung

Eine grafische Umgebung wird benötigt. Danach kann der Agent so gestartet werden:

```bash
python3 ui_manager.py
```

Soll keine grafische Oberfläche verwendet werden, kann der Agent auch im
Terminal gestartet werden:

```bash
python3 cli.py
```

Links befindet sich das Chatfenster, rechts die Reiter für Diagnosedaten. Unten zeigt ein Fortschrittsbalken die aktuelle Emotionsintensität und der aktuelle Entropiewert wird angezeigt. Die Oberfläche nutzt ein dunkles Farbschema und unterstützt einfache Markdown-Formatierung mit hervorgehobenen Codeblöcken. Die Tabs aktualisieren sich jede Sekunde. Alle Textfelder besitzen Scrollleisten. Ein zusätzlicher Reiter ermöglicht die Suche im Gedächtnis. Dort lassen sich Begriffe oder das Archiv durchsuchen sowie der kürzeste Pfad zwischen zwei Wörtern anzeigen. Der Tab "Graph" visualisiert die Verbindungen im Gedächtnis und bietet einen Export-Button, um den Graphen als PNG zu speichern. Ein Analyse-Tab listet die wichtigsten Knoten nach Zentralität und zeigt die häufigsten Wörter im Gedächtnis. Der Tab "Statistik" zeigt Anzahl der Knoten, Kanten und den Entropiewert. Im Tab "Entropieverlauf" kann man den Verlauf des Entropiewerts grafisch verfolgen. Ein weiterer Tab "Ziele" erlaubt das Anlegen, Abschließen und Entfernen von Zielen. Der Speicher kann manuell über einen "Speichern"-Button oder automatisch jede Minute in ``memory.json`` und ``goals.json`` gesichert werden und wird beim Start wieder geladen. Wird die Grenze von 1000 Nachrichten überschritten, entfernt MetaboMind automatisch die ältesten Einträge.
Während der Laufzeit kann MetaboMind auch ohne neue Nutzereingabe Nachrichten schicken, wenn das Sprachmodell dies für sinnvoll hält.
Sind zusätzlich ein Archiv-Pfad und ``archive_path`` gesetzt, landen diese Einträge in ``memory_archive.jsonl``. Die gespeicherten Kanten enthalten ein Gewicht, das die semantische Ähnlichkeit angibt.
Ein weiterer Tab "Repository" bietet Buttons für ``Analyse``, ``Test``, ``Tests``, ``Status``, ``Diff`` und ``Commit``, ``Patch`` sowie ``Grep``. Damit können Codeanalyse, Kompilierung, Testläufe, Git-Aktionen und Code-Suchen direkt aus der Oberfläche ausgelöst werden.
Darunter befindet sich ein Dateipfadfeld mit Editor, über das Dateien geladen, gespeichert und ausgeführt werden können. Ein "List"-Button zeigt den Inhalt eines Verzeichnisses an.
LLM-Anfragen laufen in einem separaten Thread, sodass die Oberfläche während der Verarbeitung nicht blockiert. Zusätzlich führt der Kernel alle zehn Sekunden einen kurzen Selbstreflexionsschritt aus, der als neuer Knoten im Gedächtnis gespeichert wird. Bei Bedarf kann das LLM dabei eigenständig Nachrichten an den Nutzer senden.
Git-Befehle lassen sich direkt im Chat mit ``git <Befehl>`` ausführen, z.B. ``git status`` oder ``git commit Mein Text``.
Dateioperationen sind über ``read <Pfad>``, ``write <Pfad>`` (gefolgt vom Inhalt in der nächsten Zeile) und ``run <Pfad>`` möglich. Der Befehl ``ls`` listet ein Verzeichnis auf. ``test`` kompiliert alle Python-Dateien, ``tests`` führt ``pytest`` aus und ``analyse`` zeigt neben Dateizahl und Zeilen auch die Anzahl von Funktionen, Klassen und Schleifen. Mit ``patch`` kann ein Diff eingespielt werden. ``git log`` zeigt die letzten Commits. Das LLM ruft diese Befehle bei Bedarf eigenständig über die Function-Calling API auf.
Suchanfragen im Gedächtnis sind über ``search: <Begriff>`` möglich und liefern passende Einträge.
``grep <Begriff>`` durchsucht den Repository-Code nach Vorkommen.
Mit ``archive <Begriff>`` lässt sich das Archiv nach älteren Einträgen durchsuchen.
=======
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
