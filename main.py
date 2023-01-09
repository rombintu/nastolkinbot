# local imports
import os
import logging

# external imports
import telebot
from telebot import types
from dotenv import load_dotenv

# internal imports
from internal import content, memory
from internal import keyboards as kb

load_dotenv()

bot = telebot.TeleBot(os.getenv("BOT_TOKEN"), parse_mode=None)
# db = database.Database(os.getenv("DATABASE"))
admin = os.getenv("BOT_ADMIN", "NoName")
mem = memory.Memory()

def handle_error(err, too, description="unknown error"):
    logging.error(err)
    bot.send_message(
        too, 
        content.error["500"].format(description, admin), 
        parse_mode="markdown"
    )

@bot.message_handler(commands=['start', 'help'])
def handle_message_start(message):
    bot.send_message(
        message.chat.id, 
        content.messages["start"]
    )

@bot.message_handler(commands=['games'])
def handle_message_games(message):
    if not mem.games:
        bot.send_message(message.chat.id, content.error["no_data"])
        return
    bot.send_message(
        message.chat.id, 
        f"🎲 *Присоединиться*" + content.get_last_update_format(), 
        reply_markup=kb.get_keyboard_games(mem.get_games()),
        parse_mode="markdown"
        )

@bot.callback_query_handler(func=lambda c: c.data)
def games_callback(c: types.CallbackQuery):
    data = c.data.split("_")
    match data:
        # REFRESH
        case ["refresh", "games"]:
            if not mem.games:
                bot.edit_message_text(
                    content.error["no_data"],
                    c.from_user.id, c.message.id,
                    reply_markup=kb.get_keyboard_games(mem.get_games()), parse_mode="markdown"
                )
            else:
                bot.edit_message_text(f"🎲 *Присоединиться*" + content.get_last_update_format(),
                    c.from_user.id, c.message.id, 
                    reply_markup=kb.get_keyboard_games(mem.get_games()), parse_mode="markdown")
        
        case ["game", _, ">"]:
            start_i = int(data[1])
            if start_i <= 0: start_i = 0
            bot.edit_message_text(f"🎲 *Присоединиться*",
                c.from_user.id, c.message.id, 
                reply_markup=kb.get_keyboard_games(mem.get_games()), parse_mode="markdown")

        case ["game", "type", _]:
            # TODO DLC
            bot.send_message(
                c.message.chat.id, 
                "Доступен только один тип игры, в разработке..."
            )
        case ["game", "max", "gamers", _]:
            game_id = data[-1]
            game = mem.get_game_by_id(game_id)
            if not game:
                bot.send_message(
                    c.message.chat.id, 
                    f"Этой игры: {game_id}, уже не существует"
                )
                return
            game.i_max_gamers()
            bot.edit_message_text(f"Игра: *{game._id}*",
                c.from_user.id, c.message.id, 
                reply_markup=kb.get_keyboard_game(game), parse_mode="markdown")

        case ["game", "connect", _]:            
            game_id = data[-1]
            game = mem.get_game_by_id(game_id)
            if not game:
                bot.send_message(c.message.chat.id, f"Этой игры: {game_id}, уже не существует")
                return
            elif game.count_gamers() >= game.count_max_gamers():
                bot.send_message(c.message.chat.id, f"Игра: {game_id} заполнена")
                return
            elif game.status == "Идет игра ✅":
                bot.send_message(c.message.chat.id, f"Игра: {game_id} уже идет")
                return
            gamer = mem.try_get_gemer_by_uuid(c.message.chat.id, c.message.chat.first_name)
            
            if not game.add_gamer(gamer):
                bot.send_message(gamer.uuid, f"Вы уже учавствуете в другой игре /info")
                return
            for g in game.gamers:
                if g.uuid == gamer.uuid: continue
                bot.send_message(g.uuid, f"Присоединился игрок: {c.message.chat.first_name}")
            bot.send_message(c.message.chat.id, game.info(), reply_markup=kb.get_keyboard_connecting(game))

        case ["game", "disconnect", _]:
            game_id = data[-1]
            game = mem.get_game_by_id(game_id)
            if not game:
                bot.send_message(c.message.chat.id, f"Этой игры: {game_id}, уже не существует")
                return

            gamer = mem.try_get_gemer_by_uuid(c.message.chat.id, c.message.chat.first_name)
            if not game.del_gamer(gamer):
                bot.send_message(gamer.uuid, f"Вы не учавствуете в игре: {game._id}\n/games")
                return
            for g in game.gamers:
                if g.uuid == gamer.uuid: continue
                bot.send_message(g.uuid, f"Отключился игрок: {c.message.chat.first_name}")
            bot.send_message(c.message.chat.id, f"Вы покинули игру: {game._id}")
            bot.delete_message(c.message.chat.id, c.message.message_id)
        case ["game", "delete", _]:
            game_id = data[-1]
            game = mem.delete_game_by_id(game_id)
            for g in game.gamers:
                bot.send_message(g.uuid, f"Игра: {game._id} была удалена 😵")
            bot.delete_message(c.message.chat.id, c.message.message_id)
        case ["game", "start", _]:
            game_id = data[-1]
            game = mem.delete_game_by_id(game_id)
            if not game:
                bot.send_message(c.message.chat.id, f"Этой игры: {game_id}, уже не существует")
                return
            elif game.count_gamers() < 2:
                bot.send_message(c.message.chat.id, f"Требуется минимум 2 игрока")
                return
            game.change_status()
            for g in game.gamers:
                bot.send_message(g.uuid, f"Итак, начнем игру\nСегодня с нами играют:\n{game.get_table_players()}")
    return

@bot.message_handler(commands=['create'])
def handle_message_create(message):
    gamer = mem.try_get_gemer_by_uuid(message.from_user.id, message.from_user.first_name)
    game = memory.Game()
    game.add_gamer(gamer)
    mem.new_game(game)
    bot.send_message(
        message.chat.id, 
        f"Игра: *{game._id}*",
        reply_markup=kb.get_keyboard_game(game), parse_mode="markdown"
    )

@bot.message_handler(commands=['info'])
def handle_message_create(message):
    gamer = mem.try_get_gemer_by_uuid(message.from_user.id, message.from_user.first_name)
    info = "Вы не учавствуете в играх\n/games - Список"
    if gamer.game_id:
        game = mem.get_game_by_id(gamer.game_id)
        bot.send_message(
            message.chat.id, 
            game.info(),
            reply_markup=kb.get_keyboard_connecting(game)
        )
    else:
        bot.send_message(
            message.chat.id, 
            info,
        )

@bot.message_handler(content_types=['text'])
def handle_message_text(message):
    bot.send_message(
        message.chat.id, 
        content.messages["start"]
    )

def main():
    print("Service status: OK")
    bot.polling(none_stop=True, timeout=60)

if __name__ == "__main__":
    main()