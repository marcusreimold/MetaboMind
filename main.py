from control.cycle_manager import CycleManager


def main():
    manager = CycleManager()
    text = input("Eingabe: ")
    result = manager.run_cycle(text)
    print(result)


if __name__ == "__main__":
    main()
