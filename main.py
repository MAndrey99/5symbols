from collections import Counter, defaultdict
from typing import Callable


class Rule:
    """Class for defining and applying rules in the '5 letters' word-finding game."""

    TOTAL_SYMBOLS = 5

    def __init__(self):
        self._exists: dict[str, set[int]] = defaultdict(set)
        self._match: dict[str, set[int]] = defaultdict(set)
        self._not_exists: set[str] = set()

    def add_exists_rule(self, symbol: str, not_matched_position: int) -> None:
        """Add a rule where the symbol exists but not at a specified position."""
        self._exists[symbol].add(not_matched_position)

    def add_match_rule(self, symbol: str, matched_position: int) -> None:
        """Add a rule where the symbol matches at a specified position."""
        self._match[symbol].add(matched_position)

    def add_not_exists_rule(self, symbol: str) -> None:
        """Add a rule where the symbol does not exist in the word."""
        self._not_exists.add(symbol)

    def matches(self, word: str) -> bool:
        """Check if the word matches all the set rules."""
        for symbol, positions in self._match.items():
            if any(word[position] != symbol for position in positions):
                return False

        for position, symbol in enumerate(word):
            if symbol in self._not_exists:
                return False
            if symbol in self._exists and (position in self._exists[symbol] or symbol not in word):
                return False

        return True

    def need_check(self, symbol: str, position: int, found_symbols: set[str]) -> float:
        """Calculate the need to check a symbol based on current rules and found symbols."""
        if symbol in self._not_exists or (symbol in self._exists and position in self._exists[symbol]):
            return 0.0
        if symbol in self._match and position not in self._match[symbol]:
            return 0.1 if len(found_symbols) < Rule.TOTAL_SYMBOLS else 0.0

        return 1.0 - 0.07 * len(found_symbols)


# Global variables for the game state
all_words: list[str] = []
matched_words: set[str] = set()
symbols_counter = Counter()
found_symbols: set[str] = set()


def read_file(filename: str = 'russian_nouns.txt') -> None:
    """Read words from a file and initialize the word list and matched words set."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            words = [line.strip() for line in file]
            all_words.extend(words)
            matched_words.update(words)
        update_symbols_counter()
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")


def update_symbols_counter() -> None:
    """Update the counter for symbols in matched words."""
    symbols_counter.clear()
    for word in matched_words:
        symbols_counter.update(word)


def apply_rule(rule: Rule) -> None:
    """Filter matched words based on the given rule."""
    global matched_words
    matched_words = {word for word in matched_words if rule.matches(word)}


def rank_word(word: str, rule: Rule) -> float:
    """Rank a word based on the symbols that need to be checked."""
    checked = set()
    rank = 0.0
    for position, symbol in enumerate(word):
        if symbol in checked:
            continue
        checked.add(symbol)
        rank -= rule.need_check(symbol, position, found_symbols) * symbols_counter[symbol]
    return rank


def get_top_words(n: int, rule: Rule) -> list[str]:
    """Get the top N words based on ranking."""
    return sorted(all_words, key=lambda word: rank_word(word, rule))[:n]


def update_rule(rule: Rule, word: str, result: str) -> None:
    """Update rule based on the result feedback for each symbol in the word."""
    for position, symbol in enumerate(result):
        if symbol == '-':
            rule.add_not_exists_rule(word[position])
        elif symbol == '+':
            found_symbols.add(word[position])
            rule.add_exists_rule(word[position], position)
        elif symbol == '=':
            found_symbols.add(word[position])
            rule.add_match_rule(word[position], position)

    apply_rule(rule)
    update_symbols_counter()


def input_with_validation(prompt: str, validation: Callable[[str], bool]) -> str:
    """Prompt the user for input and validate it."""
    while True:
        answer = input(prompt)
        if validation(answer):
            return answer
        print("Invalid input, please try again.")


def choose_next_word(rule: Rule) -> str:
    """Choose the next word based on remaining matched words or top ranked words."""
    if len(matched_words) <= 5:
        print("Remaining words:", ', '.join(matched_words))
        if input_with_validation("Try to guess a word (use first one)? (y/n): ", lambda x: x in ('y', 'n')) == 'y':
            return list(matched_words)[0]

    top_words = get_top_words(10, rule)
    print("Top words:", ', '.join(top_words))
    index = int(input_with_validation("Enter the index of the word you chose (1-10): ", lambda x: x.isdigit() and 1 <= int(x) <= len(top_words)))

    result = top_words[index - 1]
    print(f"Your choice: {result}")
    return result


def game_step(rule: Rule) -> bool:
    """Perform a step in the game by selecting a word and updating rules based on feedback."""
    if len(matched_words) < 2:
        print("Game over. Remaining words:", ', '.join(matched_words))
        return False

    word = choose_next_word(rule)
    result = input_with_validation("Enter the result (e.g., '=-+=-'): ", lambda x: len(x) == Rule.TOTAL_SYMBOLS and all(c in '-+=' for c in x))
    update_rule(rule, word, result)
    return True


def main() -> None:
    """Main function to run the game."""
    read_file()
    rule = Rule()
    try:
        while game_step(rule):
            pass
    except KeyboardInterrupt:
        print("\nGame interrupted. Remaining words:", ', '.join(matched_words))


if __name__ == '__main__':
    main()
