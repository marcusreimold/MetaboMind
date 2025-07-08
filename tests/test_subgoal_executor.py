import subgoal_executor


def test_execute_first_subgoal(monkeypatch):
    recorded = []
    monkeypatch.setattr(subgoal_executor, "set_goal", lambda g: recorded.append(g))
    new_goal = subgoal_executor.execute_first_subgoal("orig", ["sg1", "sg2"])
    assert new_goal == "sg1"
    assert recorded == ["sg1"]


def test_execute_first_subgoal_fallback(monkeypatch):
    recorded = []
    monkeypatch.setattr(subgoal_executor, "set_goal", lambda g: recorded.append(g))
    new_goal = subgoal_executor.execute_first_subgoal("orig", [])
    assert new_goal == "orig"
    assert recorded == ["orig"]
