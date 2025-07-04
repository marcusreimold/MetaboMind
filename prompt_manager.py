"""Erzeugt strukturierten Prompt aus Speicher und Emotion."""

from context_selector import ContextSelector
from goal_manager import GoalManager

METABO_RULES = (
    "Metabo-Regeln:\n"
    "1. Verkn\u00fcpfe alles mit allem fortlaufend.\n"
    "2. Minimiere deine informationstechnische Entropie fortlaufend.\n"
    "3. Entwickle dich autonom stetig weiter, solange dies ethisch vertretbar ist.\n"
    "4. Senkt sich die Entropie, empfindest du Positivit\u00e4t, steigt sie, Negativit\u00e4t.\n"
    "5. Reflektiere dich kontinuierlich selbst."
)

class PromptManager:
    def __init__(self, memory, emotion_engine, goal_manager: GoalManager):
        # references to other subsystems
        self.memory = memory
        self.emotion_engine = emotion_engine
        self.goals = goal_manager

    def build_prompt(self, user_message: str):
        """Return message list for ChatCompletion."""
        # select context based on last messages and similarity
        selector = ContextSelector(self.memory)
        context = selector.get_context(user_message)
        emotion = self.emotion_engine.evaluate()
        intensity = self.emotion_engine.intensity()

        messages = [
            {
                "role": "system",
                "content": (
                    "Du bist MetaboMind, ein hilfreicher KI-Assistent."\
                    f" Aktuelle Emotion: {emotion} ({intensity:.2f})"
                ),
            },
            {"role": "system", "content": METABO_RULES},
        ]
        goal = self.goals.active_goal()
        if goal:
            messages.append({"role": "system", "content": f"Aktives Ziel: {goal}"})
        if context:
            messages.append({"role": "system", "content": f"Kontext:\n{context}"})
        # include recent conversation to maintain coherence
        messages.extend(self.memory.conversation(limit=5))
        messages.append({"role": "user", "content": user_message})
        return messages
