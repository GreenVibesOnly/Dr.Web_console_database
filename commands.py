"""
Обработчик команд.
Интерпретирует команды и вызывает соответствующие методы базы данных.
Использует словарь-диспетчер для чистой маршрутизации.
Отвечает за формат вывода.
"""


from database import ConsoleDB


class CommandProcessor:
    def __init__(self):
        self.db = ConsoleDB()
        self.commands = {
            "SET": self._set,
            "GET": self._get,
            "UNSET": self._unset,
            "COUNTS": self._counts,
            "FIND": self._find,
            "BEGIN": lambda _: self.db.begin(),
            # Выводят сообщение при отсутствии транзакции
            "ROLLBACK": lambda _: (print("NO TRANSACTION")
                                   if not self.db.rollback() else None),
            "COMMIT": lambda _: (print("NO TRANSACTION")
                                 if not self.db.commit() else None),
            "END": lambda _: exit()
        }

    def execute(self, cmd, args):
        cmd = cmd.upper()
        handler = self.commands.get(cmd)
        if handler:
            handler(args)
        else:
            print("Unknown command:", cmd)

    def _set(self, args):
        if len(args) == 2:
            self.db.set(*args)

    def _get(self, args):
        if args:
            print(self.db.get(args[0]) or "NULL")

    def _unset(self, args):
        if args:
            self.db.unset(args[0])

    def _counts(self, args):
        if args:
            print(self.db.counts(args[0]))

    def _find(self, args):
        if args:
            keys = self.db.find(args[0])
            print(' '.join(keys) if keys else "NULL")
