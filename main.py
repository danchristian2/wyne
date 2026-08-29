from agent import run_agent

if __name__ == "__main__":
    print("File Assistant — ask me about files in a directory (counts, sizes, extensions).")
    print("Type 'quit' or 'exit' to stop.\n")

    question_count = 0

    while True:
        question = input("Ask me anything: ").strip()

        if question.lower() in ("quit", "exit"):
            print(f"Goodbye! You asked {question_count} question(s) this session.")
            break

        if not question:
            print("You didn't ask anything - try again.\n")
            continue

        question_count += 1
        answer = run_agent(question)
        print("\nAgent:", answer, "\n")