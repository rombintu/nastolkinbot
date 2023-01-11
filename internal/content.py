from datetime import datetime as dt
from random import choice
import os

commands = [
    "/start - Помощь",
    "/create - Создать игру",
    "/games - Список созданных игр"
]

messages = {
    "start" : "Настолкин \n" + "\n".join(commands)
}

# ERRORS
error = {
    "500": "Ошибка 500: `{description}`\n\nОбратитесь к администратору: @{admin}",
    "database": "База данных не отвечает",
    "no_data" : "Нет созданных игр\n/create - Создай сам!",
}

already_play = "Вы уже учавствуете в другой игре /info"
devtodo = "Изменение настройки пока что декоративное. В разработке."
game_not_found = "Этой игры: {}, уже не существует"
game_full_players = "Игра: {} заполнена"
game_to_play = "Игра: {} уже идет"
not_playing = "Вы не учавствуете в игре: {}\n/games"
game_join = "🎲 *Присоединиться*"

def get_last_update_format():
    return f"\n\t{dt.now().strftime('%d %B в %H:%M:%S')}"

def get_rand_question():
    return choice(questions)

types_game = [("Смех😁ёчки", "Пока недоделано, но кароче нужно просто подставлять смешные фразы или слова в пропуски, разберешься")]

def get_content(filename, packs=False):
    path = os.path.join(os.getcwd(), filename)
    if packs:
        path = os.path.join(os.getcwd(), "packs", filename)
    with open(path) as f: 
        return f.read().splitlines()

nicknames = get_content("nicknames.txt")
questions = get_content("default.txt", packs=True)