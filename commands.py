"""
Обработчик команд.
Интерпретирует команды и вызывает соответствующие методы базы данных.
Использует словарь-диспетчер для чистой маршрутизации.
Отвечает за формат вывода.
"""


from database import ConsoleDB


def require_args(n):
    """Декоратор: проверяет количество аргументов"""
    def decorator(func):
        def wrapper(*wrapper_args, **kwargs):
            args = wrapper_args[1] if len(wrapper_args) > 1 else []
            if len(args) != n:
                raise TypeError()
            return func(*wrapper_args, **kwargs)
        return wrapper
    return decorator


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
        # Проверка введенных пользователем команды и значения
        if handler:
            try:
                handler(args)
            except TypeError:
                print(f"ERROR: Invalid arguments for command {cmd}")
        else:
            print(f"Unknown command: {cmd}")

    @require_args(2)
    def _set(self, args):
        self.db.set(args[0], args[1])

    @require_args(1)
    def _get(self, args):
        print(self.db.get(args[0]) or "NULL")

    @require_args(1)
    def _unset(self, args):
        self.db.unset(args[0])

    @require_args(1)
    def _counts(self, args):
        print(self.db.counts(args[0]))

    @require_args(1)
    def _find(self, args):
        keys = self.db.find(args[0])
        print(' '.join(keys) if keys else "NULL")
