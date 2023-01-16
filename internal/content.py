from datetime import datetime as dt
from random import choice
import os, json
from loguru import logger as log

log.level("DEBUG")
admin = "rombintu"
src_link = "https://github.com/rombintu/nastolkinbot"
commands = [
    "/create - Создать игру",
    "/games - Список созданных игр"
    "/info -Информация о текущей игре" 
]

messages = {
    "start" : f"""Присоединяйся к друзьями /games
Создавай игру /create и зови друзей 
Создай свой пак! /mypacks
    
    При поломке пиши @{admin}
    *Ваши данные нигде не хранятся, только сборки*"""
}

# ERRORS
error = {
    "500": "Ошибка 500: `{description}`\n\nОбратитесь к администратору: @{admin}",
    "database": "База данных не отвечает",
    "no_data" : "Нет созданных игр\n/create - Создай сам!",
}

already_play = "Вы уже учавствуете в другой игре /info"
devtodo = "Изменение настройки пока что декоративное. В разработке..."
game_not_found = "Этой игры: {}, уже не существует"
game_full_players = "Игра: {} заполнена"
game_to_play = "Игра: {} уже идет"
not_playing = "Вы не учавствуете в игре: {}\n/games"
game_join = "🎲 *Присоединиться*"
pack_help = "Ожидается, что файл будет состоять из вопросов, которые разделяются строчками"
pack_error = "Сборка [{}] неисправна, пересоздай ее /mypacks\n{}"
            

def get_last_update_format():
    return f"\n\t{dt.now().strftime('%d %B в %H:%M:%S')}"

def get_content(filename, packs=False):
    path = os.path.join(os.getcwd(), filename)
    if packs:
        path = os.path.join(os.getcwd(), "packs", filename)
    try:
        with open(path, "r") as f:
            return f.read().splitlines()
    except Exception as err:
        log.debug(err)
        return []
class Pack:
    def __init__(self, title, owner, game_type, filename, new=False):
        self.title = title
        self.owner = owner
        self.game_type = game_type
        self.filename = filename
        if new:
            self.questions = []
        else:
            self.questions = self.get_questions() 
        
    
    def get_questions(self):
        return get_content(self.filename, packs=True)

    def get_size(self):
        self.questions = self.get_questions() 
        return len(self.questions)

    def get_question(self, round):
        return self.questions[round]

    def get_rand_question(self):
        return choice(self.questions)

    def get_file(self):
        return open(os.path.join(os.getcwd(), "packs", self.filename), "rb")

    def delete(self):
        try:
            os.remove(os.path.join(os.getcwd(), "packs", self.filename))
        except Exception as err:
            log.debug(err)

def get_all_packs():
    packs = []
    with open(os.path.join(os.getcwd(), 'packs.json'), "r") as json_file:
        for pack in json.load(json_file):
            packs.append(Pack(
                pack["title"],
                pack["owner"],
                pack["game_type"],
                pack["filename"],
            ))
    return packs        

def update_pack_file(packs):
    js_data = []
    for pack in packs:
        js_data.append(
            {
                "title": pack.title,
                "game_type": pack.game_type,
                "owner": pack.owner,
                "filename": pack.filename,
            }
        )
    with open(os.path.join(os.getcwd(), 'packs.json'), "w") as json_file:
        json_file.write(json.dumps(js_data, indent=4))

def create_new_pack(packs, data):
    js_data = []
    for pack in packs:
        js_data.append(
            {
                "title": pack.title,
                "game_type": pack.game_type,
                "owner": pack.owner,
                "filename": pack.filename,
            }
        )
    with open(os.path.join(os.getcwd(), 'packs.json'), "w") as json_file:
        json_file.write(json.dumps(js_data, indent=4))
    with open(os.path.join(os.getcwd(), 'packs', pack.filename), "wb") as data_file:
        data_file.write(data)

types_game = [
    ["Смех😁ёчки", "Кароче нужно просто подставлять смешные фразы в пропуски, разберешься"]
]

def get_game_type(game_type_name):
    for i, t in  enumerate(types_game):
        if t[0] == game_type_name:
            return i
    return -1

nicknames = get_content("nicknames.txt")