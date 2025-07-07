from control.cycle_manager import CycleManager
from logs.logger import MetaboLogger
from metabo_rules import METABO_RULES


def main():
    print(METABO_RULES)
    manager = CycleManager(logger=MetaboLogger())
    text = input("Eingabe: ")
    result = manager.run_cycle(text)
    print(result)


if __name__ == "__main__":
    main()
