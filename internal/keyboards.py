from telebot import types

def get_keyboard_connecting(game):
    keyboard = types.InlineKeyboardMarkup()
    btn_disconnect = types.InlineKeyboardButton(text="Покинуть игру ❌", callback_data=f"game_disconnect_{game._id}")
    keyboard.add(btn_disconnect)
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
                text=f"{games[i]._id}: {games[i].count_gamers()}/{games[i].count_max_gamers()} игрок(ов)", 
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
    btn_game_type = types.InlineKeyboardButton(text=f"{game.type}", callback_data=f"game_type_{game._id}")
    btn_game_max_gamers = types.InlineKeyboardButton(text=f"Игроков: {game.count_max_gamers()}", callback_data=f"game_max_gamers_{game._id}")
    btn_game_delete = types.InlineKeyboardButton(text="Удалить 🚮", callback_data=f"game_delete_{game._id}")
    btn_game_status = types.InlineKeyboardButton(text="Начать игру", callback_data=f"game_start_{game._id}")

    keyboard = types.InlineKeyboardMarkup(row_width=3)
    keyboard.row(btn_game_type, btn_game_max_gamers)
    keyboard.row(btn_game_delete, btn_game_status)
    return keyboard