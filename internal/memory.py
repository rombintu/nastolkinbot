import shortuuid

type_game = ["Смех😁ёчки"]

class Gamer:
    def __init__(self, uuid, name):
        self.uuid = uuid
        self.score = 0
        self.game_id = None
        if not name:
            self.name = uuid
        else:
            self.name = name

class Game:
    def __init__(self, gamers=[], max_gamers=8, type=0):
        self.refresh_id()
        self.gamers = gamers
        self.max_gamers = max_gamers
        self.type = type_game[type]
        self.status = "Ждем ⏰"

    def refresh_id(self):
        self._id = shortuuid.ShortUUID(alphabet="ABCDEFGHJKLMNPQRSTUVWXYZ").random(length=6)

    def count_gamers(self):
        return len(self.gamers)

    def count_max_gamers(self):
        return self.max_gamers

    def change_status(self, status="Идет игра ✅"):
        self.status = status
    
    def i_max_gamers(self):
        max_gamers = (self.max_gamers + 2) % 9
        if max_gamers == 1:
            self.max_gamers = 2
        else:
            self.max_gamers = max_gamers
    
    def get_table_players(self):
        return "\n".join([f'{i+1}. {g.name} {g.score}' for i, g in enumerate(self.gamers)])

    def add_gamer(self, gamer):
        for g in self.gamers:
            if g.uuid == gamer.uuid:
                return False
        gamer.game_id = self._id
        self.gamers.append(gamer)
        return True

    def del_gamer(self, gamer):
        for i, g in enumerate(self.gamers):
            if g.uuid == gamer.uuid:
                g.game_id = None
                self.gamers.pop(i)
                return True
        return False

    def info(self):
        buff = f"Игра: {self._id} 🎮\n"
        buff += f"Тип: {self.type}\n"
        buff += f"Игроки: {self.count_gamers()}/{self.max_gamers}\n"
        buff += f"Статус: {self.status}"
        return buff
    
class Memory:
    def __init__(self):
        self.games = []

    def try_get_gemer_by_uuid(self, uuid, name):
        for game in self.games:
            for g in game.gamers:
                if g.uuid == uuid:
                    return g
        return Gamer(uuid, name)

    def new_game(self, game):
        for g in self.games:
            if g._id == game._id:
                game.refresh_id()
                self.new_game(game)
        self.games.append(game)

    def get_game_by_id(self, _id):
        for g in self.games:
            if g._id == _id:
                return g
        return None

    def delete_game_by_id(self, _id):
        for i, g in enumerate(self.games):
            if g._id == _id:
                self.games.pop(i)
                return g
        return None

    def get_games(self):
        for i, game in enumerate(self.games):
            if len(game.gamers) == 0:
                self.games.pop(i)
        return self.games