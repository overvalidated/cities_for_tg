from copy import copy

from game_logic.game import *
from game_logic.basic_preparations import *

if __name__ == '__main__':
    human_score = 0
    computer_score = 0

    all_towns, towns = load_data('../towns.csv')
    bot_pools = prepare_bot_pool(towns)

    game = GameWithBot(
        towns_set=set(all_towns),
        towns=towns,
        bot_pool=copy(bot_pools[Difficulty.BOT_EASY])
    )

    while True:
        print("Новая игра!")
        print(f"Счет: человек {human_score} - {computer_score} компьютер")

        response, done = game.reset()
        if response is not None:
            print(response)
        while not done:
            city = input()
            if city == "сдаюсь":
                break
            elif city == "выйти из игры":
                exit(0)

            response, done = game.step(city)
            print(response)

        if done == 1:
            human_score += 1
        else:
            computer_score += 1
