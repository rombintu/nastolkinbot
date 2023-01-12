# local imports
import os
from loguru import logger as log

# external imports
import telebot
from telebot import types
from dotenv import load_dotenv

# internal imports
from internal import content, memory
from internal import keyboards as kb

load_dotenv()
log.level("DEBUG")
MARKDOWN = "markdown"

bot = telebot.TeleBot(os.getenv("BOT_TOKEN"), parse_mode=None)
# db = database.Database(os.getenv("DATABASE"))
admin = os.getenv("BOT_ADMIN", "NoName")
mem = memory.Memory()

def handle_error(err, too, description="unknown error"):
    log.error(err)
    bot.send_message(
        too, 
        content.error["500"].format(description, admin), 
        parse_mode=MARKDOWN
    )

def send_to_players(message, game, text, keyboard=None, get_input=False, end_round=False):
    if end_round:
        game.inc_round()
    log.debug(f"ANSWERS: {game.get_players_answers()}")
    for player in game.get_players():
        bot.send_message(player.uuid, text, reply_markup=keyboard, parse_mode=MARKDOWN)
        if get_input:
            message.chat.id = player.uuid
            message.from_user.id = player.uuid
            message.from_user.first_name = player.name
            if end_round:
                bot.register_next_step_handler(message, handle_end_round, player, game)
            else:
                bot.register_next_step_handler(message, handle_next_round, player, game)

def handle_next_round(message, player, game):
    player_answer = message.text
    if not player_answer or player_answer in game.get_players_answers() or len(player_answer) > 25:
        bot.send_message(player.uuid, "Ожидается небольшой текст или кто то тебя опередил 🤔\nПопробуй еще раз!")
        bot.register_next_step_handler(message, handle_next_round, player, game)
        return
    player.set_answer(player_answer)
    log.debug(f"{message.text} {player.answer}")
    if game.check_players_answers_by_None():
        send_to_players(message, game, 
            f"Голосуй за самый смешной ответ", 
            keyboard=kb.get_keyboard_round(game.get_players()), get_input=True, end_round=True)
    else:
        bot.send_message(player.uuid, "Отлично, ждем остальных!", reply_markup=types.ReplyKeyboardRemove())

def handle_end_round(message, player, game):
    player.add_score(game.get_players_answers().count(player.answer)) # TODO
    log.debug(f"PLAYER: {player.name} SCORE: {player.score}")
    
    player.clear_answer()
    log.debug(f"ANSWERS AFTER CLEAR: {game.get_players_answers()}")

    if game.end():
        bot.send_message(player.uuid, f"Игра закончена, расходимся!", reply_markup=types.ReplyKeyboardRemove())
        game.del_player(player)
        return
    # else:
    elif game.check_players_answers_by_empty():
        send_to_players(message, game,  
            f"Внимание, раунд {game.get_round()}/{game.round_max}: {content.get_rand_question()}", get_input=True)
    else:
        bot.send_message(player.uuid, "Отлично, ждем остальных!", reply_markup=types.ReplyKeyboardRemove())

# def handle_middleskip_round(message, player, game):
#     # bot.send_message(player.uuid, 
#     #     f"Внимание раунд {game.get_round()}/{game.round_max}: {content.get_rand_question()}")
#     bot.register_next_step_handler(message, handle_next_round, player, game)

@bot.message_handler(commands=['start', 'help'])
def handle_message_start(message):
    log.debug(str(mem))
    bot.send_message(
        message.chat.id, 
        content.messages["start"]
    )

@bot.message_handler(commands=['games'])
def handle_message_games(message):
    if not mem.get_games():
        bot.send_message(message.chat.id, content.error["no_data"])
        return
    bot.send_message(
        message.chat.id, 
        f"🎲 *Присоединиться*" + content.get_last_update_format(), 
        reply_markup=kb.get_keyboard_games(mem.get_games()),
        parse_mode=MARKDOWN
        )

@bot.callback_query_handler(func=lambda c: c.data)
def games_callback(c: types.CallbackQuery):
    data = c.data.split("_")
    match data:
        # REFRESH
        case ["refresh", "games"]:
            if not mem.get_games():
                bot.edit_message_text(
                    content.error["no_data"],
                    c.from_user.id, c.message.id,
                    reply_markup=kb.get_keyboard_games(mem.get_games()), parse_mode=MARKDOWN
                )
            else:
                bot.edit_message_text(content.game_join + content.get_last_update_format(),
                    c.from_user.id, c.message.id, 
                    reply_markup=kb.get_keyboard_games(mem.get_games()), parse_mode=MARKDOWN)
        
        case ["game", _, ">"]:
            start_i = int(data[1])
            if start_i <= 0: start_i = 0
            bot.edit_message_text(content.game_join,
                c.from_user.id, c.message.id, 
                reply_markup=kb.get_keyboard_games(mem.get_games()), parse_mode=MARKDOWN)

        case ["game", "type", _]:
            # TODO DLC
            game_id = data[-1]
            game = mem.get_game_by_id(game_id)
            if not game:
                bot.send_message(c.message.chat.id, content.game_not_found.format(game_id))
                return
            bot.send_message(
                c.message.chat.id, 
                content.devtodo
            )
        case ["game", "refresh", _]:
            game_id = data[-1]
            game = mem.get_game_by_id(game_id)
            if not game:
                bot.send_message(c.message.chat.id, content.game_not_found.format(game_id))
                return
            bot.edit_message_text(
                game.info(),
                c.from_user.id, c.message.id, 
                reply_markup=kb.get_keyboard_connecting(game)
            )
            
        case ["game", "max", "players", _]:
            game_id = data[-1]
            game = mem.get_game_by_id(game_id)
            if not game:
                bot.send_message(c.message.chat.id, content.game_not_found.format(game_id))
                return
            game.inc_players_max()
            bot.edit_message_text(f"Игра: *{game._id}*",
                c.from_user.id, c.message.id, 
                reply_markup=kb.get_keyboard_game(game), parse_mode=MARKDOWN)

        case ["game", "password", "update", _]:
            game_id = data[-1]
            game = mem.get_game_by_id(game_id)
            if not game:
                bot.send_message(c.message.chat.id, content.game_not_found.format(game_id))
                return
            game.update_password()
            bot.send_message(c.message.chat.id, content.devtodo)
            bot.edit_message_text(f"Игра: *{game._id}*",
                c.from_user.id, c.message.id, 
                reply_markup=kb.get_keyboard_game(game), parse_mode=MARKDOWN)
        
        case ["game", "connect", _]:            
            game_id = data[-1]
            game = mem.get_game_by_id(game_id)
            if not game:
                bot.send_message(c.message.chat.id, content.game_not_found.format(game_id))
                return
            elif game.get_players_count() >= game.get_players_max():
                bot.send_message(c.message.chat.id, content.game_full_players.format(game_id))
                return
            elif game.status == "Идет игра ✅":
                bot.send_message(c.message.chat.id, content.game_to_play.format(game_id))
                return
            elif game.get_password():
                # TODO
                pass
            player = mem.try_get_player_by_uuid(c.message.chat.id, c.message.chat.first_name)
            
            if not game.add_player(player):
                bot.send_message(player.uuid, content.already_play)
                return
            for pl in game.get_players():
                if pl.uuid == player.uuid: continue
                bot.send_message(pl.uuid, f"Присоединился игрок: {c.message.chat.first_name}")
            bot.send_message(c.message.chat.id, game.info(), reply_markup=kb.get_keyboard_connecting(game))

        case ["game", "disconnect", _]:
            game_id = data[-1]
            game = mem.get_game_by_id(game_id)
            if not game:
                bot.send_message(c.message.chat.id, content.game_not_found.format(game_id))
                return

            player = mem.try_get_player_by_uuid(c.message.chat.id, c.message.chat.first_name)
            if not game.del_player(player):
                bot.send_message(player.uuid, content.not_playing.format(game._id))
                return
            for g in game.get_players():
                if g.uuid == player.uuid: continue
                bot.send_message(g.uuid, f"Отключился игрок: {c.message.chat.first_name}")
            bot.send_message(c.message.chat.id, f"Вы покинули игру: {game._id}")
            bot.delete_message(c.message.chat.id, c.message.message_id)
        case ["game", "delete", _]:
            game_id = data[-1]
            game = mem.get_game_by_id(game_id)
            if not game:
                bot.send_message(c.message.chat.id, content.game_not_found.format(game_id))
                return
            game = mem.delete_game_by_id(game_id)
            for g in game.get_players():
                bot.send_message(g.uuid, f"Игра: {game._id} была удалена 😵")
            bot.delete_message(c.message.chat.id, c.message.message_id)

        case ["game", "start", _]:
            game_id = data[-1]
            game = mem.get_game_by_id(game_id)
            if not game:
                bot.send_message(c.message.chat.id, content.game_not_found.format(game_id))
                return
            elif game.get_players_count() < 2:
                bot.send_message(c.message.chat.id, "Чтобы начать игру требуется минимум 2 игрока")
                return
            game.change_status()
            send_to_players(c.message, game, f"Итак, начнем игру\nСегодня с нами играют:\n{game.get_table_players()}")
            send_to_players(c.message, game, f"Правила игры: {game.get_game_rule()}")
            send_to_players(c.message, game, 
                f"Внимание, раунд {game.get_round()}/{game.round_max}: {content.get_rand_question()}",
                get_input=True)
            
    return

@bot.message_handler(commands=['create'])
def handle_message_create(message):
    player = mem.try_get_player_by_uuid(message.from_user.id, message.from_user.first_name)
    if player.game_id:
        bot.send_message(player.uuid, content.already_play)
        return
    game = memory.Game()
    game.add_player(player)
    mem.new_game(game)
    bot.send_message(
        message.chat.id, 
        f"Игра: *{game._id}*",
        reply_markup=kb.get_keyboard_game(game), parse_mode=MARKDOWN
    )

@bot.message_handler(commands=['info'])
def handle_message_create(message):
    player = mem.try_get_player_by_uuid(message.from_user.id, message.from_user.first_name)
    info = "Вы не учавствуете в играх\n/games - Список"
    if player.game_id:
        game = mem.get_game_by_id(player.game_id)
        if not game:
            bot.send_message(message.chat.id, content.game_not_found.format(player.game_id))
            return
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