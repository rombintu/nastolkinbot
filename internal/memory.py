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
    def __init__(self, players=[], max_players=8, game_type=0):
        self.refresh_id()
        self.players = players
        self.max_players = max_players
        self.type = game_type
        self.status = "Ждем ⏰"
        self.password = None
        self.timeround = None

    def info(self):
        buff = f"Игра: {self._id} 🎮\n"
        buff += f"Тип: {self.get_game_type()}\n"
        buff += f"Игроки: {self.count_players()}/{self.max_players}\n"
        buff += f"Пароль: {self.get_password()}\n"
        buff += f"Раунд: {self.get_timeround()}\n"
        buff += f"Статус: {self.status}"
        return buff

    def get_password(self):
        if self.password == None: return "Нет"
        else: return self.password
    def update_password(self):
        self.password = shortuuid.ShortUUID().random(length=6) # TODO

    def get_timeround(self):
        return "пока не ответят все"
        # else: return self.timeround TODO
    
    def get_game_type(self): return type_game[self.type][0]
    def get_game_rule(self): return type_game[self.type][1]

    def refresh_id(self):
        self._id = shortuuid.ShortUUID(
            alphabet="ABCDEFGHJKLMNPQRSTUVWXYZ").random(length=6)

    def count_players(self):
        return len(self.players)

    def count_max_players(self):
        return self.max_players

    def change_status(self, new_status="Идет игра ✅"):
        self.status = new_status
    
    def i_max_players(self):
        max_players = (self.max_players + 2) % 9
        if max_players == 1:
            self.max_players = 2
        else:
            self.max_players = max_players
    
    def get_table_players(self):
        return "\n".join([f'{i+1}. {g.name} {g.score} смеху@чков' for i, g in enumerate(self.players)])

    def add_player(self, player):
        for g in self.players:
            if g.uuid == player.uuid:
                return False
        player.game_id = self._id
        self.players.append(player)
        return True

    def del_player(self, player):
        for i, g in enumerate(self.players):
            if g.uuid == player.uuid:
                g.game_id = None
                self.players.pop(i)
                return True
        return False

    
class Memory:
    def __init__(self):
        self.games = []

    def try_get_player_by_uuid(self, uuid, name):
        for game in self.games:
            for i, g in enumerate(game.players):
                if g.uuid == uuid:
                    log.debug(f"Found player: {game.players[i].name}")
                    return game.players[i]
        return Player(uuid, name)

    def new_game(self, game):
        for g in self.games:
            if g._id == game._id:
                game.refresh_id()
                self.new_game(game)
        self.games.append(game)
        log.debug(f"Create new Game: {game._id}")
        log.debug(f"All Games: {', '.join(game._id for game in self.get_games())}")

    def get_game_by_id(self, _id):
        for g in self.games:
            if g._id == _id:
                log.debug(f"Found game: {g._id}")
                return g
        log.debug(f"All Games: {', '.join(game._id for game in self.get_games())}")
        return None

    def delete_game_by_id(self, _id):
        for i, g in enumerate(self.games):
            if g._id == _id:
                for pl in g.players:
                    pl.game_id = None
                self.games.pop(i)
                return g
        log.debug(f"(After delete) All Games: {', '.join(game._id for game in self.get_games())}")
        return None

    def get_games(self):
        for i, game in enumerate(self.games):
            if len(game.players) == 0:
                self.games.pop(i)
        return self.games