import os
from metabomind.agent import MetaboAgent


def main():
    api_key = os.getenv("OPENAI_API_KEY")
    agent = MetaboAgent(api_key=api_key)
    print("MetaboMind CLI. Type 'exit' to quit.")
    while True:
        try:
            user_input = input('> ')
        except EOFError:
            break
        if user_input.strip().lower() == 'exit':
            break
        response = agent.process_input(user_input)
        print(response)


if __name__ == '__main__':
    main()
