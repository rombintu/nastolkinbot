import shortuuid
from loguru import logger as log
from internal.content import types_game, nicknames, get_all_packs
from random import choice

log.level("DEBUG")

class Player:
    def __init__(self, uuid, name):
        self.uuid = uuid
        self.game_id = None
        if not name:
            self.name = uuid
        else:
            self.name = name
        self.game = {
            "answer": None, 
            "score": 0
            }
        self.nick = choice(nicknames)
        self.packs = []
    
    @property
    def answer(self):
        return self.game["answer"]
    @property
    def score(self):
        return self.game["score"]

    def set_answer(self, new_answer):
        self.game["answer"] = new_answer

    def clear_answer(self):
        self.set_answer(None)    

    def add_score(self, score):
        self.game["score"] = self.game["score"] + score

    def end_game(self):
        self.game_id = None
        self.game["score"] = 0

    def get_packs(self):
        pass

class Game:
    def __init__(self, pack, max_players=8, game_type=0, round_max=12):
        self.refresh_id()
        self.PLAYERS = {
            "players": [], 
            "players_max": max_players,
            }
        self.type = game_type
        self.status = "Ждем ⏰"
        self.password = None # TODO
        self.timeround = None # TODO
        self.pack = pack
        self.round = 1
        self.round_max = round_max

    def info(self):
        buff = f"Игра: {self._id} 🎮\n"
        buff += f"Тип: {self.get_game_type()}\n"
        buff += f"Игроки: {self.get_players_count()}/{self.get_players_max()}\n"
        buff += f"Пароль: {self.get_password()}\n"
        buff += f"Раунд: {self.get_timeround()}\n"
        buff += f"Статус: {self.status}"
        return buff

    def get_players(self):
        return self.PLAYERS["players"]

    def get_players_count(self):
        return len(self.PLAYERS["players"])
    
    def get_players_max(self):
        return self.PLAYERS["players_max"]

    def get_players_answers(self):
        return [player.answer for player in self.PLAYERS["players"]]

    def get_pack_title(self):
        return self.pack.title.title()

    def check_players_answers_by_None(self):
        if None in self.get_players_answers():
            return False
        return True
    
    def check_players_answers_by_empty(self):
        if self.get_players_answers().count(None) == len(self.get_players_answers()):
            return True 
        return False

    def get_round(self):
        return self.round

    def inc_round(self):
        self.round = self.round + 1

    def end(self):
        return self.round > self.round_max

    def get_password(self):
        if self.password == None: return "Нет"
        else: return self.password

    def update_password(self):
        self.password = shortuuid.ShortUUID().random(length=6) # TODO

    def get_timeround(self):
        return "ждем всех"
        # else: return self.timeround TODO
    
    def get_game_type(self): return types_game[self.pack.game_type][0]
    def get_game_rule(self): return types_game[self.pack.game_type][1]

    def refresh_id(self):
        self._id = shortuuid.ShortUUID(
            alphabet="ABCDEFGHJKLMNPQRSTUVWXYZ").random(length=6)

    def change_status(self, new_status="Идет игра ✅"):
        self.status = new_status
    
    def inc_players_max(self):
        max_players = (self.PLAYERS["players_max"] + 2) % 9
        if max_players == 1:
            self.PLAYERS["players_max"] = 2
        else:
            self.PLAYERS["players_max"] = max_players
    
    def get_table_players(self):
        return "\n".join([f'{i+1}. {pl.name} *{pl.nick.title()}*' \
            for i, pl in enumerate(self.PLAYERS["players"])])

    def add_player(self, player):
        for pl in self.PLAYERS["players"]:
            if pl.uuid == player.uuid:
                return False
        player.game_id = self._id
        self.PLAYERS["players"].append(player)
        return True

    def del_player(self, player):
        for i, pl in enumerate(self.get_players()):
            if pl.uuid == player.uuid:
                pl.end_game()
                self.PLAYERS["players"].pop(i)
                return True
        return False
    
    
class Memory:
    def __init__(self):
        self.GAMES = {"games": [], "games_names": []}
        self.packs = get_all_packs()

    def __str__(self) -> str:
        string = ""
        for game in self.get_games():
            string += f"{game._id}: {len(game.get_players())}" 
        return string 

    def get_games(self):
        for i, game in enumerate(self.GAMES["games"]):
            if len(game.get_players()) == 0:
                self.GAMES["games"].pop(i)
        return self.GAMES["games"]

    def get_games_names(self):
        return ', '.join(game._id for game in self.GAMES["games"])

    def try_get_player_by_uuid(self, uuid, name):
        for game in self.GAMES["games"]:
            for i, g in enumerate(game.get_players()):
                if g.uuid == uuid:
                    log.debug(f"Found player: {game.get_players()[i].name}")
                    return game.get_players()[i]
        return Player(uuid, name)

    def new_game(self, game):
        for g in self.GAMES["games"]:
            if g._id == game._id:
                game.refresh_id()
                self.new_game(game)
        self.GAMES["games"].append(game)
        log.debug(f"Create new Game: {game._id}")
        log.debug(f"All Games: {self.get_games_names()}")

    def get_game_by_id(self, _id):
        for game in self.GAMES["games"]:
            if game._id == _id:
                log.debug(f"Found game: {game._id}")
                return game
        log.debug(f"All Games: {self.get_games_names()}")
        return None

    def delete_game_by_id(self, _id):
        for i, game in enumerate(self.GAMES["games"]):
            if game._id == _id:
                for pl in game.get_players():
                    pl.game_id = None
                self.GAMES["games"].pop(i)
                return game
        log.debug(f"(After delete) All Games: {self.get_games_names()}")
        return None
    
    def refresh_packs(self):
        self.packs = get_all_packs()

    def add_pack(self, pack):
        self.packs.append(pack)

    def check_pack_exists(self, pack_name):
        for pack in self.packs:
            if pack.title == pack_name:
                return True
        return False

    def get_packs_by_uuid(self, uuid):
        packs = []
        for pack in self.packs:
            if pack.owner == uuid:
                packs.append(pack)
        return packs