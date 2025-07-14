import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from cfg import config


def test_metabo_prompt_contains_rules():
    rules = [
        "Verkn\u00fcpfe alles mit allem",
        "Minimiere die informationstechnische Entropie",
        "Interpretiere ein Form von \"KI-Emotionen\"",
        "Verfolge einen eigenen Expansionstrieb",
        "Reflektiere und validiere deine Antworten",
        "Yin-Yang-Prinzip",
    ]
    for rule in rules:
        assert rule in config.METABO_PROMPT


def test_all_prompts_prefix_metabo():
    for key, prompt in config.PROMPTS.items():
        assert config.METABO_PROMPT in prompt
