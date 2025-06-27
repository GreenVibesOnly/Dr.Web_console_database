"""
Логика базы данных.
Реализует in-memory хранилище с поддержкой транзакций
(вложенных BEGIN, ROLLBACK, COMMIT).
Поддерживает команды SET, GET, UNSET, COUNTS, FIND.
Вся бизнес-логика базы сосредоточена здесь.
"""


from collections import defaultdict


class ConsoleDB:
    def __init__(self):
        # Стек баз данных: каждая транзакция — это новый словарь
        self.db_stack = [{}]
        # Стек счётчиков значений: сколько раз каждое значение встречается
        self.counts_stack = [defaultdict(int)]

    def _current(self):
        """Возвращает текущий (верхний) уровень базы и счётчиков"""
        return self.db_stack[-1], self.counts_stack[-1]

    def set(self, key, value):
        """
        Сохраняет значение для ключа.
        Обновляет счётчик старого значения (если было) и нового.
        """
        db, counts = self._current()
        old = self.get(key)
        if old:
            counts[old] -= 1
        db[key] = value
        counts[value] += 1

    def get(self, key):
        """
        Ищет значение ключа, начиная с самой новой транзакции.
        Возвращает None, если ключ не найден или удалён (None).
        """
        for db in reversed(self.db_stack):
            if key in db:
                return db[key]
        return None

    def unset(self, key):
        """
        Удаляет значение ключа (присваивает None).
        Также уменьшает счётчик для старого значения.
        """
        db, counts = self._current()
        val = self.get(key)
        if val:
            db[key] = None
            counts[val] -= 1

    def counts(self, value):
        """
        Показывает, сколько раз значение встречается во всех уровнях.
        Итоговая сумма всех счётчиков по стеку.
        """
        return sum(c[value] for c in self.counts_stack)

    def find(self, value):
        """
        Ищет все ключи, у которых текущее значение равно переданному.
        Принимает во внимание переопределения и удаления в верхних уровнях.
        """
        found = set()
        for db in reversed(self.db_stack):
            for k, v in db.items():
                if v == value:
                    found.add(k)
                elif v is None and k in found:
                    found.remove(k)
        return sorted(found)

    def begin(self):
        """
        Начинает новую транзакцию.
        Добавляет новые пустые уровни в стек базы и счётчиков.
        """
        self.db_stack.append({})
        self.counts_stack.append(defaultdict(int))

    def rollback(self):
        """
        Откатывает самую последнюю транзакцию.
        Удаляет верхний уровень.
        """
        if len(self.db_stack) == 1:
            return False  # нельзя откатить базовый уровень
        self.db_stack.pop()
        self.counts_stack.pop()
        return True

    def commit(self):
        """
        Применяет текущую транзакцию ко внутреннему уровню.
        Объединяет значения и обновляет счётчики.
        """
        if len(self.db_stack) == 1:
            return False

        top_db = self.db_stack.pop()
        self.counts_stack.pop()
        curr_db, curr_counts = self._current()

        for k, v in top_db.items():
            prev = curr_db.get(k)
            if prev:
                curr_counts[prev] -= 1
            if v is not None:
                curr_db[k] = v
                curr_counts[v] += 1
            else:
                curr_db.pop(k, None)

        return True
