from game_logic import Difficulty


# TODO закончить функцию
def prepare_bot_pool(towns):
    """
    Подготавливает наборы городов для ботов

    :param all_towns: список всех городов
    :return:
    """
    pools = {}
    # для каждого уровня
    for level in Difficulty:
        pool = {}
        # проходимся по каждой букве
        for letter in towns:
            pool[letter] = set(tuple(towns[letter])[:level.value[0]])
        # сохраняем поднабор
        pools[level] = pool

    return pools


def load_data(path):
    """
    загружает необходимые для логики данные

    :path: путь к файлу с названиями городов
    """
    with open(path) as f:
        all_towns = [town.strip('\n').lower() for town in f]

    towns = {}
    for town in all_towns:
        if town[0] in towns:
            towns[town[0]].add(town)
        else:
            towns[town[0]] = set(town)

    return all_towns, towns
