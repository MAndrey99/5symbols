from collections import defaultdict
from typing import Callable


class Rule:
    """Класс для определения и применения правил в игре '5 букв'."""

    TOTAL_SYMBOLS = 5

    def __init__(self):
        self._exists: dict[str, set[int]] = defaultdict(set)
        self._match: dict[str, set[int]] = defaultdict(set)
        self._not_exists: set[str] = set()

    def add_exists_rule(self, symbol: str, not_matched_position: int) -> None:
        """Добавить правило, где символ существует, но не на указанной позиции."""
        self._exists[symbol].add(not_matched_position)

    def add_match_rule(self, symbol: str, matched_position: int) -> None:
        """Добавить правило, где символ совпадает на указанной позиции."""
        self._match[symbol].add(matched_position)

    def add_not_exists_rule(self, symbol: str) -> None:
        """Добавить правило, где символ не существует в слове."""
        self._not_exists.add(symbol)

    def matches(self, word: str) -> bool:
        """Проверить, соответствует ли слово всем установленным правилам."""
        for symbol, positions in self._match.items():
            if any(word[position] != symbol for position in positions):
                return False

        for symbol, positions in self._exists.items():
            if symbol not in word:
                return False
            if any(word[position] == symbol for position in positions):
                return False

        for position, symbol in enumerate(word):
            if symbol in self._not_exists:
                return False

        return True


# Глобальные переменные для состояния игры
all_words: list[str] = []
matched_words: set[str] = set()


def read_file(filename: str = 'russian_nouns.txt') -> None:
    """Прочитать слова из файла и инициализировать списки слов."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            words = [line.strip() for line in file if len(line.strip()) == Rule.TOTAL_SYMBOLS]
            all_words.extend(words)
            matched_words.update(words)
    except FileNotFoundError:
        print(f"Ошибка: Файл '{filename}' не найден.")


def apply_rule(rule: Rule) -> None:
    """Отфильтровать возможные слова на основе заданного правила."""
    global matched_words
    matched_words = {word for word in matched_words if rule.matches(word)}


def update_letter_position_frequencies() -> list[dict[str, int]]:
    """Вычислить частоту каждой буквы на каждой позиции среди оставшихся слов."""
    position_frequencies = [defaultdict(int) for _ in range(Rule.TOTAL_SYMBOLS)]
    for word in matched_words:
        for i, letter in enumerate(word):
            position_frequencies[i][letter] += 1
    return position_frequencies


def rank_word(word: str, position_frequencies: list[dict[str, int]]) -> float:
    """Ранжировать слово на основе частот букв на позициях."""
    score = 0
    used_letters = set()
    for i, letter in enumerate(word):
        if letter not in used_letters:
            used_letters.add(letter)
            score += position_frequencies[i].get(letter, 0)
    return -score  # Отрицательное значение для сортировки по убыванию


def get_top_words(n: int) -> list[str]:
    """Получить топ-N слов на основе ранжирования."""
    position_frequencies = update_letter_position_frequencies()
    ranked_words = sorted(
        all_words,
        key=lambda word: rank_word(word, position_frequencies)
    )
    return ranked_words[:n]


def update_rule(rule: Rule, word: str, result: str) -> None:
    """Обновить правила на основе результата для каждого символа в слове."""
    for position, symbol_result in enumerate(result):
        symbol = word[position]
        if symbol_result == '-':
            rule.add_not_exists_rule(symbol)
        elif symbol_result == '+':
            rule.add_exists_rule(symbol, position)
        elif symbol_result == '=':
            rule.add_match_rule(symbol, position)

    apply_rule(rule)


def input_with_validation(prompt: str, validation: Callable[[str], bool]) -> str:
    """Запросить ввод пользователя с проверкой валидности."""
    while True:
        answer = input(prompt)
        if validation(answer):
            return answer
        print("Некорректный ввод, пожалуйста, попробуйте снова.")


def choose_next_word() -> str:
    """Выбрать следующее слово на основе оставшихся возможных слов или топа ранжированных слов."""
    if len(matched_words) <= 5:
        print("Оставшиеся слова:", ', '.join(matched_words))
        if input_with_validation("Попробовать угадать слово (использовать первое)? (y/n): ", lambda x: x in ('y', 'n')) == 'y':
            return list(matched_words)[0]

    top_words = get_top_words(10)
    print("Топ слов:", ', '.join(top_words))
    index = int(input_with_validation("Введите номер выбранного слова (1-10): ", lambda x: x.isdigit() and 1 <= int(x) <= len(top_words)))

    result = top_words[index - 1]
    print(f"Ваш выбор: {result}")
    return result


def game_step(rule: Rule) -> bool:
    """Выполнить шаг игры: выбрать слово и обновить правила на основе обратной связи."""
    if len(matched_words) < 2:
        print("Игра окончена. Оставшиеся слова:", ', '.join(matched_words))
        return False

    word = choose_next_word()
    result = input_with_validation("Введите результат (например, '=-+=-'): ", lambda x: len(x) == Rule.TOTAL_SYMBOLS and all(c in '-+=' for c in x))
    update_rule(rule, word, result)
    return True


def main() -> None:
    """Главная функция для запуска игры."""
    read_file()
    rule = Rule()
    try:
        while game_step(rule):
            pass
    except KeyboardInterrupt:
        print("\nИгра прервана. Оставшиеся слова:", ', '.join(matched_words))


if __name__ == '__main__':
    main()
