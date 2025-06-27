"""
Точка входа.
Запускает консольное приложение и принимает команды от пользователя.
Управляет вводом, обрабатывает EOF и KeyboardInterrupt,
передаёт команды в обработчик.
"""


from commands import CommandProcessor


def main():
    processor = CommandProcessor()
    try:
        while True:
            try:
                line = input("> ").strip()
            except EOFError:
                print()  # Завершение по Ctrl+D
                break
            if not line:
                continue
            parts = line.split()
            cmd, args = parts[0], parts[1:]
            # Выполнить команду или вывести сообщение об ошибке
            processor.execute(cmd, args)
    except KeyboardInterrupt:
        print("\nInterrupted.")  # Завершение по Ctrl+C


if __name__ == "__main__":
    main()
