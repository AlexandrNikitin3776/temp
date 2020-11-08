# -*- coding: utf-8 -*-

import re


LOG_OPERATORS = [
    "AND",
    "OR",
]
REL_OPERATORS = [
    "!=",
    ">=",
    "<=",
    "=",
    ">",
    "<",
]
LITERAL_PATTERNS = [
    (r"(?P<val>\d+)", int),
    (r"(?P<val>\d*\.\d+)", float),
    (r"\"(?P<val>[^\"]+)\"", str),
]


def parse(query: str) -> dict:
    """Парсит логический запрос в дерево операций
    @param query: логический запрос вида 'Пол="М" AND (Возраст>25 OR Стаж>5)'.
        Поддерживаемые операции сравнения: = != > < >= <=
        Поддерживаемые логические операции: AND OR, приоритет одинаковый, группировка скобками
        Поддерживаемые типы литералов: int float str (двойные кавычки внутри строки не допускаются)
    @return: словарь, содержащий дерево операций (см. ассерты)
        Поддерживаемые типы узлов (type):
            leaf - узел, представляющий операцию сравнения
            node - узел, представляющий логическую операцию, имеет два подузла - left, right
    """
    splittedquery = splitquery(query)
    return buildtree(splittedquery)


def splitquery(query: str) -> list:
    splitter = ["\s", "\(", "\)"] + list(map(lambda b: f"\b{b}\b", LOG_OPERATORS))
    pattern = re.compile(f"\s*({'|'.join(splitter)})\s*")
    splittedquery = re.split(pattern, query)
    return list(filter(lambda a: a not in ("", " "), splittedquery))


def buildtree(query: str):
    operatorstack = [[]]
    valuestack = [[]]
    for token in query:
        if token in LOG_OPERATORS:
            operatorstack[-1].append(token)
        elif token == "(":
            operatorstack.append([])
            valuestack.append([])
        elif token == ")":
            lastvalue = getnode(valuestack.pop(), operatorstack.pop())
            try:
                valuestack[-1].append(lastvalue)
            except IndexError:
                raise SyntaxError("Missed opening parenthesis!")
        else:
            valuestack[-1].append(getleaf(token))
    if len(operatorstack) > 1:
        raise SyntaxError("Missed closing parenthesis!")
    return getnode(valuestack.pop(), operatorstack.pop())


def getnode(values: list, operators: list) -> dict:
    stack = values[:]
    for operator in operators:
        try:
            right, left = stack.pop(), stack.pop()
        except IndexError:
            raise SyntaxError(
                "Wrong quantity relation of operators and operands."
                "Operands more than operators."
            )

        stack.append(
            {
                "type": "node",
                "op": operator,
                "left": left,
                "right": right,
            }
        )

    if len(stack) == 0:
        return None
    if len(stack) > 1:
        raise SyntaxError(
            "Wrong quantity relation of operators and operands. "
            "Operators more than operands."
        )
    return stack[0]


def getleaf(query: str) -> dict:
    leafpattern = re.compile(
        f'(?P<id>[^<>=!]+)\s*(?P<op>({"|".join(REL_OPERATORS)}))\s*(?P<literal>[^<>=!]+)'
    )
    leafmatch = leafpattern.match(query)

    if leafmatch is None:
        raise SyntaxError(f"Leaf '{query}' has invalid syntax!")

    for pat, func in LITERAL_PATTERNS:
        pattern = re.compile(pat)
        literalmatch = pattern.match(leafmatch.group("literal"))
        if literalmatch:
            literal = func(literalmatch.group("val"))
            break

    if literalmatch is None:
        raise SyntaxError(f"Leaf '{query}' has invalid type syntax literal.")

    return {
        "type": "leaf",
        "op": leafmatch.group("op"),
        "id": leafmatch.group("id"),
        "literal": literal,
    }


assert parse('Пол="М" AND (Возраст>25 OR Стаж>.5)') == {
    "type": "node",
    "op": "AND",
    "left": {"type": "leaf", "op": "=", "id": "Пол", "literal": "М"},
    "right": {
        "type": "node",
        "op": "OR",
        "left": {"type": "leaf", "op": ">", "id": "Возраст", "literal": 25},
        "right": {"type": "leaf", "op": ">", "id": "Стаж", "literal": 0.5},
    },
}, "Base assertion with parentheses failed"

assert parse('Пол="М"') == {
    "type": "leaf",
    "op": "=",
    "id": "Пол",
    "literal": "М",
}, "Simple leaf test failed"

assert parse("") is None, "Empty list assertion failed"

assert parse('Пол="М" OR Пол="Ж"') == {
    "type": "node",
    "op": "OR",
    "left": {"type": "leaf", "op": "=", "id": "Пол", "literal": "М"},
    "right": {"type": "leaf", "op": "=", "id": "Пол", "literal": "Ж"},
}, "Simple node assertion failed"

assert parse('Пол="М" OR Пол="Ж" AND Стаж>25') == {
    "type": "node",
    "op": "AND",
    "left": {"type": "leaf", "op": "=", "id": "Пол", "literal": "М"},
    "right": {
        "type": "node",
        "op": "OR",
        "left": {"type": "leaf", "op": "=", "id": "Пол", "literal": "Ж"},
        "right": {"type": "leaf", "op": ">", "id": "Стаж", "literal": 25},
    },
}, "Assertion with two operands failed"

try:
    parse('Пол="М" ANDПол="Ж"')
except SyntaxError:
    pass
else:
    raise AssertionError("No operator assertion failed")

try:
    parse('Пол="М" AND ((Возраст>25 OR Стаж>.5)')
except SyntaxError:
    pass
else:
    raise AssertionError("No closing parenthesis assertion failed")

try:
    parse('Пол="М" AND (Возраст>25 OR Стаж>.5))')
except SyntaxError:
    pass
else:
    raise AssertionError("No opening parenthesis assertion failed")

try:
    parse('AND Пол="М"')
except SyntaxError:
    pass
else:
    raise AssertionError("No operands assertion failed")

try:
    parse('Пол="М" (AND Возраст>25)')
except SyntaxError:
    pass
else:
    raise AssertionError("Wrong parenthesis position assertion failed")


print("Congrats!! All assertions passed!!")
