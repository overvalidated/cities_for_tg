from copy import copy
from random import random, shuffle
from collections import deque
import os

import telebot

from game_logic import Difficulty
from game_logic.game import GameWithBot, GameWithoutBot
from game_logic.basic_preparations import prepare_bot_pool, load_data

all_towns, towns = load_data('cities/towns.csv')
bot_pools = prepare_bot_pool(towns)

# очередь матчмейкера
user_queue_set = set()
user_queue = deque()
# объекты игры
game_instances = {}
# оппоненты и очередь на ход
opponents = {}
time_to_play = {}
# уровень сложности
difficult_level = {}

# инстанс бота
bot = telebot.TeleBot(token=os.environ["TELEBOT_TOKEN"])


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    bot.send_message(
        chat_id=message.chat.id,
        text="Это бот для игры города. \n"
             "Поддерживается игра с человеком или против бота.",
    )


@bot.message_handler(commands=['new_game_bot'])
def new_game_bot(message):
    chat_id = message.chat.id
    bot.send_message(
        chat_id=chat_id,
        text="Начинаем новую игру!"
    )

    if chat_id in game_instances:
        response, done = game_instances[chat_id].reset()
        bot.send_message(
            chat_id=chat_id,
            text=response
        )
    else:
        if chat_id not in difficult_level:
            bot.send_message(
                chat_id=chat_id,
                text="Ваша выбранная сложность неизвестна, вместо нее будет средняя"
            )
            diff = Difficulty.BOT_MEDIUM
            difficult_level[chat_id] = diff
        else:
            diff = difficult_level[chat_id]
        game_instances[chat_id] = GameWithBot(
            towns_set=set(all_towns),
            towns=towns,
            bot_pool=copy(bot_pools[diff])
        )
        response, done = game_instances[chat_id].reset()
        bot.send_message(
            chat_id=chat_id,
            text=response
        )


@bot.message_handler(commands=['new_game_human'])
def new_game_human(message):
    player1 = message.chat.id
    if player1 in opponents:
        bot.send_message(
            chat_id=player1,
            text='У тебя уже игра. Не беги, все получится.'
        )
        return

    if len(user_queue) > 0 and player1 not in user_queue_set:
        player2 = user_queue.pop()
        for player_id in [player1, player2]:
            bot.send_message(
                chat_id=player_id,
                text='Ваш соперник найден!'
            )

        game = GameWithoutBot(
            towns_set=set(all_towns),
            towns=towns
        )

        game_instances[player1] = game_instances[player2] = game
        opponents[player1] = player2
        opponents[player2] = player1

        order = [player1, player2]
        shuffle(order)

        time_to_play[order[0]] = True
        time_to_play[order[1]] = False
        bot.send_message(
            chat_id=order[0],
            text='Ты ходишь первым'
        )
        bot.send_message(
            chat_id=order[1],
            text='Твой оппонент ходит первым'
        )
    else:
        if player1 not in user_queue_set:
            user_queue_set.add(player1)
            user_queue.appendleft(player1)
        bot.send_message(chat_id=player1, text='Ждем второго игрока...')


@bot.message_handler(commands=['surrender'])
def surrender(message):
    player1 = message.chat.id
    if player1 not in game_instances:
        bot.send_message(
            chat_id=player1,
            text='Ты сдался даже не начав игру. Жалкое зрелище.'
        )
        return

    bot.send_message(
        chat_id=player1,
        text='Ультраслабый.' if random() < 0.1 else 'Вы сдались.'
    )
    if player1 in opponents:
        player2 = opponents[player1]
        bot.send_message(
            chat_id=player2,
            text='Ваш оппонент сдался'
        )
        # очищаем все массивы
        del game_instances[player1]
        del opponents[player2]
        del opponents[player1]
        del time_to_play[player1]
        del time_to_play[player2]
    else:
        del game_instances[player1]


@bot.message_handler(commands=['increase_difficulty'])
def inc_difficulty(message):
    difficulties = [diff for diff in Difficulty]
    chat_id = message.chat.id
    if chat_id in difficult_level:
        # находим этот уровень сложности и берем следующий
        new_difficulty = difficulties.index(difficult_level[chat_id]) + 1
        if new_difficulty == len(difficulties):
            bot.send_message(chat_id=chat_id,
                             text='Warning. The Slayer has entered the facility.')
            return
        else:
            difficult_level[chat_id] = difficulties[new_difficulty]
    else:
        difficult_level[chat_id] = Difficulty.BOT_HARD

    bot.send_message(chat_id=chat_id,
                     text=difficult_level[chat_id].value[1])


@bot.message_handler(commands=['decrease_difficulty'])
def dec_difficulty(message):
    difficulties = [diff for diff in Difficulty]
    chat_id = message.chat.id
    if chat_id in difficult_level:
        # находим этот уровень сложности и берем следующий
        new_difficulty = difficulties.index(difficult_level[chat_id]) - 1
        if new_difficulty < 0:
            bot.send_message(chat_id=chat_id,
                             text='Слабее только плакать в подушку.')
            return
        else:
            difficult_level[chat_id] = difficulties[new_difficulty]
    else:
        difficult_level[chat_id] = Difficulty.BOT_EASY

    bot.send_message(chat_id=chat_id,
                     text=difficult_level[chat_id].value[1])


@bot.message_handler(content_types=['text'])
def reply(message):
    player1 = message.chat.id
    if player1 not in game_instances:
        bot.reply_to(message=message,
                     text='Ты куда звонишь сынок? Игру начни сначала.')
        return

    if player1 in opponents:
        player2 = opponents[player1]
        # здесь логика в случае игры двух людей
        if time_to_play[player1]:
            resp, done = game_instances[player1].step(message.text)
            if done == -1:
                bot.send_message(
                    chat_id=player1,
                    text=resp
                )
            elif done == 1:
                bot.send_message(
                    chat_id=player1,
                    text=resp
                )
                bot.send_message(
                    chat_id=player2,
                    text=resp
                )
                del game_instances[player1]
                del opponents[player2]
                del opponents[player1]
                del time_to_play[player1]
                del time_to_play[player2]
            else:
                bot.send_message(
                    chat_id=player2,
                    text=resp
                )
                time_to_play[player1] = False
                time_to_play[player2] = True
        else:
            bot.send_message(
                chat_id=player1,
                text='Ждем хода соперника. Посиди.'
            )
    else:
        # логика игры с ботом
        resp, done = game_instances[player1].step(message.text)
        bot.send_message(
            chat_id=player1,
            text=resp
        )
        if done:
            del game_instances[player1]


bot.infinity_polling()
