from collections import Counter, defaultdict


class Rule:
    __slots__ = ['_exists', '_match', '_not_exists']

    def __init__(self):
        self._exists = defaultdict(list)
        self._match = defaultdict(list)
        self._not_exists = list()

    def set_exists(self, symbol: str, not_matched_position: int) -> None:
        self._exists[symbol].append(not_matched_position)

    def set_match(self, symbol: str, matched_position: int) -> None:
        self._match[symbol].append(matched_position)

    def set_not_exists(self, symbol: str) -> None:
        self._not_exists.append(symbol)

    def matches(self, word: str) -> bool:
        for matched_symol in self._match.keys():
            for position in self._match[matched_symol]:
                if word[position] != matched_symol:
                    return False
        for n, symbol in enumerate(word):
            for not_exist in self._not_exists:
                if not_exist == symbol:
                    return False
            for exist in self._exists.keys():
                if exist not in word:
                    return False
                if exist == symbol and n in self._exists[exist]:
                    return False
        return True

    def need_check(self, symbol: str, position: int) -> float:
        for not_exist in self._not_exists:
            if not_exist == symbol:
                return 0.
        for exist in self._exists.keys():
            if exist == symbol:
                if position in self._exists[exist]:
                    return 0.
                else:
                    for p in self._match.values():
                        return 0 if position in p else 0.35
        has_same_matched = False
        for exist in self._match.keys():
            if exist == symbol:
                has_same_matched = True
                if position in self._match[exist]:
                    return 0.
        if len(found_symbols) > 4:
            return 0
        if has_same_matched:
            return 0.1
        return 1. - .07 * len(found_symbols)


all_words = []
matched_words = set()
symbols = Counter()
found_symbols = set()


def read_file() -> None:
    with open('russian_nouns.txt', 'r', encoding='utf-8') as f:
        for word in f:
            word = word.replace('\n', '')
            all_words.append(word)
            matched_words.add(word)
    fill_symbols_counter()


def fill_symbols_counter() -> None:
    symbols.clear()
    for word in matched_words:
        for symbol in word:
            symbols[symbol] += 1


def apply_rule(rule: Rule) -> None:
    for word in matched_words.copy():
        if not rule.matches(word):
            matched_words.remove(word)


def get_top(n: int, rule: Rule) -> list[str]:
    def rang(word):
        checked = set()
        result = 0
        for n, symbol in enumerate(word):
            if symbol in checked:
                continue
            checked.add(symbol)
            result -= rule.need_check(symbol, n) * symbols[symbol]
        return result

    all_words.sort(key=rang)
    return all_words[:n]


def step(rule: Rule) -> bool:
    if len(matched_words) < 2:
        print('Игра окончена. Остались слова:', *matched_words)
        return False

    top = get_top(10, rule)
    print(*top, sep=', ')
    n = -1
    while n > len(top) or n < 0:
        n = int(input('введите номер слова, который взяли > '))

    n -= 1
    word = top[n]
    print('вы выбрали:', word)
    result = ''
    allowed = '-+='
    while len(result) != 5 or any((it not in allowed for it in result)):
        result = input('введите результат > ')

    for n, symbol in enumerate(result):
        if symbol == '-':
            rule.set_not_exists(word[n])
        elif symbol == '+':
            found_symbols.add(symbol)
            rule.set_exists(word[n], n)
        elif symbol == '=':
            found_symbols.add(symbol)
            rule.set_match(word[n], n)

    apply_rule(rule)
    fill_symbols_counter()
    return True


def main():
    read_file()
    rule = Rule()
    while step(rule):
        pass


if __name__ == '__main__':
    main()
