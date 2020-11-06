# Необходимо написать парсер простого языка логических запросов.
import re


def parse(query: str) -> dict:
    """ Парсит логический запрос в дерево операций
    @param query: логический запрос вида 'Пол="М" AND (Возраст>25 OR Стаж>5)'.
        Поддерживаемые операции сравнения: = != > < >= <=
        Поддерживаемые логические операции: AND OR, приоритет одинаковый, группировка скобками
        Поддерживаемые типы литералов: int float str (двойные кавычки внутри строки не допускаются)
    @return: словарь, содержащий дерево операций (см. ассерты)
        Поддерживаемые типы узлов (type):
            leaf - узел, представляющий операцию сравнения
            node - узел, представляющий логическую операцию, имеет два подузла - left, right
    """
    querylist = re.split(r"\s*(\(|\)|AND|OR)\s*", query)
    querylist = list(filter(lambda a: a != '', querylist))

    parenthesesstack = [[]]
    for item in querylist:
        if item == '(':
            parenthesesstack.append([])
        elif item == ')':
            laststackitem = parenthesesstack.pop(-1)
            parenthesesstack[-1].append(getnode(laststackitem))
        else:
            parenthesesstack[-1].append(item)
    laststackitem = parenthesesstack.pop(-1)
    assert parenthesesstack == [], 'Missed closing parenthesis.'
    return getnode(laststackitem)


def getleaf(query: str):
    # TODO: Use re tokens
    # TODO: Use logic expression in re

    leafpattern = re.compile(r'(?P<id>.+)\s*(?P<op>(=|!=|>=|<=|>|<))\s*(?P<literal>.+)')
    leafmatch = re.match(leafpattern, query)

    assertionmessage = f"Leaf '{query}' doesn't match initial requirements!"
    assert leafmatch is not None, assertionmessage

    # literal type converting
    literalmatch = re.match(r'((?P<int>\d+)|(?P<float>\d*.\d+)|\"(?P<str>[^\"]+)\"|(?P<err>.+))', leafmatch.group("literal"))
    if literalmatch.group('int'):
        literal = int(literalmatch.group("int"))
    elif literalmatch.group('float'):
        literal = float(literalmatch.group("float"))
    elif literalmatch.group('str'):
        literal = literalmatch.group("str")
    elif literalmatch.group('err'):
        raise Exception(f"In leaf '{query}' literal {leafmatch.group('literal')} isn't int, float or str.")

    return {
         'type': 'leaf',
         'op': leafmatch.group("op"),
         'id': leafmatch.group("id"),
         'literal': literal,
    }


def getnode(query):
    node = {
                'type': 'node',
                'op': None,
                'left': None,
                'right': None,
    }
    for i in range(len(query))[::-1]:
        if query[i] in ['AND', 'OR']:
            node['op'] = query[i]
            continue
        if isinstance(query[i], dict):
            item = query[i]
        else:
            item = getleaf(query[i])
        if node['right']:
            node['left'] = item
            if i > 0:
                prevnode = node
                node = {
                            'type': 'node',
                            'op': None,
                            'left': None,
                            'right': prevnode,
                }
        else:
            node['right'] = item
    return node


   # Необходимо написать функцию, пользуясь любыми библиотеками или без них.
   # Также необходимо написать 3-5 ассертов на разные граничные случаи:
   #   разную расстановку скобок, синтаксические ошибки в выражении и т.п.
   # При использовании сторонних библиотек парсинга необходимо написать 5-10 ассертов,
   # т.е. проверить как можно больше граничных случаев.

assert parse('Пол="М" AND (Возраст>25 OR Стаж>.5)') == {
    'type': 'node', 'op': 'AND',
    'left': {'type': 'leaf', 'op': '=', 'id': 'Пол', 'literal': "М"},
    'right': {
        'type': 'node', 'op': 'OR',
        'left': {'type': 'leaf', 'op': '>', 'id': 'Возраст', 'literal': 25},
        'right': {'type': 'leaf', 'op': '>', 'id': 'Стаж', 'literal': 0.5}
    }
}



# print(parse('Пол="М" AND (Возраст>25 OR Стаж>.5)'))
# print(getleaf('Пол="М"'))
# print(getleaf('Возраст >= 25'))
# print(getleaf('Стаж>""5"'))
# print(parse('Возраст>25 OR Стаж>.5 AND Имя="Василий"'))
