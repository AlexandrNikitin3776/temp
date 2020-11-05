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
    return getnode(querylist)


def getleaf(query: str):
    leafpattern = re.compile(r'(?P<id>.+)\s*(?P<op>(=|!=|>=|<=|>|<))\s*(?P<literal>.+)')
    leafmatch = re.match(leafpattern, query)

    assertionmessage = f"Leaf '{query}' doesn't match initial requirements!"
    assert leafmatch is not None, assertionmessage

    # literal type converting
    literalmatch = re.match(r'((?P<int>\d+)|(?P<float>\d*.\d+)|(?P<str>\".+\"))', leafmatch.group("literal"))
    if literalmatch.group('int'):
        literal = int(leafmatch.group("literal"))
    elif literalmatch.group('float'):
        literal = float(leafmatch.group("literal"))
    elif literalmatch.group('str'):
        literal = leafmatch.group("literal")
    else:
        raise Exception(f"Leaf '{query}' literal isn't int, float or str.")

    return {
         'type': 'leaf',
         'op': leafmatch.group("op"),
         'id': leafmatch.group("id"),
         'literal': literal,
    }


def getnode(querylist: list):
    i = 0
    while i < len(querylist):
        if querylist[i] == '(':
            pass
        elif querylist[i] == ')':
            pass
        elif querylist[i] in ['AND', 'OR']:
            return {
                'type': 'node',
                'op': querylist[i],
                'left': querylist[:i],
                'right': getnode(querylist[i + 1:]),
            }
        else:
            querylist[i] = getleaf(querylist[i])
        i += 1



# def getnode(query:str):
#     nodepattern = re.compile(r'(?P<left>\b((?!(AND|OR)))\b\S+)\s+(?P<op>(AND|OR))\s+(?P<right>.+)')
#     nodematch = re.match(nodepattern, query)

#     if nodematch is None:
#         return getleaf(query)

#     return {
#         'type': 'node',
#         'op': nodematch.group("op"),
#         'left': getleaf(nodematch.group("left")),
#         'right': getnode(nodematch.group("right")),
#     }


   # Необходимо написать функцию, пользуясь любыми библиотеками или без них.
   # Также необходимо написать 3-5 ассертов на разные граничные случаи:
   #   разную расстановку скобок, синтаксические ошибки в выражении и т.п.
   # При использовании сторонних библиотек парсинга необходимо написать 5-10 ассертов,
   # т.е. проверить как можно больше граничных случаев.

# assert parse('Пол="М" AND (Возраст>25 OR Стаж>.5)') == {
#    'type': 'node', 'op': 'AND',
#    'left': {'type': 'leaf', 'op': '=', 'id': 'Пол', 'literal': "М"},
#    'right': {
#        'type': 'node', 'op': 'OR',
#        'left': {'type': 'leaf', 'op': '>', 'id': 'Возраст', 'literal': 25},
#        'right': {'type': 'leaf', 'op': '>', 'id': 'Стаж', 'literal': 0.5}
#    }
# }

print(parse('Пол="М" AND (Возраст>25 OR Стаж>.5)'))
# print(getleaf('Пол="М"'))
# print(getleaf('Возраст >= 25'))
# print(getleaf('Стаж>""5"'))
# print(getnode('Возраст>25 OR Стаж>.5 AND Имя="Василий"'))
