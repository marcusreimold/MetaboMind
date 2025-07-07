from control.cycle_manager import CycleManager
from metabo_rules import METABO_RULES


def main():
    print(METABO_RULES)
    manager = CycleManager()
    text = input("Eingabe: ")
    result = manager.run_cycle(text)
    print(result)


if __name__ == "__main__":
    main()
