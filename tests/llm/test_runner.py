import os
import sys
import yaml

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from control.metabo_cycle import run_metabo_cycle
from goals.goal_engine import update_goal
from goals.goal_manager import GoalManager

LOG_PATH = os.path.join('data', 'llm_test_log.md')


def load_cases(path: str):
    with open(path, 'r', encoding='utf-8') as fh:
        return yaml.safe_load(fh) or []


def determine_mode(delta: float) -> str:
    return 'YANG' if delta >= 0 else 'YIN'


def check_case(idx: int, case: dict, goal_mgr: GoalManager, logger):
    user_input = case['input']
    exp = case.get('expected', {})
    result = run_metabo_cycle(user_input)
    new_goal = update_goal(
        user_input=user_input,
        last_reflection=result.get('reflection', ''),
        triplets=result.get('triplets', []),
    )
    goal_mgr.set_goal(new_goal)

    answer = result.get('reflection', '')
    emotion = result.get('emotion', '')
    delta = result.get('delta', 0.0)
    mode = determine_mode(delta)

    passed = True
    reasons = []

    if exp.get('emotion') is not None and emotion != exp['emotion']:
        passed = False
        reasons.append(f"expected emotion {exp['emotion']}, got {emotion}")
    rng = exp.get('delta_range')
    if isinstance(rng, list) and len(rng) == 2:
        if not (rng[0] <= delta <= rng[1]):
            passed = False
            reasons.append(f"Δ{delta:+.2f} not in range {rng}")
    if exp.get('mode') and mode != exp['mode']:
        passed = False
        reasons.append(f"expected {exp['mode']}, got {mode}")
    if exp.get('answer_contains') and exp['answer_contains'] not in answer:
        passed = False
        reasons.append(
            f"answer does not contain '{exp['answer_contains']}'")
    if exp.get('goal_hint'):
        if exp['goal_hint'] not in new_goal:
            passed = False
            reasons.append(
                f"goal not adjusted to '{exp['goal_hint']}'")

    if passed:
        msg = f"✅ Test {idx} passed"
    else:
        msg = f"❌ Test {idx} failed: {'; '.join(reasons)}"
    print(msg)
    if logger:
        logger.write(msg + '\n')
    return passed


def run_tests(path: str = os.path.join('tests', 'llm', 'test_dialogs.yaml')) -> None:
    cases = load_cases(path)
    goal_mgr = GoalManager()
    logger = None
    if LOG_PATH:
        os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
        logger = open(LOG_PATH, 'a', encoding='utf-8')
    try:
        for idx, case in enumerate(cases, 1):
            check_case(idx, case, goal_mgr, logger)
    finally:
        if logger:
            logger.close()


if __name__ == '__main__':
    run_tests()
