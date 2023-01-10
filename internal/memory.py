import shortuuid
from loguru import logger as log

type_game = [("Смех😁ёчки", "rules1")]
log.level("DEBUG")

class Player:
    def __init__(self, uuid, name):
        self.uuid = uuid
        self.score = 0
        self.game_id = None
        if not name:
            self.name = uuid
        else:
            self.name = name

class Game:
    def __init__(self, max_players=8, game_type=0):
        self.refresh_id()
        self.PLAYERS = {
            "players": [], 
            # "players_count": 0,
            "players_max": max_players,
            }
        self.type = game_type
        self.status = "Ждем ⏰"
        self.password = None
        self.timeround = None

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

    def get_password(self):
        if self.password == None: return "Нет"
        else: return self.password
    def update_password(self):
        self.password = shortuuid.ShortUUID().random(length=6) # TODO

    def get_timeround(self):
        return "ждем всех"
        # else: return self.timeround TODO
    
    def get_game_type(self): return type_game[self.type][0]
    def get_game_rule(self): return type_game[self.type][1]

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
        return "\n".join([f'{i+1}. {g.name} {g.score} смеху@чков' for i, g in enumerate(self.players)])

    def add_player(self, player):
        for g in self.PLAYERS["players"]:
            if g.uuid == player.uuid:
                return False
        player.game_id = self._id
        self.PLAYERS["players"].append(player)
        return True

    def del_player(self, player):
        for i, g in enumerate(self.get_players()):
            if g.uuid == player.uuid:
                g.game_id = None
                self.PLAYERS["players"].pop(i)
                return True
        return False

    
class Memory:
    def __init__(self):
        self.GAMES = {"games": [], "games_names": []}


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
                for pl in game.players:
                    pl.game_id = None
                self.GAMES["games"].pop(i)
                return game
        log.debug(f"(After delete) All Games: {self.get_games_names()}")
        return None

   