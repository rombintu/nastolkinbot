from telebot import types
from internal.content import types_game

def get_keyboard_connecting(game):
    keyboard = types.InlineKeyboardMarkup()
    btn_refresh = types.InlineKeyboardButton(text="Обновить 🔄", callback_data=f"game_refresh_{game._id}")
    btn_disconnect = types.InlineKeyboardButton(text="Покинуть игру ❌", callback_data=f"game_disconnect_{game._id}")
    keyboard.add(btn_refresh, btn_disconnect)
    return keyboard

def get_keyboard_games(games, start_i=0):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    btn_refresh = types.InlineKeyboardButton(text="🔄", callback_data=f"refresh_games")
    btn_next_r = types.InlineKeyboardButton(text="➡️", callback_data=f"game_{start_i+5}_>")
    btn_next_l = types.InlineKeyboardButton(text="⬅️", callback_data=f"game_{start_i-5}_>")
    for i in range(start_i, start_i + 5):
        if i == len(games): break
        keyboard.add(
            types.InlineKeyboardButton(
                text=f"{games[i]._id}: {games[i].get_players_count()}/{games[i].get_players_max()} игрок(ов)", 
                callback_data=f"game_connect_{games[i]._id}"))

    if start_i == 0 and start_i + 5 >= len(games):
        keyboard.add(btn_refresh)
    elif start_i + 5 >= len(games): 
        keyboard.add(btn_next_l, btn_refresh)
    elif start_i == 0: 
        keyboard.add(btn_refresh, btn_next_r)
    else: 
        keyboard.add(btn_next_l, btn_refresh, btn_next_r)
    return keyboard

def get_keyboard_game(game):
    btn_game_type = types.InlineKeyboardButton(text=f"{game.get_game_type()}", callback_data=f"game_type_{game._id}")
    btn_game_max_players = types.InlineKeyboardButton(text=f"Игроков: {game.get_players_max()}", callback_data=f"game_max_players_{game._id}")
    btn_game_pack = types.InlineKeyboardButton(text=f"Сборка: {game.get_pack_title()}", callback_data=f"game_pack_update_{game._id}")
    btn_game_password = types.InlineKeyboardButton(text=f"Пароль: {game.get_password()}", callback_data=f"game_password_update_{game._id}")
    btn_game_timeround = types.InlineKeyboardButton(text=f"Раунд: {game.get_timeround()}", callback_data=f"game_timeround_update_{game._id}")
    btn_game_delete = types.InlineKeyboardButton(text="Удалить 🚮", callback_data=f"game_delete_{game._id}")
    btn_game_start = types.InlineKeyboardButton(text="Начать игру", callback_data=f"game_start_{game._id}")

    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(btn_game_type, btn_game_max_players)
    keyboard.row(btn_game_pack)
    keyboard.row(btn_game_password, btn_game_timeround)
    keyboard.row(btn_game_delete, btn_game_start)
    return keyboard

def get_keyboard_round(game):
    keyboard = types.InlineKeyboardMarkup()
    for player in game.get_players():
        # if player.uuid == current_player: continue
        btn = types.InlineKeyboardButton(text=f"{player.answer}", callback_data=f"game_answer_{game._id}_{player.uuid}")
        keyboard.add(btn)
    # keyboard = types.ReplyKeyboardMarkup()
    # for pl in players:
    #     keyboard.add(pl.answer)
    return keyboard

def get_keyboard_packs_type_game():
    keyboard = types.ReplyKeyboardMarkup()
    for t in types_game:
        keyboard.add(t[0])
    return keyboard

def get_keyboard_packs(packs):
    keyboard = types.InlineKeyboardMarkup()
    for pack in packs:
        keyboard.add(
            types.InlineKeyboardButton(
                text=f"{pack.title}", 
                callback_data=f"pack_{pack.title}")
        )
    btn_refresh = types.InlineKeyboardButton(text="🔄", callback_data=f"packs_refresh")
    keyboard.add(btn_refresh)
    return keyboard

def get_keyboard_pack(pack):
    keyboard = types.InlineKeyboardMarkup()
    
    btn_download = types.InlineKeyboardButton(text="Получить файл", callback_data=f"pack_download_{pack.title}")
    btn_back = types.InlineKeyboardButton(text="↩️", callback_data=f"packs_refresh")
    btn_delete = types.InlineKeyboardButton(text="❌", callback_data=f"pack_delete_{pack.title}")
    keyboard.add(btn_download)
    keyboard.add(btn_delete, btn_back)
    return keyboard