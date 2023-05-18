def present_city(city_name, last_letter):
    return city_name + f", тебе на {last_letter}"


class GameWithoutBot:
    def __init__(self,
                 towns_set,
                 towns, ):
        """
        Игра в города

        Вариант для игры вдвоем

        :param towns_set: Множество всех городов в России
        :param towns: Список городов по первой букве
        :param bot_pool: Список городов по первой букве, подвыборка из towns (зависит от уровня сложности)
        """
        super()
        self.all_cities = towns
        self.towns_set = towns_set
        self.used_cities = {letter: set()
                            for letter in self.all_cities}

        self.our_last_answer = None
        self.required_letter = None

        self.game_over = False

    def get_last_letter(self, city_name):
        idx = len(city_name) - 1
        last_letter = None
        while idx != 0:
            last_letter = city_name[idx]
            # если на такую букву есть города, и есть свободные, то выходим
            if last_letter in self.all_cities:
                break
            # иначе пробуем другую букву
            idx -= 1

        # если дошли до первой буквы то возвращаем ответ
        if idx == 0 or last_letter is None:
            return "Нет буквы на которую можно ответить"
        else:
            return last_letter

    def reset(self):
        self.used_cities = {letter: set()
                            for letter in self.all_cities}
        self.our_last_answer = None
        self.required_letter = None

        return None, 0

    def check_answer(self, human_answer):
        # проверяем ответ человека

        # проверяем что город на ту букву что надо
        if self.required_letter is not None and human_answer[0] != self.required_letter:
            return f"Город не на ту букву, нужно на {self.required_letter}"

        # проверяем что такой город есть в списке городов
        if human_answer not in self.towns_set:
            return "Такого города нет!"

        # проверяем что город не использован
        if human_answer in self.used_cities[human_answer[0]]:
            return "Этот город уже использован!"

        return None

    def save_answer(self, human_answer, last_letter):
        # первая буква в названии города
        first_letter = human_answer[0]
        # сохраняем город как использованный
        self.used_cities[first_letter].add(human_answer)

        self.our_last_answer = human_answer
        self.required_letter = last_letter

    def get_last_answer(self):
        if self.our_last_answer is None:
            return "Никто еще не отвечал"
        else:
            return present_city(self.our_last_answer, self.required_letter)

    def step(self, human_answer):
        if self.game_over:
            return "Игра окончена. Начни новую.", 0
        # все в нижнем регистре
        human_answer = human_answer.lower().replace('ё', 'е')
        status = self.check_answer(human_answer)
        if status is not None:
            return status, -1

        # ищем такую последнюю букву, на которую можно ответить
        last_letter = self.get_last_letter(human_answer)
        if len(last_letter) > 1:
            # если не находится последняя буква, то игра окончена
            return last_letter, 1

        if len(self.used_cities[last_letter]) == len(self.all_cities[last_letter]):
            return f"Больше нет городов на букву {last_letter}", 1

        self.save_answer(human_answer, last_letter)
        return self.get_last_answer(), 0


class GameWithBot(GameWithoutBot):
    def __init__(self,
                 towns_set,
                 towns,
                 bot_pool):
        """
        Игра в города

        Поддерживает несколько уровней сложности через разные наборы городов

        :param towns_set: Множество всех городов в России
        :param towns: Список городов по первой букве
        :param bot_pool: Список городов по первой букве, подвыборка из towns (зависит от уровня сложности)
        """
        super().__init__(towns_set, towns)
        self.all_cities = towns
        self.towns_set = towns_set
        self.bot_pool = bot_pool
        self.used_cities = {letter: set()
                            for letter in self.bot_pool}

        self.our_last_answer = None
        self.required_letter = None

    def reset(self, bot_starts=True):
        super().reset()

        if bot_starts:
            # выбираем первый город
            first_city = self.towns_set.pop()
            self.our_last_answer = first_city
            # определяем на какую букву нужно отвечать человеку
            self.required_letter = self.get_last_letter(first_city)
            # сохраняем город как уже названный
            self.used_cities[first_city[0]].add(first_city)
            return present_city(first_city, self.required_letter), 0
        else:
            return None, 0

    def step(self, human_answer):
        if self.game_over:
            return "Игра окончена. Начни новую.", 0
        # все в нижнем регистре
        human_answer = human_answer.lower().replace('ё', 'е')
        status = self.check_answer(human_answer)
        if status is not None:
            return status, 0

        # ищем такую последнюю букву, на которую можно ответить
        last_letter = self.get_last_letter(human_answer)
        if len(last_letter) > 1:
            # если не находится последняя буква, то игра окончена
            self.game_over = True
            return last_letter, 1

        # первая буква в названии города
        first_letter = human_answer[0]
        # сохраняем город как использованный
        self.used_cities[first_letter].add(human_answer)

        # выбираем возможные ответы
        available_cities = self.bot_pool[last_letter] - self.used_cities[last_letter]

        # выбираем город и последнюю букву на которую человек будет отвечать
        # если на эту букву нет свободных городов то выбираем другой город
        if len(available_cities) == 0:
            self.game_over = True
            return f"Больше не знаю городов на {last_letter} - ты победил", 1

        while True:
            if len(available_cities) == 0:
                self.game_over = True
                return "Нет городов, на которые ты сможешь ответить - игра окончена", 1
            our_answer = available_cities.pop()
            last_letter = self.get_last_letter(our_answer)
            # если вместо последней буквы пришло письмо, то ищем дальше
            if len(last_letter) == 1:
                self.save_answer(our_answer, last_letter)
                return self.get_last_answer(), 0
