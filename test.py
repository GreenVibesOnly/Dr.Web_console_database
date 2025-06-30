import sys
import unittest
from io import StringIO

from commands import CommandProcessor
from database import ConsoleDB


class TestConsoleDB(unittest.TestCase):
    def setUp(self):
        self.db = ConsoleDB()

    def test_set_get(self):
        """Проверка базовых команд SET и GET"""
        self.db.set("A", "10")
        self.assertEqual(self.db.get("A"), "10")

    def test_unset(self):
        """UNSET удаляет значение"""
        self.db.set("A", "10")
        self.db.unset("A")
        self.assertIsNone(self.db.get("A"))

    def test_counts(self):
        """COUNTS считает значения корректно"""
        self.db.set("A", "10")
        self.db.set("B", "10")
        self.db.set("C", "20")
        self.assertEqual(self.db.counts("10"), 2)
        self.assertEqual(self.db.counts("20"), 1)
        self.assertEqual(self.db.counts("30"), 0)

    def test_find(self):
        """FIND находит ключи по значению"""
        self.db.set("A", "10")
        self.db.set("B", "10")
        self.db.set("C", "20")
        self.assertEqual(self.db.find("10"), ["A", "B"])
        self.db.unset("A")
        self.assertEqual(self.db.find("10"), ["B"])

    def test_simple_transaction_rollback(self):
        """Откат одной транзакции"""
        self.db.set("A", "10")
        self.db.begin()
        self.db.set("A", "20")
        self.db.rollback()
        self.assertEqual(self.db.get("A"), "10")

    def test_simple_transaction_commit(self):
        """Фиксация одной транзакции"""
        self.db.set("A", "10")
        self.db.begin()
        self.db.set("A", "20")
        self.db.commit()
        self.assertEqual(self.db.get("A"), "20")

    def test_nested_rollback(self):
        """Откат вложенной транзакции"""
        self.db.set("A", "1")
        self.db.begin()
        self.db.set("A", "2")
        self.db.begin()
        self.db.unset("A")
        self.assertIsNone(self.db.get("A"))  # В верхней транзакции удалено
        self.db.rollback()
        self.assertEqual(self.db.get("A"), "2")

    def test_nested_commit(self):
        """Фиксация вложенной транзакции с удалением"""
        self.db.set("A", "1")
        self.db.begin()
        self.db.set("A", "2")
        self.db.begin()
        self.db.unset("A")
        self.db.commit()
        self.assertIsNone(self.db.get("A"))
        self.db.commit()
        self.assertIsNone(self.db.get("A"))

    def test_rollback_no_transaction(self):
        """ROLLBACK без активной транзакции"""
        self.assertFalse(self.db.rollback())

    def test_commit_no_transaction(self):
        """COMMIT без активной транзакции"""
        self.assertFalse(self.db.commit())

    def test_override_counts_in_transaction(self):
        """COUNTS учитывает изменения в транзакции"""
        self.db.set("A", "10")
        self.db.begin()
        self.db.set("A", "20")
        self.assertEqual(self.db.counts("10"), 0)
        self.assertEqual(self.db.counts("20"), 1)

    def test_counts_after_unset(self):
        """COUNTS обновляется после UNSET"""
        self.db.set("A", "10")
        self.db.unset("A")
        self.assertEqual(self.db.counts("10"), 0)


class TestCommandProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = CommandProcessor()
        self._stdout = sys.stdout
        sys.stdout = StringIO()  # Перехват stdout

    def tearDown(self):
        sys.stdout = self._stdout  # Возвращаем stdout после теста

    def get_output(self):
        return sys.stdout.getvalue().strip()

    def test_invalid_arguments(self):
        """Проверка сообщений об ошибках при недостатке аргументов"""
        self.processor.execute("SET", [])
        self.processor.execute("SET", ["A"])
        self.processor.execute("GET", [])
        self.processor.execute("UNSET", [])
        self.processor.execute("COUNTS", [])
        self.processor.execute("FIND", [])

        output = self.get_output().splitlines()
        self.assertTrue(all("ERROR: Invalid arguments"
                            in line for line in output))

    def test_valid_arguments(self):
        """SET с двумя аргументами работает корректно"""
        self.processor.execute("SET", ["A", "10"])
        self.processor.execute("GET", ["A"])
        output = self.get_output().splitlines()
        self.assertIn("10", output)


if __name__ == "__main__":
    unittest.main()
